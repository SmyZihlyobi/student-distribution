from sqlalchemy.ext.asyncio import AsyncSession
from .student_repository import StudentRepository
from .project_repository import ProjectRepository
from .company_repository import CompanyRepository
from .team_repository import TeamRepository
from .models import Student, Project, Company, Team

async def get_repositories(session: AsyncSession):
    return {
        'students': StudentRepository(session, Student),
        'projects': ProjectRepository(session, Project),
        'companies': CompanyRepository(session, Company),
        'teams': TeamRepository(session, Team),
    }