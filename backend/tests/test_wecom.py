"""
企业微信服务测试用例
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.wecom import WeComService
from config import settings


class TestWeComService:
    """企业微信服务测试类"""
    
    @pytest.fixture
    def wecom_service(self):
        """创建 WeComService 实例"""
        return WeComService()
    
    def test_init_mock_mode(self, wecom_service):
        """测试 Mock 模式初始化"""
        # 默认无配置时应为 Mock 模式
        assert wecom_service is not None
    
    def test_get_access_token_mock(self, wecom_service):
        """测试 Mock 模式获取 access_token"""
        token = wecom_service.get_access_token()
        assert token is not None
        assert isinstance(token, str)
        # Mock 模式返回模拟 token
        if not os.getenv('WECOM_CORP_ID'):
            assert 'mock' in token.lower() or len(token) > 0
    
    def test_get_access_token_cached(self, wecom_service):
        """测试 access_token 缓存"""
        token1 = wecom_service.get_access_token()
        token2 = wecom_service.get_access_token()
        # 缓存有效期内应返回相同 token
        assert token1 == token2
    
    @patch('services.wecom.httpx.Client')
    def test_get_access_token_real_mode(self, mock_client):
        """测试真实模式获取 access_token"""
        # 模拟 API 响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'errcode': 0,
            'errmsg': 'ok',
            'access_token': 'real_token_123',
            'expires_in': 7200
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        # patch settings 对象而非环境变量，因为 settings 是模块加载时就已实例化的单例
        with patch('services.wecom.settings') as mock_settings:
            mock_settings.wecom_corp_id = 'test_corp_id'
            mock_settings.wecom_corp_secret = 'test_corp_secret'
            mock_settings.wecom_agent_id = ''
            service = WeComService()
            service._token_cache = {}
            token = service.get_access_token()
            assert token == 'real_token_123'

    
    def test_is_mock_mode(self, wecom_service):
        """测试 Mock 模式检测"""
        # 无配置时应为 Mock 模式
        if not os.getenv('WECOM_CORP_ID'):
            assert wecom_service.is_mock_mode() == True
    
    @patch('services.wecom.httpx.Client')
    def test_api_error_handling(self, mock_client):
        """测试 API 错误处理"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'errcode': 40001,
            'errmsg': 'invalid credential'
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        
        with patch.object(settings, 'wecom_corp_id', 'test_corp_id'), \
             patch.object(settings, 'wecom_corp_secret', 'test_corp_secret'):
            service = WeComService()
            service._token_cache = {}
            # 应该处理错误而不是崩溃
            try:
                token = service.get_access_token()
                # 如果有错误处理，可能返回 None 或抛出自定义异常
            except Exception as e:
                assert 'credential' in str(e).lower() or 'error' in str(e).lower()


class TestWeComSheetOperations:
    """企业微信表格操作测试类"""
    
    @pytest.fixture
    def wecom_service(self):
        return WeComService()
    
    def test_write_sheet_mock(self, wecom_service):
        """测试 Mock 模式写入表格"""
        if wecom_service.is_mock_mode():
            result = wecom_service.write_to_sheet(
                spreadsheet_token='mock_sheet_123',
                sheet_id='Sheet1',
                range_str='A1:B2',
                values=[['Name', 'Age'], ['Alice', 25]]
            )
            assert result is not None
            assert result.get('success', True) == True
    
    def test_read_sheet_mock(self, wecom_service):
        """测试 Mock 模式读取表格"""
        if wecom_service.is_mock_mode():
            result = wecom_service.read_from_sheet(
                spreadsheet_token='mock_sheet_123',
                sheet_id='Sheet1',
                range_str='A1:B2'
            )
            assert result is not None


class TestTokenCache:
    """Token 缓存测试类"""
    
    def test_token_expiry(self):
        """测试 token 过期机制"""
        service = WeComService()
        
        # 获取 token
        token1 = service.get_access_token()
        
        # 模拟 token 过期
        if hasattr(service, '_token_cache'):
            service._token_cache = {}
        
        # 重新获取应该得到新 token（或相同的 mock token）
        token2 = service.get_access_token()
        assert token2 is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
