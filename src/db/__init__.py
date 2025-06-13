from sqlalchemy.ext.asyncio import AsyncSession
from .student_repository import StudentRepository
from .project_repository import ProjectRepository
from .company_repository import CompanyRepository
from .team_repository import TeamRepository
from .models import Student, Project, Company, Team
from .database import db
from fastapi import Depends

class Repositories:
    def __init__(self, session: AsyncSession):
        self.student_repo = StudentRepository(session, Student)
        self.project_repo = ProjectRepository(session, Project)
        self.company_repo = CompanyRepository(session, Company)
        self.team_repo = TeamRepository(session, Team)

async def get_session() -> AsyncSession:
    """Get database session"""

    async with db.async_session() as session:
        yield session

async def get_repositories(session: AsyncSession = Depends(get_session)) -> Repositories:
    """Dependency that provides repository instances."""
    return Repositories(session=session)