from typing import List, Optional
from sqlalchemy import select, and_, or_
from .models import Project, Company
from .repository import BaseRepository

class ProjectRepository(BaseRepository[Project]):
    async def get_active_projects(self) -> List[Project]:
        result = await self.session.execute(
            select(Project).where(Project.is_active == True))
        return list(result.scalars().all())

    async def get_projects_by_company(self, company_id: int) -> List[Project]:
        result = await self.session.execute(
            select(Project).where(Project.company_id == company_id))
        return list(result.scalars().all())

    async def search_projects(
        self,
        name: Optional[str] = None,
        stack: Optional[str] = None,
        direction: Optional[str] = None
    ) -> List[Project]:
        query = select(Project)
        conditions = []
        
        if name:
            conditions.append(Project.name.ilike(f"%{name}%"))
        if stack:
            conditions.append(Project.stack.ilike(f"%{stack}%"))
        if direction:
            conditions.append(Project.direction.ilike(f"%{direction}%"))
        
        if conditions:
            query = query.where(and_(*conditions))
            
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_projects_with_company(self) -> List[Project]:
        result = await self.session.execute(
            select(Project).join(Company).where(Project.company_id.is_not(None)))
        return list(result.scalars().all())