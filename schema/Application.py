from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import TEXT
from sqlalchemy.dialects.postgresql import TEXT as PG_TEXT
from typing import Optional, List, Dict, Any
from datetime import datetime

class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    vectorDbUuid: str = Field(index=True, description="UUID referencing the vector database document")
    name: str = Field(index=True, description="Name of the applicant")
    email: Optional[str] = Field(default=None, index=True, description="Email of the applicant")
    phone: Optional[str] = Field(default=None, index=True, description="Phone number of the applicant")
    address: Optional[str] = Field(default=None, index=True, description="Address of the applicant")
    education: List['Education'] = Relationship(back_populates="application", cascade_delete=True)
    skills: List['ExperiencedSkill'] = Relationship(back_populates="application", cascade_delete=True)
    workExperiences: List['WorkExperience'] = Relationship(back_populates="application", cascade_delete=True)
    projects: List['Project'] = Relationship(back_populates="application", cascade_delete=True)
    linkedIn: Optional[str] = Field(default=None, index=True, description="LinkedIn profile URL of the applicant")
    gitRepo: Optional[str] = Field(default=None, index=True, description="Git repository URL (GitHub, GitLab, etc.) of the applicant")
    yearsOfExperience: Optional[float] = Field(default=None, description="Total years of experience of the applicant")
    lastUpdated: datetime = Field(default_factory=datetime.now, description="Last updated timestamp of the application")

class Education(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="application.id", index=True, description="ID of the application this education belongs to")
    application: Optional[Application] = Relationship(back_populates="education")
    degree: str = Field(index=True, description="Degree obtained by the applicant")
    institution: str = Field(index=True, description="Institution where the degree was obtained")
    year: Optional[str] = Field(default=None, index=True, description="Year of graduation of period of education")
    gpa: Optional[str] = Field(default=None, description="GPA obtained by the applicant")

class ExperiencedSkill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="application.id", index=True, description="ID of the application this skill belongs to")
    application: Optional[Application] = Relationship(back_populates="skills")
    skill: str = Field(index=True, description="Name of the skill")
    yearsOfExperience: Optional[float] = Field(default=None, description="Years of experience in the skill")

class WorkExperience(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="application.id", index=True, description="ID of the application this work experience belongs to")
    application: Optional[Application] = Relationship(back_populates="workExperiences")
    company: str = Field(index=True, description="Company where the applicant worked")
    position: str = Field(index=True, description="Position held by the applicant")
    startDate: Optional[datetime] = Field(description="Start date of the work experience")
    endDate: Optional[datetime] = Field(default=None, description="End date of the work experience (if applicable)")
    description: Optional[str] = Field(default=None, sa_column=Column(TEXT), description="Description of the work experience")

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="application.id", index=True, description="ID of the application this project belongs to")
    application: Optional[Application] = Relationship(back_populates="projects")
    name: str = Field(index=True, description="Name of the project")
    description: Optional[str] = Field(default=None, sa_column=Column(TEXT), description="Description of the project")
    startDate: Optional[datetime] = Field(description="Start date of the project")
    endDate: Optional[datetime] = Field(default=None, description="End date of the project (if applicable)")