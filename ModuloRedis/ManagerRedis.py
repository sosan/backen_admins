import os
from urllib.parse import urlparse
import redis


class ManagerRedis:
    def __init__(self):
        self.conexion: redis.Redis = None

    def setRedisHerokuSinPool(self, nombrecliente=None):
        url = urlparse(os.environ.get('REDISCLOUD_URL'))
        self.conexion = redis.Redis(host=url.hostname, port=url.port, password=url.password)
        if nombrecliente is not None:
            self.conexion.client_setname(nombrecliente)

    def setupStreamGroup_RedisHeroku_Pool(self, key, grupo):
        redisconexion = self.getPoolRedisHeroku(True, "setupxgroup")
        if redisconexion.exists(key) == 0:
            redisconexion.xgroup_create(key, grupo, mkstream=True)
            redisconexion.close()

    def getPoolRedisHeroku(self, pool, nombrecliente=None):
        url = urlparse(os.environ.get('REDISCLOUD_URL'))
        try:
            redis_pool = redis.ConnectionPool(host=url.hostname, port=url.port, password=url.password)
            conexion = redis.Redis(connection_pool=redis_pool)
            if nombrecliente is not None:
                conexion.client_setname(nombrecliente)
            return conexion
        except redis.ConnectionError:
            raise ConnectionError()

    def setlocalRedisPool(self, nombrecliente=None):

        redis_pool = redis.ConnectionPool(host=os.environ.get("REDIS_HOST", "192.168.1.37"),
                                          port=os.environ.get("REDIS_PORT", 6379),
                                          db=0, decode_responses=True)
        self.conexion = redis.Redis(connection_pool=redis_pool)

    def setupStreamGroup_RedisLocal(self, key, grupo):

        if self.conexion.exists(key) == 0:
            self.conexion.xgroup_create(key, grupo, mkstream=True)


