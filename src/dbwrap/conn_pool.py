import asyncpg
import asyncio
from contextlib import asynccontextmanager

class DatabasePool:
    _pool = None
    _default_dsn = "postgresql://thymelaadmin:This_Is_My_Database_There_Are_Many_Like_It_But_This_One_Is_Mine@db-thymela.cfak28agap23.eu-west-1.rds.amazonaws.com/thymeladatabase"

    @classmethod
    async def create_pool(cls, dsn=None):
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(dsn or cls._default_dsn)
        return cls._pool

    @classmethod
    @asynccontextmanager
    async def acquire(cls):
        if cls._pool is None:
            await cls.create_pool()
        async with cls._pool.acquire() as connection:
            yield connection

# Usage example:
async def main():
    # Use the pool
    async with DatabasePool.acquire() as conn:
        result = await conn.fetch("""SELECT * FROM public."processed_Studies" """)    # The connection is automatically released back to the pool
        print(len(result))
