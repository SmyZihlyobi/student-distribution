from sqlalchemy.ext.asyncio import AsyncSession
from .student_repository import StudentRepository
from .project_repository import ProjectRepository
from .company_repository import CompanyRepository
from .team_repository import TeamRepository
from .models import Student, Project, Company, Team
from .database import db
from typing import Dict, Any

async def get_session() -> AsyncSession:
    """Get database session"""
    if not db.async_session:
        await db.connect()
    async with db.async_session() as session:
        yield session

async def get_repositories() -> Dict[str, Any]:
    """Get repository instances"""
    session = await anext(get_session())
    return {
        'student_repo': StudentRepository(session, Student),
        'project_repo': ProjectRepository(session, Project),
        'company_repo': CompanyRepository(session, Company),
        'team_repo': TeamRepository(session, Team),
    }