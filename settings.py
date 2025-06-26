from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    openai_api_key: str

    langfuse_secret_key: str
    langfuse_public_key: str
    langfuse_host: str = "https://cloud.langfuse.com"

    default_model: str = "gpt-4.1-mini"
    default_cv_storage_path: str
    default_vectordb_storage_path: str

    mariadb_username: str
    mariadb_password: str
    mariadb_host: str
    mariadb_port: int
    mariadb_database: str

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache()
def get_settings() -> Settings:
    return Settings()