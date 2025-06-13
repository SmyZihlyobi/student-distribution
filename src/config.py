from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_USER: str = "pg"
    POSTGRES_PASSWORD: str = "pwd"
    POSTGRES_DB: str = "project-practice-api"
    DB_HOST: str = "localhost"
    MINIO_ROOT_USER: str = "7fcc12fdc2d1"
    MINIO_ROOT_PASSWORD: str = "96a19220ee73"
    MINIO_ENDPOINT: str = "http://localhost:9000"
    MODEL_DIR: str = 'C:\\Users\\malko\\PycharmProjects\\student_vectorizer\\distribution\\src\\models'
    POSTGRES_PORT: int = 5432
    AI: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()