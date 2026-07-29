"""
核心配置 —— 环境变量 / 数据库连接 / DeepSeek API 等
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── 应用 ──
    APP_NAME: str = "气象科学研究数据平台"
    VERSION: str = "6.1.0"
    DEBUG: bool = True
    # ⚠️ 生产环境请通过环境变量覆盖此值
    SECRET_KEY: str = "change-me-in-production"

    # ── 数据库 (PostgreSQL + PostGIS) ──
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    # ⚠️ 生产环境请通过环境变量覆盖此值
    DB_PASSWORD: str = "change-me-in-production"
    DB_NAME: str = "AcademicSearchDB"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # ── JWT ──
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24

    # ── 上传 ──
    UPLOAD_DIR: str = os.path.join(os.path.dirname(__file__), "..", "uploads")
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50 MB

    # ── DeepSeek AI ──
    # ⚠️ 请在 .env 文件中配置有效的 API Key
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # ── CORS ──
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
