from application.services import session_service
from infrastructure.cache import cache_client
from unittest.mock import MagicMock
import secrets
import pytest
import time

class TestSessionService:
    @pytest.fixture
    def service(self, monkeypatch):
        self.mock_cache = {
            'set': MagicMock(),
            'expire': MagicMock(),
            'delete': MagicMock()
        }

        self.mock_token_hex = MagicMock(return_value='mocked_session_id')

        self.mock_time = MagicMock(return_value=1234567890)

        monkeypatch.setattr(cache_client, 'set', self.mock_cache['set'])
        monkeypatch.setattr(cache_client, 'expire', self.mock_cache['expire'])
        monkeypatch.setattr(cache_client, 'delete', self.mock_cache['delete'])
        monkeypatch.setattr(secrets, 'token_hex', self.mock_token_hex)
        monkeypatch.setattr(time, 'time', self.mock_time)
        
        return session_service

    def test_swap(self, service):
        test_decoded = {'exp': 1234568000}
        test_token = 'test_jwt_token'

        session_id, ttl = service.swap(test_decoded, test_token)

        assert session_id == 'mocked_session_id'
        assert ttl == 110

        self.mock_cache['set'].assert_called_once_with(
            'users:sessions:mocked_session_id',
            test_token
        )
        self.mock_cache['expire'].assert_called_once_with(
            'users:sessions:mocked_session_id',
            110
        )
        
    def test_swap_with_past_expiration(self, service):
        test_decoded = {'exp': 1234567800}
        test_token = 'test_jwt_token'
        
        session_id, ttl = service.swap(test_decoded, test_token)
        
        assert ttl == 0
        
    def test_invalidate(self, service):
        test_session_id = 'test_session_id'
        
        service.invalidate(test_session_id)
        
        self.mock_cache['delete'].assert_called_once_with(
            'users:sessions:test_session_id'
        )

    def test_invalidate_empty_session(self, service):
        with pytest.raises(ValueError):
            service.invalidate('')
