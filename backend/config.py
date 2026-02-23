"""
配置管理模块
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置"""
    
    # 企业微信配置
    wecom_corp_id: str = ""
    wecom_corp_secret: str = ""
    wecom_agent_id: str = ""
    
    # API配置
    api_key: str = "test-api-key-256"
    debug: bool = False
    
    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
