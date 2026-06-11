from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class JobOut(BaseModel):
    id: int
    external_id: Optional[str] = None
    source: Optional[str] = None
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    job_url: Optional[str] = None
    apply_url: Optional[str] = None
    description: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    is_remote: bool = False
    required_skills: Optional[str] = None
    keywords: Optional[str] = None
    experience_required: Optional[int] = None
    seniority_level: Optional[str] = None
    recruiter_email: Optional[str] = None
    careers_email: Optional[str] = None
    fetched_at: Optional[datetime] = None
    analyzed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobDiscoverResponse(BaseModel):
    task_id: str
    message: str
