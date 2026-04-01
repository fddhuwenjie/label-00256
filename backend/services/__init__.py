"""
服务层模块
提供依赖注入支持，所有服务类通过此模块对外暴露
"""
from services.wecom import WeComService
from services.sheet_service import SheetService, SheetDataCache
from services.local_excel import LocalExcelService


def get_wecom_service() -> WeComService:
    """获取企业微信服务实例（依赖注入）

    Returns:
        WeComService: 企业微信服务单例实例
    """
    return WeComService()


def get_sheet_service() -> SheetService:
    """获取表格服务实例（依赖注入）

    Returns:
        SheetService: 表格操作服务实例
    """
    wecom_service = get_wecom_service()
    return SheetService(wecom_service=wecom_service)


def get_local_excel_service() -> LocalExcelService:
    """获取本地 Excel 服务实例（依赖注入）

    Returns:
        LocalExcelService: 本地 Excel 操作服务实例
    """
    return LocalExcelService()


__all__ = [
    "WeComService",
    "SheetService",
    "SheetDataCache",
    "LocalExcelService",
    "get_wecom_service",
    "get_sheet_service",
    "get_local_excel_service",
]
