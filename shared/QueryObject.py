from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from langchain_core.documents import Document

class SearchCVQuery(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="Name of the applicant to search in the CVs.",
    )
    email: Optional[str] = Field(
        default=None,
        description="Email of the applicant to search in the CVs.",
    )
    phone: Optional[str] = Field(
        default=None,
        description="Phone number of the applicant to search in the CVs.",
    )
    linkedIn: Optional[str] = Field(
        default=None,
        description="LinkedIn profile URL of the applicant to search in the CVs.",
    )
    gitRepo: Optional[str] = Field(
        default=None,
        description="Git repository URL (GitHub, GitLab, etc.) of the applicant to search in the CVs.",
    )
    experiencedSkills: Optional[Dict[str, float]] = Field(
        default=None,
        description="Dictionary of skills and their years of experience to search in the CVs."
    )
    keywords: List[str] = Field(
        default=None,
        description="List of keywords to search in the CVs."
    )
    skills: List[str] = Field(
        default=None,
        description="List of skills to search in the CVs."
    )
    jobTitles: List[str] = Field(
        default=None,
        description="List of job titles to search in the CVs."
    )
    location: Optional[str] = Field(
        default=None,
        description="Location of work to filter the CVs."
    )
    requirementDescription: Optional[str] = Field(
        default=None,
        description="Description of the job requirements to filter the CVs."
    )


    