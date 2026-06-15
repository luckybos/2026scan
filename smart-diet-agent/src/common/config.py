from pathlib import Path
from typing import Dict, Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置管理"""
    
    # 应用设置
    app_name: str = "Smart Diet Agent"
    app_version: str = "1.0.0"
    
    # 数据库配置
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "smart_diet"
    db_user: str = "admin"
    db_password: str = "password"
    
    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # LLM配置
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str = ""
    llm_base_url: str = ""
    
    # 日志配置
    log_level: str = "INFO"
    
    @property
    def database_url(self) -> str:
        """获取数据库连接URL"""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# 全局配置实例
settings = Settings()
