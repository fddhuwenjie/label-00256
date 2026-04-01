"""
企业微信 API 服务模块
封装企业微信 API 调用，支持真实模式和 Mock 模式
"""
import httpx
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
from core.logger import logger
from core.exceptions import WeComAPIError
from config import settings


class WeComService:
    """企业微信 API 服务

    封装企业微信 API 调用，自动处理 access_token 缓存，支持 Mock 模式
    """

    BASE_URL = "https://qyapi.weixin.qq.com/cgi-bin"
    MOCK_DATA_FILE = Path(__file__).parent.parent / "data" / "mock_sheets.json"

    def __init__(self):
        """初始化企业微信服务

        从配置文件读取企业微信应用配置，初始化 token 缓存
        """
        self.corp_id = settings.wecom_corp_id
        self.corp_secret = settings.wecom_corp_secret
        self.agent_id = settings.wecom_agent_id
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._token_cache: Dict[str, Any] = {}

        self.MOCK_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    def is_mock_mode(self) -> bool:
        """检查是否为 Mock 模式

        Returns:
            bool: 未配置企业微信信息时返回 True，表示使用 Mock 模式
        """
        return not bool(self.corp_id and self.corp_secret)

    @property
    def is_configured(self) -> bool:
        """检查企业微信是否已配置

        Returns:
            bool: corp_id 和 corp_secret 都配置时返回 True
        """
        return bool(self.corp_id and self.corp_secret)

    def get_access_token(self) -> str:
        """获取 access_token（同步版本，带缓存）

        Returns:
            str: access_token 字符串

        Raises:
            WeComAPIError: 获取 token 失败时抛出
        """
        if self.is_mock_mode():
            mock_token = f"mock_access_token_{datetime.now().strftime('%Y%m%d')}"
            logger.info("Mock模式: 返回模拟token")
            return mock_token

        if self._access_token and self._token_expires_at:
            if datetime.now() < self._token_expires_at:
                return self._access_token

        url = f"{self.BASE_URL}/gettoken"
        params = {"corpid": self.corp_id, "corpsecret": self.corp_secret}

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
        """获取 access_token（异步版本，带缓存）

        Returns:
            str: access_token 字符串

        Raises:
            WeComAPIError: 获取 token 失败时抛出
        """
        if self.is_mock_mode():
            mock_token = f"mock_access_token_{datetime.now().strftime('%Y%m%d')}"
            logger.info("Mock模式: 返回模拟token")
            return mock_token

        if self._access_token and self._token_expires_at:
            if datetime.now() < self._token_expires_at:
                return self._access_token

        url = f"{self.BASE_URL}/gettoken"
        params = {"corpid": self.corp_id, "corpsecret": self.corp_secret}

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
    
    def _load_mock_data(self) -> Dict[str, Any]:
        """加载 Mock 数据

        Returns:
            Dict[str, Any]: 从 JSON 文件加载的 Mock 数据
        """
        if self.MOCK_DATA_FILE.exists():
            with open(self.MOCK_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"sheets": {}}

    def _save_mock_data(self, data: Dict[str, Any]):
        """保存 Mock 数据到文件

        Args:
            data: 要保存的数据
        """
        with open(self.MOCK_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _get_mock_sheet_key(self, spreadsheet_id: str, sheet_id: str) -> str:
        """生成 Mock 数据的存储键

        Args:
            spreadsheet_id: 表格 ID
            sheet_id: 工作表 ID

        Returns:
            str: 用于存储的键字符串
        """
        return f"{spreadsheet_id}_{sheet_id}"

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送企业微信 API 请求

        Args:
            method: HTTP 方法
            endpoint: API 端点路径
            **kwargs: 请求参数

        Returns:
            Dict[str, Any]: API 响应数据

        Raises:
            WeComAPIError: API 返回错误码时抛出
        """
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
        """获取表格信息

        Args:
            spreadsheet_id: 表格 ID

        Returns:
            Dict[str, Any]: 表格元信息和工作表列表
        """
        if self.is_mock_mode():
            return {
                "errcode": 0,
                "errmsg": "ok",
                "doc_base_info": {
                    "docid": spreadsheet_id,
                    "doc_name": "Mock表格",
                    "doc_type": 10,
                },
                "sheet_list": [{"sheet_id": "Sheet1", "title": "工作表1", "index": 0}],
            }

        return await self._request(
            "POST",
            "/wedoc/spreadsheet/get_sheet_properties",
            json={"docid": spreadsheet_id},
        )

    async def read_sheet_data(
        self,
        spreadsheet_id: str,
        sheet_id: str,
        range_str: str,
    ) -> Dict[str, Any]:
        """读取表格数据

        注：缓存逻辑由 SheetService 层管理

        Args:
            spreadsheet_id: 表格 ID
            sheet_id: 工作表 ID
            range_str: 读取范围，如 "A1:C5"

        Returns:
            Dict[str, Any]: 包含表格数据的响应
        """
        if self.is_mock_mode():
            mock_data = self._load_mock_data()
            key = self._get_mock_sheet_key(spreadsheet_id, sheet_id)
            sheet_data = mock_data.get("sheets", {}).get(key, {})

            result = {
                "errcode": 0,
                "errmsg": "ok",
                "data": sheet_data.get("values", []),
                "range": range_str,
            }

            logger.info(f"Mock模式: 读取表格数据 {key}")
            return result

        result = await self._request(
            "POST",
            "/wedoc/spreadsheet/get_sheet_range_data",
            json={
                "docid": spreadsheet_id,
                "sheet_id": sheet_id,
                "range": range_str,
            },
        )

        return result

    async def write_sheet_data(
        self,
        spreadsheet_id: str,
        sheet_id: str,
        range_str: str,
        values: list,
    ) -> Dict[str, Any]:
        """写入表格数据

        Args:
            spreadsheet_id: 表格 ID
            sheet_id: 工作表 ID
            range_str: 写入范围
            values: 二维数组数据

        Returns:
            Dict[str, Any]: 写入结果
        """
        if self.is_mock_mode():
            mock_data = self._load_mock_data()
            key = self._get_mock_sheet_key(spreadsheet_id, sheet_id)

            if "sheets" not in mock_data:
                mock_data["sheets"] = {}

            mock_data["sheets"][key] = {
                "values": values,
                "range": range_str,
                "updated_at": datetime.now().isoformat(),
            }

            self._save_mock_data(mock_data)

            logger.info(f"Mock模式: 写入表格数据 {key}")
            return {
                "errcode": 0,
                "errmsg": "ok",
                "success": True,
                "updated_range": f"{sheet_id}!{range_str}",
                "updated_rows": len(values),
                "updated_columns": len(values[0]) if values else 0,
                "updated_cells": sum(len(row) for row in values),
            }

        result = await self._request(
            "POST",
            "/wedoc/spreadsheet/batch_update",
            json={
                "docid": spreadsheet_id,
                "requests": [
                    {
                        "update_range": {
                            "sheet_id": sheet_id,
                            "range": range_str,
                            "values": values,
                        }
                    }
                ],
            },
        )

        return result

    def write_to_sheet(
        self,
        spreadsheet_token: str,
        sheet_id: str,
        range_str: str,
        values: list,
    ) -> Dict[str, Any]:
        """同步写入表格数据（用于测试）

        Args:
            spreadsheet_token: 表格 ID
            sheet_id: 工作表 ID
            range_str: 写入范围
            values: 二维数组数据

        Returns:
            Dict[str, Any]: 写入结果

        Raises:
            NotImplementedError: 非 Mock 模式下抛出
        """
        if self.is_mock_mode():
            mock_data = self._load_mock_data()
            key = self._get_mock_sheet_key(spreadsheet_token, sheet_id)

            if "sheets" not in mock_data:
                mock_data["sheets"] = {}

            mock_data["sheets"][key] = {
                "values": values,
                "range": range_str,
                "updated_at": datetime.now().isoformat(),
            }

            self._save_mock_data(mock_data)

            return {"success": True, "updated_cells": sum(len(row) for row in values)}

        raise NotImplementedError("同步模式仅支持 Mock")

    def read_from_sheet(
        self,
        spreadsheet_token: str,
        sheet_id: str,
        range_str: str,
    ) -> Dict[str, Any]:
        """同步读取表格数据（用于测试）

        Args:
            spreadsheet_token: 表格 ID
            sheet_id: 工作表 ID
            range_str: 读取范围

        Returns:
            Dict[str, Any]: 读取结果

        Raises:
            NotImplementedError: 非 Mock 模式下抛出
        """
        if self.is_mock_mode():
            mock_data = self._load_mock_data()
            key = self._get_mock_sheet_key(spreadsheet_token, sheet_id)
            sheet_data = mock_data.get("sheets", {}).get(key, {})

            return {
                "success": True,
                "data": sheet_data.get("values", []),
                "range": range_str,
            }

        raise NotImplementedError("同步模式仅支持 Mock")
