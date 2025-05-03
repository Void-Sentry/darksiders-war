from infrastructure.database.repositories import profile_repository
from infrastructure.cache import cache_client
from infrastructure.auth import auth_client
from typing import Optional, List

class ProfileService:
    def __init__(self):
        self.repo = profile_repository
        self.client = auth_client
        self.cache = cache_client

    def info(self, user_id):
        return self.client.get_user(user_id)
    
    def search(self, display_name: Optional[str] = None, user_ids: Optional[List[str]] = None):
        return self.client.search(display_name, user_ids)
    
    def followers(self, user_id):
        return self.cache.get(f"users:followers:{user_id}")
    
    def most_followed(self, count=10):
        return self.cache.zrevrange("users:followers:ranking", 0, count - 1, withscores=False)
    
    def edit_count_followers(self, user_id, operation):
        profiles = self.repo.find_by({ 'id': user_id })

        if not profiles:
            self.repo.insert({ 'id': user_id })

        total = self.repo.count_followers(user_id, operation)

        self.cache.set(f"users:followers:{user_id}", total)
        self.cache.zadd("users:followers:ranking", { f"{user_id}": total })
