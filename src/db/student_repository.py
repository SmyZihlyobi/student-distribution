from typing import List, Optional
from sqlalchemy import select, and_
from .models import Student, t_student_roles
from .repository import BaseRepository

class StudentRepository(BaseRepository[Student]):
    async def get_by_username(self, username: str) -> Optional[Student]:
        result = await self.session.execute(
            select(Student).where(Student.username == username))
        return result.scalars().first()

    async def get_student_roles(self, student_id: int) -> List[str]:
        result = await self.session.execute(
            select(t_student_roles.c.role)
            .where(t_student_roles.c.student_id == student_id))
        return [row[0] for row in result.all()]

    async def get_students_by_stack(self, stack_terms: List[str]) -> List[Student]:
        conditions = [Student.stack.ilike(f"%{term}%") for term in stack_terms]
        result = await self.session.execute(
            select(Student).where(and_(*conditions)))
        return list(result.scalars().all())

    async def get_student_by_id(self, student_id: int) -> Optional[Student]:
        result = await self.session.execute(
            select(Student).where(Student.id == student_id))
        return result.scalars().first()

    async def get_students_by_team(self, team_id: int) -> List[Student]:
        result = await self.session.execute(
            select(Student).where(Student.team_id == team_id))
        return list(result.scalars().all())