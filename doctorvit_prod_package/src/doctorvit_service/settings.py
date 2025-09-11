
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    port: int = Field(default=8000)
    redis_host: str = Field(default="redis")
    redis_port: int = Field(default=6379)
    artifacts_dir: str = Field(default="/app/artifacts")
    notebook_path: str = Field(default="/app/notebooks/DoctorVIT_V1.ipynb")
    converted_module_path: str = Field(default="/app/artifacts/converted_module.py")

settings = Settings()
