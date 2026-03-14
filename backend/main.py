"""
企业微信表格操作 API 服务
主程序入口
"""
import os
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from core.logger import logger
from core.exceptions import WeComAPIError, AuthenticationError, ValidationError
from api.sheets import router as sheets_router
from api.health import router as health_router
from api.local_excel import router as local_excel_router

# 基于当前文件位置计算项目根目录，确保跨平台兼容
BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    (BASE_DIR / "logs").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "data").mkdir(parents=True, exist_ok=True)
    logger.info("=" * 50)
    logger.info("企业微信表格操作 API 服务启动")
    logger.info(f"Debug模式: {settings.debug}")
    logger.info(f"企业微信配置: {'已配置' if settings.wecom_corp_id else '未配置(Mock模式)'}")
    logger.info("=" * 50)
    yield
    logger.info("服务关闭")


app = FastAPI(
    title="企业微信表格操作 API",
    description="面向日常测试工作的 RESTful API 服务，支持企业微信在线表格的读写操作",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(WeComAPIError)
async def wecom_error_handler(request: Request, exc: WeComAPIError):
    logger.error(f"企业微信API错误: {exc.errcode} - {exc.errmsg}")
    return JSONResponse(
        status_code=502,
        content={
            "detail": {
                "code": f"WECOM_API_ERROR",
                "message": f"企业微信API错误: {exc.errmsg}"
            }
        }
    )


@app.exception_handler(AuthenticationError)
async def auth_error_handler(request: Request, exc: AuthenticationError):
    logger.error(f"认证错误: {exc}")
    return JSONResponse(
        status_code=401,
        content={
            "detail": {
                "code": "AUTH_FAILED",
                "message": str(exc)
            }
        }
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    logger.error(f"验证错误: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "code": "VALIDATION_ERROR",
                "message": str(exc)
            }
        }
    )


@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    logger.exception(f"未处理异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": {
                "code": "INTERNAL_ERROR",
                "message": "服务器内部错误"
            }
        }
    )


# 注册路由
app.include_router(health_router)
app.include_router(sheets_router)
app.include_router(local_excel_router, prefix="/api/v1/sheets")


# 根路径
@app.get("/", tags=["系统"])
async def root():
    """API根路径"""
    return {
        "name": "企业微信表格操作 API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info" if not settings.debug else "debug"
    )
