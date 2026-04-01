"""
服务模块
保持向后兼容性
"""
from .wecom import WeComService
from .sheet_service import SheetService
from .local_excel import LocalExcelService
from .dependencies import (
    get_wecom_service,
    get_sheet_service,
    get_local_excel_service,
)

# 保持向后兼容性：创建单例实例
_wecom_service_instance = None
_sheet_service_instance = None
_local_excel_service_instance = None


def _get_wecom_service_singleton():
    global _wecom_service_instance
    if _wecom_service_instance is None:
        _wecom_service_instance = WeComService()
    return _wecom_service_instance


def _get_sheet_service_singleton():
    global _sheet_service_instance
    global _wecom_service_instance
    if _sheet_service_instance is None:
        if _wecom_service_instance is None:
            _wecom_service_instance = WeComService()
        _sheet_service_instance = SheetService(_wecom_service_instance)
    return _sheet_service_instance


def _get_local_excel_service_singleton():
    global _local_excel_service_instance
    if _local_excel_service_instance is None:
        _local_excel_service_instance = LocalExcelService()
    return _local_excel_service_instance


wecom_service = _get_wecom_service_singleton()
sheet_service = _get_sheet_service_singleton()
local_excel_service = _get_local_excel_service_singleton()

__all__ = [
    "WeComService",
    "SheetService",
    "LocalExcelService",
    "get_wecom_service",
    "get_sheet_service",
    "get_local_excel_service",
    "wecom_service",
    "sheet_service",
    "local_excel_service",
]
