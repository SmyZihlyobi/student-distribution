from typing import List
from sqlalchemy import select
from .models import Team
from .repository import BaseRepository
from sqlalchemy.orm import selectinload
from .models import Student

class TeamRepository(BaseRepository[Team]):
    async def get_team_with_students(self, team_id: int) -> Team | None:
        result = await self.session.execute(
            select(Team)
            .where(Team.id == team_id)
            .options(selectinload(Team.student)))
        return result.scalars().first()

    async def get_teams_without_projects(self) -> List[Team]:
        result = await self.session.execute(
            select(Team)
            .where(~Team.student.any(Student.team_id.is_not(None))))
        return list(result.scalars().all())