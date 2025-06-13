from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_USER: str = "pg"
    POSTGRES_PASSWORD: str = "pwd"
    POSTGRES_DB: str = "project-practice-api"
    DB_HOST: str = "localhost"
    MODEL_DIR: str = 'models'
    POSTGRES_PORT: int = 5432

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()