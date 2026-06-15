from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes.diet import router as diet_router
from src.common.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="智能饮食助手 API"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(diet_router, prefix="/api", tags=["diet"])


@app.get("/")
async def root():
    """健康检查"""
    return {"message": f"{settings.app_name} API is running"}


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "version": settings.app_version}
