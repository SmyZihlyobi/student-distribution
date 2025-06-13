from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKeyConstraint, Identity, Index, Integer, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

class Base(DeclarativeBase):
    pass


class Company(Base):
    __tablename__ = 'company'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='company_pkey'),
        UniqueConstraint('email', name='ukbma9lv19ba3yjwf12a34xord3'),
        UniqueConstraint('name', name='ukniu8sfil2gxywcru9ah3r4ec5')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    contacts: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=6))
    email: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    representative: Mapped[str] = mapped_column(String(255))
    student_company: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))
    password: Mapped[Optional[str]] = mapped_column(String(255))
    website: Mapped[Optional[str]] = mapped_column(String(255))

    project: Mapped[List['Project']] = relationship('Project', back_populates='company')


class FavoriteProject(Base):
    __tablename__ = 'favorite_project'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='favorite_project_pkey'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    project_id: Mapped[int] = mapped_column(BigInteger)
    student_id: Mapped[int] = mapped_column(BigInteger)


class FlywaySchemaHistory(Base):
    __tablename__ = 'flyway_schema_history'
    __table_args__ = (
        PrimaryKeyConstraint('installed_rank', name='flyway_schema_history_pk'),
        Index('flyway_schema_history_s_idx', 'success')
    )

    installed_rank: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String(200))
    type: Mapped[str] = mapped_column(String(20))
    script: Mapped[str] = mapped_column(String(1000))
    installed_by: Mapped[str] = mapped_column(String(100))
    installed_on: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('now()'))
    execution_time: Mapped[int] = mapped_column(Integer)
    success: Mapped[bool] = mapped_column(Boolean)
    version: Mapped[Optional[str]] = mapped_column(String(50))
    checksum: Mapped[Optional[int]] = mapped_column(Integer)


class Team(Base):
    __tablename__ = 'team'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='team_pkey'),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))

    student: Mapped[List['Student']] = relationship('Student', back_populates='team')


class Project(Base):
    __tablename__ = 'project'
    __table_args__ = (
        ForeignKeyConstraint(['company_id'], ['company.id'], name='fk76fngi71pfr8phbobe5pq0swd'),
        PrimaryKeyConstraint('id', name='project_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=6))
    description: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(String(255))
    stack: Mapped[str] = mapped_column(String(255))
    is_student_project: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))
    teams_amount: Mapped[int] = mapped_column(Integer, server_default=text('1'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=6))
    presentation: Mapped[Optional[str]] = mapped_column(String(255))
    technical_specifications: Mapped[Optional[str]] = mapped_column(String(255))
    company_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    direction: Mapped[Optional[str]] = mapped_column(String(255))
    required_roles: Mapped[Optional[str]] = mapped_column(String(255))

    company: Mapped[Optional['Company']] = relationship('Company', back_populates='project')


class Student(Base):
    __tablename__ = 'student'
    __table_args__ = (
        ForeignKeyConstraint(['team_id'], ['team.id'], name='fkmdgbo3apnk7o38pp6ua3ig139'),
        PrimaryKeyConstraint('id', name='student_pkey'),
        UniqueConstraint('username', name='ukjyet50p17q01ks2bv4sn8i5r7')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=6))
    first_name: Mapped[Optional[str]] = mapped_column(String(255))
    first_priority: Mapped[Optional[int]] = mapped_column(Integer)
    group_id: Mapped[Optional[str]] = mapped_column(String(255))
    last_name: Mapped[Optional[str]] = mapped_column(String(255))
    other_priorities: Mapped[Optional[str]] = mapped_column(String(255))
    patronymic: Mapped[Optional[str]] = mapped_column(String(255))
    resume_link: Mapped[Optional[str]] = mapped_column(String(255))
    resume_pdf: Mapped[Optional[str]] = mapped_column(String(255))
    second_priority: Mapped[Optional[int]] = mapped_column(Integer)
    team_name: Mapped[Optional[str]] = mapped_column(String(255))
    telegram: Mapped[Optional[str]] = mapped_column(String(255))
    third_priority: Mapped[Optional[int]] = mapped_column(Integer)
    year: Mapped[Optional[int]] = mapped_column(Integer)
    team_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    desired_role: Mapped[Optional[str]] = mapped_column(String(255))
    stack: Mapped[Optional[str]] = mapped_column(String(255))

    team: Mapped[Optional['Team']] = relationship('Team', back_populates='student')


t_user_roles = Table(
    'user_roles', Base.metadata,
    Column('user_id', BigInteger, nullable=False),
    Column('role', String(255), nullable=False),
    ForeignKeyConstraint(['user_id'], ['company.id'], name='fksaltqa4odo78cuohnisbw22l6')
)


t_student_roles = Table(
    'student_roles', Base.metadata,
    Column('student_id', BigInteger, nullable=False),
    Column('role', String(255), nullable=False),
    ForeignKeyConstraint(['student_id'], ['student.id'], name='fk5wsgmwcdh1mu2aakbatae9ouh')
)
