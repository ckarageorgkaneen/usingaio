# Example 4-24. DB model for the “patron” table
import logging
from json import loads, dumps
# You have to add triggers to the database in order to get notifications when
# data changes. I’ve created these handy helpers to create the trigger
# function itself (with create_notify_trigger) and to add the trigger to a
# specific table (with add_table_triggers). The SQL required to do this is
# somewhat out of scope for this book, but it’s still crucial to understanding
# how this case study works.
from triggers import (
    create_notify_trigger, add_table_triggers)
# The third-party boltons package provides a bunch of useful tools, not the
# least of which is the LRU cache, a more versatile option than the @lru_cache
# decorator in the functools standard library module.
from boltons.cacheutils import LRU

logger = logging.getLogger('perf')

# This block of text holds all the SQL for the standard CRUD operations. Note
# that I’m using native PostgreSQL syntax for the parameters: $1, $2, and so
# on. There is nothing novel here, and it won’t be discussed further.
CREATE_TABLE = ('CREATE TABLE IF NOT EXISTS patron('
                'id serial PRIMARY KEY, name text, '
                'fav_dish text)')
INSERT = ('INSERT INTO patron(name, fav_dish) '
          'VALUES ($1, $2) RETURNING id')
SELECT = 'SELECT * FROM patron WHERE id = $1'
UPDATE = 'UPDATE patron SET name=$1, fav_dish=$2 WHERE id=$3'
DELETE = 'DELETE FROM patron WHERE id=$1'
EXISTS = "SELECT to_regclass('patron')"

# Create the cache for this app instance.
CACHE = LRU(max_size=65536)


# I called this function from the Sanic module inside the new_patron()
# endpoint for adding new patrons. Inside the function, I use the fetchval()
# method to insert new data. Why fetchval() and not execute()? Because
# fetchval() returns the primary key of the new inserted record!
async def add_patron(conn, data: dict) -> int:
    return await conn.fetchval(
        INSERT, data['name'], data['fav_dish'])


async def update_patron(conn, id: int, data: dict) -> bool:
    # Update an existing record. When this succeeds, PostgreSQL will return
    # UPDATE 1, so I use that as a check to verify that the update succeeded.
    result = await conn.execute(
        UPDATE, data['name'], data['fav_dish'], id)
    return result == 'UPDATE 1'


# Deletion is very similar to updating.
async def delete_patron(conn, id: int):
    result = await conn.execute(DELETE, id)
    return result == 'DELETE 1'


# This is the read operation. This is the only part of our CRUD interface that
# cares about the cache. Think about that for a second: we don’t update the
# cache when doing an insert, update, or delete. This is because we rely on
# the async notification from the database (via the installed triggers) to
# update the cache if any data is changed.
async def get_patron(conn, id: int) -> dict:
    if id not in CACHE:
        logger.info(f'id={id} Cache miss')
        # Of course, we do still want to use the cache after the first GET.
        record = await conn.fetchrow(SELECT, id)
        CACHE[id] = record and dict(record.items())
    return CACHE[id]


# The db_event() function is the callback that asyncpg will make when there are
# events on our DB notification channel, chan_patron. This specific parameter
# list is required by asyncpg. conn is the connection on which the event was
# sent, pid is the process ID of the PostgreSQL instance that sent the event,
# channel is the name of the channel (which in this case will be chan_patron),
# and the payload is the data being sent on the channel.
def db_event(conn, pid, channel, payload):
    # Deserialize the JSON data to a dict.
    event = loads(payload)
    logger.info('Got DB event:\n' + dumps(event, indent=4))
    id = event['id']
    if event['type'] == 'INSERT':
        CACHE[id] = event['data']
    elif event['type'] == 'UPDATE':
        # The cache population is generally quite straightforward, but note
        # that update events contain both new and old data, so we need to make
        # sure to cache the new data only.
        CACHE[id] = event['data']['new']
    elif event['type'] == 'DELETE':
        CACHE[id] = None


# This is a small utility function I’ve made to easily re-create a table if
# it’s missing. This is really useful if you need to do this frequently—such
# as when writing the code samples for this book!
# This is also where the database notification triggers are created and added
# to our patron table.
async def create_table_if_missing(conn):
    if not await conn.fetchval(EXISTS):
        await conn.fetchval(CREATE_TABLE)
        await create_notify_trigger(
            conn, channel='chan_patron')
        await add_table_triggers(
            conn, table='patron')
