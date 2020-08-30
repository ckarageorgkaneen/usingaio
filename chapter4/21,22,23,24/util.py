# Example 4-22. Useful tooling for your asyncpg experiments
import argparse
import asyncio
import asyncpg
from asyncpg.pool import Pool

DSN = 'postgresql://{user}@{host}:{port}'
DSN_DB = DSN + '/{name}'
CREATE_DB = 'CREATE DATABASE {name}'
DROP_DB = 'DROP DATABASE {name}'


class Database:
    def __init__(self, name, owner=False, **kwargs):
        self.params = dict(
            user='postgres', host='localhost',
            port=55432, name=name)
        self.params.update(kwargs)
        self.pool: Pool = None
        self.owner = owner
        self.listeners = []

    async def connect(self) -> Pool:
        if self.owner:
            await self.server_command(
                CREATE_DB.format(**self.params))
        self.pool = await asyncpg.create_pool(
            DSN_DB.format(**self.params))
        return self.pool

    async def disconnect(self):
        """Destroy the database"""
        if self.pool:
            releases = [self.pool.release(conn)
                        for conn in self.listeners]
            await asyncio.gather(*releases)
            await self.pool.close()
        if self.owner:
            await self.server_command(
                DROP_DB.format(**self.params))

    async def __aenter__(self) -> Pool:
        return await self.connect()

    async def __aexit__(self, *exc):
        await self.disconnect()

    async def server_command(self, cmd):
        conn = await asyncpg.connect(
            DSN.format(**self.params))
        await conn.execute(cmd)
        await conn.close()

    async def add_listener(self, channel, callback):
        conn: asyncpg.Connection = await self.pool.acquire()
        await conn.add_listener(channel, callback)
        self.listeners.append(conn)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cmd', choices=['create', 'drop'])
    parser.add_argument('--name', type=str)
    args = parser.parse_args()
    d = Database(args.name, owner=True)
    if args.cmd == 'create':
        asyncio.run(d.connect())
    elif args.cmd == 'drop':
        asyncio.run(d.disconnect())
    else:
        parser.print_help()
