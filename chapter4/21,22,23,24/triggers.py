# Example B-4. triggers.py

# These functions require asyncpg , although this import is used only to allow
# Connection to be used in type annotations.
from asyncpg.connection import Connection


# The create_notify_trigger() coroutine function will create the trigger
# function itself in the database. The trigger function will contain the name
# of the channel that updates will be sent to. The code for the function
# itself is in the SQL_CREATE_TRIGGER identifier, and it is set up as a format
# string.
async def create_notify_trigger(
        conn: Connection,
        trigger_name: str = 'table_update_notify',
        channel: str = 'table_change') -> None:
    # Recall from the case study example that update notifications included a
    # “diff” section in which the difference between old and new data was
    # shown. We use the hstore feature of PostgreSQL to calculate that diff.
    # It provides something close to the semantics of sets. The hstore
    # extension is not enabled by default, so we enable it here.
    await conn.execute(
        'CREATE EXTENSION IF NOT EXISTS hstore')
    # The desired trigger name and channel are substituted into the template
    # and then executed.
    await conn.execute(
        SQL_CREATE_TRIGGER.format(
            trigger_name=trigger_name,
            channel=channel))


# The second function, add_table_triggers() , connects the trigger function to
# table events like insert, update, and delete.
async def add_table_triggers(
        conn: Connection,
        table: str,
        trigger_name: str = 'table_update_notify',
        schema: str = 'public') -> None:
    # There are three format strings for each of the three methods.
    templates = (SQL_TABLE_INSERT, SQL_TABLE_UPDATE,
                 SQL_TABLE_DELETE)
    for template in templates:
        # The desired variables are substituted into the templates and then
        # executed.
        await conn.execute(
            template.format(
                table=table,
                trigger_name=trigger_name,
                schema=schema))

# This SQL code took me a lot longer than expected to get exactly right! This
# PostgreSQL procedure is called for insert, update, and delete events; the
# way to know which is to check the TG_OP variable. If the operation is
# INSERT, then NEW will be defined (and OLD will not be defined). For DELETE,
# OLD will be defined but not NEW . For UPDATE , both are defined, which
# allows us to calculate the diff. We also make use of PostgreSQL’s built-in
# support for JSON with the row_to_json() and hstore_to_json() functions:
# these mean that our callback handler will receive valid JSON.
#
# Finally, the call to the pg_notify() function is what actually sends the
# event. All subscribers on {channel} will receive the notification.
SQL_CREATE_TRIGGER = """\
CREATE OR REPLACE FUNCTION {trigger_name}()
RETURNS trigger AS $$
DECLARE
id integer; -- or uuid
data json;
BEGIN
data = json 'null';
IF TG_OP = 'INSERT' THEN
id = NEW.id;
data = row_to_json(NEW);
ELSIF TG_OP = 'UPDATE' THEN
id = NEW.id;
data = json_build_object(
'old', row_to_json(OLD),
'new', row_to_json(NEW),
'diff', hstore_to_json(hstore(NEW) - hstore(OLD))
);
ELSE
id = OLD.id;
data = row_to_json(OLD);
END IF;
PERFORM
pg_notify(
'{channel}',
json_build_object(
'table', TG_TABLE_NAME,
'id', id,
'type', TG_OP,
'data', data
)::text
);
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

# This is standard trigger code: it sets up a trigger to call a specific
# procedure {trigger_name}() when a specific event occurs, like an INSERT or
# an UPDATE.
SQL_TABLE_UPDATE = """\
DROP TRIGGER IF EXISTS
{table}_notify_update ON {schema}.{table};
CREATE TRIGGER {table}_notify_update
AFTER UPDATE ON {schema}.{table}
FOR EACH ROW
EXECUTE PROCEDURE {trigger_name}();
"""
SQL_TABLE_INSERT = """\
DROP TRIGGER IF EXISTS
{table}_notify_insert ON {schema}.{table};
CREATE TRIGGER {table}_notify_insert
AFTER INSERT ON {schema}.{table}
FOR EACH ROW
EXECUTE PROCEDURE {trigger_name}();
"""
SQL_TABLE_DELETE = """\
DROP TRIGGER IF EXISTS
{table}_notify_delete ON {schema}.{table};
CREATE TRIGGER {table}_notify_delete
AFTER DELETE ON {schema}.{table}
FOR EACH ROW
EXECUTE PROCEDURE {trigger_name}();
"""
