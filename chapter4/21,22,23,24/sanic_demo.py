# Example 4-23. API server with Sanic
import argparse
from sanic import Sanic
from sanic.views import HTTPMethodView
from sanic.response import json
# The Database utility helper, as described earlier. This will provide the
# methods required to connect to the database.
from util import Database
# Two more tools I’ve cobbled together to log the elapsed time of each API
# endpoint. I used this in the previous discussion to detect when a GET was
# being returned from the cache. The implementations for aelapsed() and
# aprofiler() are not important for this case study, but you can obtain them
# in Example B-1.
from perf import aelapsed, aprofiler
import model

# We create the main Sanic app instance.
app = Sanic()


# This coroutine function is for creating new patron entries. In an
# add_route() call toward the bottom of the code, new_patron() is associated
# with the endpoint /patron , only for the POST HTTP method. The @aelapsed
# decorator is not part of the Sanic API: it’s my own invention, merely to log
# out timings for each call.
@aelapsed
async def new_patron(request):
    # Sanic provides immediate deserialization of received JSON data by using
    # the .json attribute on the request object.
    data = request.json
    # The model module, which I imported, is the model for our patron table in
    # the database. I’ll go through that in more detail in the next code
    # listing; for now, just understand that all the database queries and SQL
    # are in this model module. Here I’m passing the connection pool for the
    # database, and the same pattern is used for all the interaction with the
    # database model in this function and in the PatronAPI class further down.
    id = await model.add_patron(app.pool, data)
    # A new primary key, id , will be created, and this is returned back to
    # the caller as JSON.
    return json(dict(msg='ok', id=id))


# While creation is handled in the new_patron() function, all other
# interactions are handled in this class-based view, which is a convenience
# provided by Sanic. All the methods in this class are associated with the
# same URL, /patron/<id:int>, which you can see in the add_route() function
# near the bottom. Note that the id URL parameter will be passed to each of
# the methods, and this parameter is required for all three endpoints.
# You can safely ignore the metaclass argument: all it does is wrap each
# method with the @aelapsed decorator so that timings will be printed in the
# logs. Again, this is not part of the Sanic API; it’s my own invention for
# logging timing data.
class PatronAPI(HTTPMethodView, metaclass=aprofiler):
    async def get(self, request, id):
        # As before, model interaction is performed inside the model module.
        data = await model.get_patron(app.pool, id)
        return json(data)

    async def put(self, request, id):
        data = request.json
        ok = await model.update_patron(app.pool, id, data)
        # If the model reports failure for doing the update, I modify the
        # response data. I’ve included this for readers who have not yet seen
        # Python’s version of the ternary operator.
        return json(dict(msg='ok' if ok else 'bad'))

    async def delete(self, request, id):
        ok = await model.delete_patron(app.pool, id)
        return json(dict(msg='ok' if ok else 'bad'))


# The @app.listener decorators are hooks provided by Sanic to give you a place
# to add extra actions during the startup and shutdown sequence. This one,
# before_server_start, is invoked before the API server is started up. This
# seems like a good place to initialize our database connection.
@app.listener('before_server_start')
async def db_connect(app, loop):
    # Use the Database helper to create a connection to our PostgreSQL
    # instance. The DB we’re connecting to is test.
    app.db = Database('test', owner=False)
    # Obtain a connection pool to our database.
    app.pool = await app.db.connect()
    # Use our model (for the patron table) to create the table if it’s missing.
    await model.create_table_if_missing(app.pool)
    # Use our model to create a dedicated_listener for database events,
    # listening on the channel chan_patron. The callback function for these
    # events is model.db_event(), which I’ll go through in the next listing.
    # The callback will be called every time the database updates the channel.
    await app.db.add_listener('chan_patron', model.db_event)


# after_server_stop is the hook for tasks that must happen during shutdown.
# Here we disconnect from the database.
@app.listener('after_server_stop')
async def db_disconnect(app, loop):
    await app.db.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    # This add_route() call sends POST requests for the /patron URL to the
    # new_patron() coroutine function.
    app.add_route(
        new_patron, '/patron', methods=['POST'])
    # This add_route() call sends all requests for the /patron/<id:int> URL to
    # the PatronAPI class-based view. The method names in that class determine
    # which one is called: a GET HTTP request will call the PatronAPI.get()
    # method, and so on.
    app.add_route(
        PatronAPI.as_view(), '/patron/<id:int>')
    app.run(host="0.0.0.0", port=args.port)
