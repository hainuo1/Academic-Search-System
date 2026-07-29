"""
FastAPI 主应用入口 —— 气象科学研究数据平台 v6.1
启动方式：uvicorn app.main:app --reload --host 0.0.0.0 --port 5000
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.routers import auth, search, document, favorites, citation, profile, stats, typhoon, earthquake, tornado, category

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# 注册路由
app.include_router(auth.router)
app.include_router(search.router)
app.include_router(document.router)
app.include_router(favorites.router)
app.include_router(citation.router)
app.include_router(profile.router)
app.include_router(stats.router)
app.include_router(typhoon.router)
app.include_router(earthquake.router)
app.include_router(tornado.router)
app.include_router(category.router)


@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"code": 404, "message": "接口不存在", "data": None})


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(status_code=500, content={"code": 500, "message": "服务器内部错误", "data": None})


@app.get("/")
def root():
    return {"code": 200, "message": f"{settings.APP_NAME} v{settings.VERSION}", "data": None}
