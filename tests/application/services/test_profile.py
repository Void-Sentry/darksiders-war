from infrastructure.database.repositories import profile_repository
from application.services import profile_service
from infrastructure.cache import cache_client
from infrastructure.auth import auth_client
from unittest.mock import MagicMock
from typing import Optional, List
import pytest

class TestProfileService:
    @pytest.fixture
    def service(self, monkeypatch):
        self.mock_repo = {
            'find_by': lambda *args, **kwargs: None,
            'insert': lambda *args, **kwargs: None,
            'count_followers': lambda *args, **kwargs: 0
        }
        
        self.mock_cache = {
            'get': lambda *args, **kwargs: None,
            'set': lambda *args, **kwargs: None,
            'zadd': lambda *args, **kwargs: None,
            'zrevrange': lambda *args, **kwargs: []
        }
        
        self.mock_auth = {
            'get_user': lambda *args, **kwargs: {},
            'search': lambda *args, **kwargs: []
        }

        monkeypatch.setattr(profile_repository, 'find_by', self.mock_repo['find_by'])
        monkeypatch.setattr(profile_repository, 'insert', self.mock_repo['insert'])
        monkeypatch.setattr(profile_repository, 'count_followers', self.mock_repo['count_followers'])
        
        monkeypatch.setattr(cache_client, 'get', self.mock_cache['get'])
        monkeypatch.setattr(cache_client, 'set', self.mock_cache['set'])
        monkeypatch.setattr(cache_client, 'zadd', self.mock_cache['zadd'])
        monkeypatch.setattr(cache_client, 'zrevrange', self.mock_cache['zrevrange'])
        
        monkeypatch.setattr(auth_client, 'get_user', self.mock_auth['get_user'])
        monkeypatch.setattr(auth_client, 'search', self.mock_auth['search'])
        
        return profile_service

    def test_info(self, service):
        test_user = {'id': '123', 'name': 'Test User'}
        self.mock_auth['get_user'] = lambda *args, **kwargs: test_user
        
        result = service.info('123')
        assert result == test_user

    def test_search_by_display_name(self, service):
        test_users = [{'id': '1', 'name': 'User 1'}, {'id': '2', 'name': 'User 2'}]
        self.mock_auth['search'] = lambda *args, **kwargs: test_users
        
        result = service.search(display_name='User')
        assert result == test_users

    def test_search_by_user_ids(self, service):
        test_users = [{'id': '1', 'name': 'User 1'}, {'id': '2', 'name': 'User 2'}]
        self.mock_auth['search'] = lambda *args, **kwargs: test_users
        
        result = service.search(user_ids=['1', '2'])
        assert result == test_users

    def test_followers_from_cache(self, service):
        test_followers = 100
        self.mock_cache['get'] = lambda *args, **kwargs: test_followers
        
        result = service.followers('123')
        assert result == test_followers

    def test_most_followed(self, service):
        test_users = [b'user1', b'user2'] if isinstance(cache_client.zrevrange("", 0, 0), list) else ['user1', 'user2']
        self.mock_cache['zrevrange'] = lambda *args, **kwargs: test_users
        
        result = service.most_followed(2)
        assert result == ['user1', 'user2']

    def test_edit_count_followers_new_user(self, service):
        self.mock_repo['find_by'] = lambda *args, **kwargs: []

        insert_called = False
        count_called = False
        cache_set_called = False
        zadd_called = False
        
        def mock_insert(*args, **kwargs):
            nonlocal insert_called
            insert_called = True
            return None
            
        def mock_count(*args, **kwargs):
            nonlocal count_called
            count_called = True
            return 1
            
        def mock_set(*args, **kwargs):
            nonlocal cache_set_called
            cache_set_called = True
            return None
            
        def mock_zadd(*args, **kwargs):
            nonlocal zadd_called
            zadd_called = True
            return None
            
        self.mock_repo['insert'] = mock_insert
        self.mock_repo['count_followers'] = mock_count
        self.mock_cache['set'] = mock_set
        self.mock_cache['zadd'] = mock_zadd
        
        service.edit_count_followers('123', 'increment')
        
        assert insert_called is True
        assert count_called is True
        assert cache_set_called is True
        assert zadd_called is True

    def test_edit_count_followers_existing_user(self, service):
        self.mock_repo['find_by'] = lambda *args, **kwargs: [{'id': '123'}]

        insert_called = False
        count_called = False
        
        def mock_insert(*args, **kwargs):
            nonlocal insert_called
            insert_called = True
            return None
            
        def mock_count(*args, **kwargs):
            nonlocal count_called
            count_called = True
            return 1
            
        self.mock_repo['insert'] = mock_insert
        self.mock_repo['count_followers'] = mock_count
        
        service.edit_count_followers('123', 'increment')
        
        assert insert_called is False
        assert count_called is True
