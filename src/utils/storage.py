import asyncio
import aioredis


class Database:
    def __init__(self, redis_url):
        self.redis_url = redis_url
        self.redis = None
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.connect())

    async def connect(self):
        self.redis = await aioredis.create_redis(
            self.redis_url,
            encoding='utf-8'
        )

    async def close(self):
        await self.redis.close()

    async def get_storage(self, server):
        prefix = "{}:".format(server.id)
        storage = Storage(
            prefix,
            self.redis
        )
        return storage


class Storage:
    def __init__(self, prefix, redis):
        self.prefix = prefix
        self.redis = redis

    async def set(self, key, value, expire=0):
        key = self.prefix + key
        return await self.redis.set(key, value, expire=expire)

    async def get(self, key):
        key = self.prefix + key
        return await self.redis.get(key)

    async def sort(self, key, *get_patterns, by=None, offset=None, count=None, asc=None, alpha=False, store=None):
        key = self.prefix + key
        if by:
            by = self.prefix + by
        return await self.redis.sort(key, *get_patterns, by=by, offset=offset, count=count, asc=asc, alpha=alpha, store=store)

    async def sadd(self, key, member, *members):
        key = self.prefix + key
        return await self.redis.sadd(key, member, *members)

    async def srem(self, key, value):
        key = self.prefix + key
        return await self.redis.srem(key, value)

    async def smembers(self, key):
        key = self.prefix + key
        return await self.redis.smembers(key)

    async def incrby(self, key, amount):
        key = self.prefix + key
        return await self.redis.incrby(key, amount)

    async def delete(self, key, *keys):
        key = self.prefix + key
        return await self.redis.delete(key, *keys)
