"""
企业微信服务模块
"""
import httpx
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from core.logger import logger
from core.exceptions import WeComAPIError, AuthenticationError
from config import settings


class WeComService:
    """企业微信服务"""
    
    BASE_URL = "https://qyapi.weixin.qq.com/cgi-bin"
    
    def __init__(self):
        self.corp_id = settings.wecom_corp_id
        self.corp_secret = settings.wecom_corp_secret
        self.agent_id = settings.wecom_agent_id
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
    
    @property
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(self.corp_id and self.corp_secret)
    
    async def get_access_token(self) -> str:
        """获取access_token（带缓存）"""
        # 检查缓存
        if self._access_token and self._token_expires_at:
            if datetime.now() < self._token_expires_at:
                return self._access_token
        
        # 重新获取
        if not self.is_configured:
            raise AuthenticationError("企业微信未配置，请设置 WECOM_CORP_ID 和 WECOM_CORP_SECRET")
        
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
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送API请求"""
        token = await self.get_access_token()
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
        return await self._request(
            "POST",
            "/wedoc/spreadsheet/get_sheet_properties",
            json={"docid": spreadsheet_id}
        )
    
    async def read_sheet_data(
        self, 
        spreadsheet_id: str, 
        sheet_id: str,
        range_str: str
    ) -> Dict[str, Any]:
        """读取表格数据"""
        return await self._request(
            "POST",
            "/wedoc/spreadsheet/get_sheet_range_data",
            json={
                "docid": spreadsheet_id,
                "sheet_id": sheet_id,
                "range": range_str
            }
        )
    
    async def write_sheet_data(
        self,
        spreadsheet_id: str,
        sheet_id: str,
        range_str: str,
        values: list
    ) -> Dict[str, Any]:
        """写入表格数据"""
        return await self._request(
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


# 单例
wecom_service = WeComService()
