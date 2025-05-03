from typing import List, Optional
import requests
import os

class AuthClient:
    def __init__(self):
        self.bearer_token = os.getenv('SERVICE_TOKEN')
        self.api_base_url = os.getenv('AUTH_URL_API')

    def _get_headers(self):
        return {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.bearer_token}',
            'Host': os.getenv('EXTERNAL_DOMAIN')
        }

    def get_user(self, user_id):
        url = f"{self.api_base_url}/v2/users/{user_id}"
        headers = self._get_headers()
        response = requests.get(url, headers=headers, data={})
        response.raise_for_status()
        return response.json()
    
    def search(self, display_name: Optional[str] = None, user_ids: Optional[List[str]] = None, page=1, size=10):
        url = f"{self.api_base_url}/v2/users"
        headers = self._get_headers()

        if not display_name and not user_ids:
            raise ValueError("You must provide either display_name or user_ids")

        if display_name:
            queries = [
                {
                    "displayNameQuery": {
                        "displayName": display_name,
                        "method": "TEXT_QUERY_METHOD_CONTAINS_IGNORE_CASE"
                    }
                }
            ]
        elif user_ids:
            queries = [
                {
                    "inUserIdsQuery": {
                        "userIds": user_ids
                    }
                }
            ]

        payload = {
            "query": {
                "offset": (page - 1) * size,
                "limit": size,
                "asc": False
            },
            "sortingColumn": "USER_FIELD_NAME_CREATION_DATE",
            "queries": queries
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        if data['details'].get('totalResult') is None:
            return []

        return data
