from typing import List, Optional
from sqlalchemy import select
from .models import Company, t_user_roles
from .repository import BaseRepository

class CompanyRepository(BaseRepository[Company]):
    async def get_by_email(self, email: str) -> Optional[Company]:
        result = await self.session.execute(
            select(Company).where(Company.email == email))
        return result.scalars().first()

    async def get_company_roles(self, company_id: int) -> List[str]:
        result = await self.session.execute(
            select(t_user_roles.c.role)
            .where(t_user_roles.c.user_id == company_id))
        return [row[0] for row in result.all()]

    async def get_student_companies(self) -> List[Company]:
        result = await self.session.execute(
            select(Company).where(Company.student_company == True))
        return list(result.scalars().all())