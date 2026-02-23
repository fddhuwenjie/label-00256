"""
企业微信服务模块
支持真实模式和 Mock 模式
"""
import httpx
import json
import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path
from core.logger import logger
from core.exceptions import WeComAPIError, AuthenticationError
from config import settings


class SheetDataCache:
    """表格数据缓存"""
    
    def __init__(self, ttl_seconds: int = 300):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = ttl_seconds
    
    def _make_key(self, spreadsheet_id: str, sheet_id: str, range_str: str) -> str:
        return f"{spreadsheet_id}:{sheet_id}:{range_str}"
    
    def get(self, spreadsheet_id: str, sheet_id: str, range_str: str) -> Optional[Dict]:
        """获取缓存数据"""
        key = self._make_key(spreadsheet_id, sheet_id, range_str)
        if key in self._cache:
            entry = self._cache[key]
            if datetime.now() < entry['expires_at']:
                logger.debug(f"缓存命中: {key}")
                return entry['data']
            else:
                del self._cache[key]
                logger.debug(f"缓存过期: {key}")
        return None
    
    def set(self, spreadsheet_id: str, sheet_id: str, range_str: str, data: Dict):
        """设置缓存数据"""
        key = self._make_key(spreadsheet_id, sheet_id, range_str)
        self._cache[key] = {
            'data': data,
            'expires_at': datetime.now() + timedelta(seconds=self._ttl)
        }
        logger.debug(f"缓存设置: {key}, TTL={self._ttl}s")
    
    def invalidate(self, spreadsheet_id: str, sheet_id: str = None):
        """使缓存失效"""
        keys_to_delete = []
        for key in self._cache:
            if key.startswith(spreadsheet_id):
                if sheet_id is None or f":{sheet_id}:" in key:
                    keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self._cache[key]
            logger.debug(f"缓存失效: {key}")
    
    def clear(self):
        """清空所有缓存"""
        self._cache.clear()
        logger.info("缓存已清空")


class WeComService:
    """企业微信服务"""
    
    BASE_URL = "https://qyapi.weixin.qq.com/cgi-bin"
    MOCK_DATA_FILE = Path(__file__).parent.parent / "data" / "mock_sheets.json"
    
    def __init__(self):
        self.corp_id = settings.wecom_corp_id
        self.corp_secret = settings.wecom_corp_secret
        self.agent_id = settings.wecom_agent_id
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._token_cache: Dict[str, Any] = {}
        
        # 表格数据缓存（TTL 5分钟）
        self._sheet_cache = SheetDataCache(ttl_seconds=300)
        
        # 确保 Mock 数据目录存在
        self.MOCK_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    def is_mock_mode(self) -> bool:
        """检查是否为 Mock 模式"""
        return not bool(self.corp_id and self.corp_secret)
    
    @property
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(self.corp_id and self.corp_secret)
    
    def get_access_token(self) -> str:
        """获取access_token（同步版本，带缓存）"""
        # Mock 模式
        if self.is_mock_mode():
            mock_token = f"mock_access_token_{datetime.now().strftime('%Y%m%d')}"
            logger.info(f"Mock模式: 返回模拟token")
            return mock_token
        
        # 检查缓存
        if self._access_token and self._token_expires_at:
            if datetime.now() < self._token_expires_at:
                return self._access_token
        
        # 重新获取
        url = f"{self.BASE_URL}/gettoken"
        params = {
            "corpid": self.corp_id,
            "corpsecret": self.corp_secret
        }
        
        with httpx.Client() as client:
            response = client.get(url, params=params)
            data = response.json()
        
        if data.get("errcode", 0) != 0:
            raise WeComAPIError(data.get("errcode"), data.get("errmsg", "Unknown error"))
        
        self._access_token = data["access_token"]
        expires_in = data.get("expires_in", 7200)
        self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
        
        logger.info("获取企业微信access_token成功")
        return self._access_token
    
    async def get_access_token_async(self) -> str:
        """获取access_token（异步版本，带缓存）"""
        # Mock 模式
        if self.is_mock_mode():
            mock_token = f"mock_access_token_{datetime.now().strftime('%Y%m%d')}"
            logger.info(f"Mock模式: 返回模拟token")
            return mock_token
        
        # 检查缓存
        if self._access_token and self._token_expires_at:
            if datetime.now() < self._token_expires_at:
                return self._access_token
        
        # 重新获取
        url = f"{self.BASE_URL}/gettoken"
        params = {
            "corpid": self.corp_id,
            "corpsecret": self.corp_secret
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()
        
        if data.get("errcode", 0) != 0:
            raise WeComAPIError(data.get("errcode"), data.get("errmsg", "Unknown error"))
        
        self._access_token = data["access_token"]
        expires_in = data.get("expires_in", 7200)
        self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
        
        logger.info("获取企业微信access_token成功")
        return self._access_token
    
    # ==================== Mock 数据操作 ====================
    
    def _load_mock_data(self) -> Dict[str, Any]:
        """加载 Mock 数据"""
        if self.MOCK_DATA_FILE.exists():
            with open(self.MOCK_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"sheets": {}}
    
    def _save_mock_data(self, data: Dict[str, Any]):
        """保存 Mock 数据"""
        with open(self.MOCK_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _get_mock_sheet_key(self, spreadsheet_id: str, sheet_id: str) -> str:
        return f"{spreadsheet_id}_{sheet_id}"
    
    # ==================== 表格操作 ====================
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送API请求"""
        token = await self.get_access_token_async()
        url = f"{self.BASE_URL}{endpoint}"
        
        params = kwargs.pop("params", {})
        params["access_token"] = token
        
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, params=params, **kwargs)
            data = response.json()
        
        if data.get("errcode", 0) != 0:
            raise WeComAPIError(data.get("errcode"), data.get("errmsg", "Unknown error"))
        
        return data
    
    async def get_spreadsheet_info(self, spreadsheet_id: str) -> Dict[str, Any]:
        """获取表格信息"""
        if self.is_mock_mode():
            return {
                "errcode": 0,
                "errmsg": "ok",
                "doc_base_info": {
                    "docid": spreadsheet_id,
                    "doc_name": "Mock表格",
                    "doc_type": 10
                },
                "sheet_list": [
                    {"sheet_id": "Sheet1", "title": "工作表1", "index": 0}
                ]
            }
        
        return await self._request(
            "POST",
            "/wedoc/spreadsheet/get_sheet_properties",
            json={"docid": spreadsheet_id}
        )
    
    async def read_sheet_data(
        self, 
        spreadsheet_id: str, 
        sheet_id: str,
        range_str: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """读取表格数据（带缓存）"""
        # 检查缓存
        if use_cache:
            cached = self._sheet_cache.get(spreadsheet_id, sheet_id, range_str)
            if cached:
                logger.info(f"从缓存读取表格数据: {spreadsheet_id}/{sheet_id}/{range_str}")
                return cached
        
        # Mock 模式
        if self.is_mock_mode():
            mock_data = self._load_mock_data()
            key = self._get_mock_sheet_key(spreadsheet_id, sheet_id)
            sheet_data = mock_data.get("sheets", {}).get(key, {})
            
            result = {
                "errcode": 0,
                "errmsg": "ok",
                "data": sheet_data.get("values", []),
                "range": range_str
            }
            
            # 设置缓存
            if use_cache:
                self._sheet_cache.set(spreadsheet_id, sheet_id, range_str, result)
            
            logger.info(f"Mock模式: 读取表格数据 {key}")
            return result
        
        # 真实模式
        result = await self._request(
            "POST",
            "/wedoc/spreadsheet/get_sheet_range_data",
            json={
                "docid": spreadsheet_id,
                "sheet_id": sheet_id,
                "range": range_str
            }
        )
        
        # 设置缓存
        if use_cache:
            self._sheet_cache.set(spreadsheet_id, sheet_id, range_str, result)
        
        return result
    
    async def write_sheet_data(
        self,
        spreadsheet_id: str,
        sheet_id: str,
        range_str: str,
        values: list
    ) -> Dict[str, Any]:
        """写入表格数据"""
        # Mock 模式
        if self.is_mock_mode():
            mock_data = self._load_mock_data()
            key = self._get_mock_sheet_key(spreadsheet_id, sheet_id)
            
            if "sheets" not in mock_data:
                mock_data["sheets"] = {}
            
            mock_data["sheets"][key] = {
                "values": values,
                "range": range_str,
                "updated_at": datetime.now().isoformat()
            }
            
            self._save_mock_data(mock_data)
            
            # 使相关缓存失效
            self._sheet_cache.invalidate(spreadsheet_id, sheet_id)
            
            logger.info(f"Mock模式: 写入表格数据 {key}")
            return {
                "errcode": 0,
                "errmsg": "ok",
                "success": True,
                "updated_range": f"{sheet_id}!{range_str}",
                "updated_rows": len(values),
                "updated_columns": len(values[0]) if values else 0,
                "updated_cells": sum(len(row) for row in values)
            }
        
        # 真实模式
        result = await self._request(
            "POST",
            "/wedoc/spreadsheet/batch_update",
            json={
                "docid": spreadsheet_id,
                "requests": [{
                    "update_range": {
                        "sheet_id": sheet_id,
                        "range": range_str,
                        "values": values
                    }
                }]
            }
        )
        
        # 使相关缓存失效
        self._sheet_cache.invalidate(spreadsheet_id, sheet_id)
        
        return result
    
    def write_to_sheet(
        self,
        spreadsheet_token: str,
        sheet_id: str,
        range_str: str,
        values: list
    ) -> Dict[str, Any]:
        """同步写入表格数据（用于测试）"""
        if self.is_mock_mode():
            mock_data = self._load_mock_data()
            key = self._get_mock_sheet_key(spreadsheet_token, sheet_id)
            
            if "sheets" not in mock_data:
                mock_data["sheets"] = {}
            
            mock_data["sheets"][key] = {
                "values": values,
                "range": range_str,
                "updated_at": datetime.now().isoformat()
            }
            
            self._save_mock_data(mock_data)
            
            return {"success": True, "updated_cells": sum(len(row) for row in values)}
        
        raise NotImplementedError("同步模式仅支持 Mock")
    
    def read_from_sheet(
        self,
        spreadsheet_token: str,
        sheet_id: str,
        range_str: str
    ) -> Dict[str, Any]:
        """同步读取表格数据（用于测试）"""
        if self.is_mock_mode():
            mock_data = self._load_mock_data()
            key = self._get_mock_sheet_key(spreadsheet_token, sheet_id)
            sheet_data = mock_data.get("sheets", {}).get(key, {})
            
            return {
                "success": True,
                "data": sheet_data.get("values", []),
                "range": range_str
            }
        
        raise NotImplementedError("同步模式仅支持 Mock")
    
    def clear_cache(self):
        """清空表格数据缓存"""
        self._sheet_cache.clear()


# 单例
wecom_service = WeComService()
