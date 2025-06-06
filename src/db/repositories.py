from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Base, Company, Student, Project, Team, FavoriteProject

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: int) -> Optional[ModelType]:
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[ModelType]:
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        await self.session.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
        )
        await self.session.commit()
        return await self.get(id)

    async def delete(self, id: int) -> bool:
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.commit()
        return result.rowcount > 0


class CompanyRepository(BaseRepository[Company]):
    async def get_by_email(self, email: str) -> Optional[Company]:
        result = await self.session.execute(
            select(Company).where(Company.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Company]:
        result = await self.session.execute(
            select(Company).where(Company.name == name)
        )
        return result.scalar_one_or_none()


class StudentRepository(BaseRepository[Student]):
    async def get_by_username(self, username: str) -> Optional[Student]:
        result = await self.session.execute(
            select(Student)
            .options(selectinload(Student.team))
            .where(Student.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_team_id(self, team_id: int) -> List[Student]:
        result = await self.session.execute(
            select(Student)
            .options(selectinload(Student.team))
            .where(Student.team_id == team_id)
        )
        return result.scalars().all()

    async def get_all(self) -> List[Student]:
        result = await self.session.execute(
            select(Student).options(selectinload(Student.team))
        )
        return result.scalars().all()


class ProjectRepository(BaseRepository[Project]):
    async def get_active_projects(self) -> List[Project]:
        result = await self.session.execute(
            select(Project)
            .options(selectinload(Project.company))
            .where(Project.is_active == True)
        )
        return result.scalars().all()

    async def get_by_company_id(self, company_id: int) -> List[Project]:
        result = await self.session.execute(
            select(Project)
            .options(selectinload(Project.company))
            .where(Project.company_id == company_id)
        )
        return result.scalars().all()

    async def get_all(self) -> List[Project]:
        result = await self.session.execute(
            select(Project).options(selectinload(Project.company))
        )
        return result.scalars().all()


class TeamRepository(BaseRepository[Team]):
    async def get_by_name(self, name: str) -> Optional[Team]:
        result = await self.session.execute(
            select(Team)
            .options(selectinload(Team.student))
            .where(Team.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Team]:
        result = await self.session.execute(
            select(Team).options(selectinload(Team.student))
        )
        return result.scalars().all()


class FavoriteProjectRepository(BaseRepository[FavoriteProject]):
    async def get_by_student_id(self, student_id: int) -> List[FavoriteProject]:
        result = await self.session.execute(
            select(FavoriteProject).where(FavoriteProject.student_id == student_id)
        )
        return result.scalars().all()

    async def get_by_project_id(self, project_id: int) -> List[FavoriteProject]:
        result = await self.session.execute(
            select(FavoriteProject).where(FavoriteProject.project_id == project_id)
        )
        return result.scalars().all() 