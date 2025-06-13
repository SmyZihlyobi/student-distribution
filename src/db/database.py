from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config import settings

class Database:
    def __init__(self):
        self.engine = None
        self.async_session_maker = None

    async def connect(self):
        """Создает движок и сессию для работы с базой данных"""
        database_url = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.DB_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        self.engine = create_async_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            echo=False
        )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def close(self):
        """Закрывает соединение с базой данных"""
        if self.engine:
            await self.engine.dispose()

    async def get_session(self) -> AsyncSession:
        """Возвращает сессию для работы с базой данных"""
        if not self.async_session or self.async_session is None:
            await self.connect()
        return self.async_session()
    
    async def disconnect(self):
        """Закрывает соединение с базой данных"""
        if self.engine:
            await self.engine.dispose()


db = Database()