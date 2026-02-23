"""
核心模块 - 异常处理
"""
from fastapi import HTTPException, status


class WeComAPIError(Exception):
    """企业微信API错误"""
    def __init__(self, errcode: int, errmsg: str):
        self.errcode = errcode
        self.errmsg = errmsg
        super().__init__(f"WeComAPI Error [{errcode}]: {errmsg}")


class SheetNotFoundError(Exception):
    """表格不存在"""
    pass


class CellNotFoundError(Exception):
    """单元格不存在"""
    pass


class AuthenticationError(Exception):
    """认证错误"""
    pass


class InvalidParameterError(Exception):
    """参数错误"""
    pass


def raise_http_error(status_code: int, detail: str):
    """抛出HTTP错误"""
    raise HTTPException(status_code=status_code, detail=detail)


def raise_unauthorized():
    """抛出未授权错误"""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key",
        headers={"WWW-Authenticate": "ApiKey"}
    )


def raise_not_found(resource: str):
    """抛出资源不存在错误"""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} not found"
    )


def raise_bad_request(detail: str):
    """抛出请求错误"""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail
    )
