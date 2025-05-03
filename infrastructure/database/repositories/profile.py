from infrastructure.database.utils.connection import get_db_connection
from .generic import GenericRepository

class ProfileRepository(GenericRepository):
    def __init__(self):
        super().__init__("profiles")

    def count_followers(self, user_id: str, operation: str):
        change = {'increment': 1, 'decrement': -1}[operation]

        query = f"""
            UPDATE {self.table_name}
            SET followers = GREATEST(followers + %s, 0)
            WHERE id = %s
            RETURNING followers
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (change, user_id))
                result = cur.fetchone()
                conn.commit()
                return result['followers'] if result else None
