"""
服务依赖注入模块
提供服务类的依赖注入函数
"""
from fastapi import Depends
from .wecom import WeComService
from .sheet_service import SheetService
from .local_excel import LocalExcelService


def get_wecom_service() -> WeComService:
    """
    获取企业微信服务实例
    
    Returns:
        WeComService: 企业微信服务实例
    """
    return WeComService()


def get_sheet_service(
    wecom_service: WeComService = Depends(get_wecom_service)
) -> SheetService:
    """
    获取表格服务实例
    
    Args:
        wecom_service: 企业微信服务实例（依赖注入）
        
    Returns:
        SheetService: 表格服务实例
    """
    return SheetService(wecom_service)


def get_local_excel_service() -> LocalExcelService:
    """
    获取本地 Excel 服务实例
    
    Returns:
        LocalExcelService: 本地 Excel 服务实例
    """
    return LocalExcelService()
