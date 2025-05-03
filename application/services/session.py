from infrastructure.cache import cache_client
import secrets
import time

class SessionService:
    def __init__(self):
        self.cache = cache_client

    def swap(self, decoded, token):
        sessionId = secrets.token_hex(32)
        key = f"users:sessions:{sessionId}"

        self.cache.set(key, token)
        ttl = decoded['exp'] - int(time.time())

        self.cache.expire(key, ttl)

        return sessionId, ttl
    
    def invalidate(self, session_id):
        key = f"users:sessions:{session_id}"
        self.cache.delete(key)
