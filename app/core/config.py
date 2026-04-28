from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = Field(default='Real-Time AI Code Review Bot', alias='APP_NAME')
    app_env: str = Field(default='development', alias='APP_ENV')
    app_host: str = Field(default='0.0.0.0', alias='APP_HOST')
    app_port: int = Field(default=8000, alias='APP_PORT')
    log_level: str = Field(default='INFO', alias='LOG_LEVEL')

    gemini_api_key: str = Field(default='', alias='GEMINI_API_KEY')
    gemini_model: str = Field(default='gemini-2.5-flash', alias='GEMINI_MODEL')
    gemini_embedding_model: str = Field(default='gemini-embedding-001', alias='GEMINI_EMBEDDING_MODEL')

    github_webhook_secret: str = Field(default='', alias='GITHUB_WEBHOOK_SECRET')
    github_token: str = Field(default='', alias='GITHUB_TOKEN')

    qdrant_url: str = Field(default='http://localhost:6333', alias='QDRANT_URL')
    qdrant_api_key: str = Field(default='', alias='QDRANT_API_KEY')
    qdrant_collection: str = Field(default='code_review_memory', alias='QDRANT_COLLECTION')
    qdrant_vector_size: int = Field(default=3072, alias='QDRANT_VECTOR_SIZE')

    database_url: str = Field(default='sqlite:///./code_review_bot.db', alias='DATABASE_URL')

    max_diff_files: int = Field(default=25, alias='MAX_DIFF_FILES')
    max_diff_chars_per_file: int = Field(default=12000, alias='MAX_DIFF_CHARS_PER_FILE')
    inline_comment_fallback_to_pr_review: bool = Field(default=True, alias='INLINE_COMMENT_FALLBACK_TO_PR_REVIEW')


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
