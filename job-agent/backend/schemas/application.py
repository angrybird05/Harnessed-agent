from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from backend.models.application import APPLICATION_STATUSES


class ApplicationOut(BaseModel):
    id: int
    user_id: int
    job_id: int
    status: str = "pending"
    thread_id: Optional[str] = None
    followup_count: int = 0
    last_email_sent_at: Optional[datetime] = None
    celery_task_id: Optional[str] = None
    resume_version: Optional[str] = None
    cover_letter_text: Optional[str] = None
    match_score: Optional[float] = None
    applied_at: Optional[datetime] = None
    followup_due_at: Optional[datetime] = None
    response_received_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Job details (joined)
    job_title: Optional[str] = None
    job_company: Optional[str] = None
    job_location: Optional[str] = None
    job_url: Optional[str] = None
    is_remote: Optional[bool] = None

    class Config:
        from_attributes = True


class ApplicationStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in APPLICATION_STATUSES:
            raise ValueError(
                f"Invalid status '{v}'. Must be one of: {', '.join(APPLICATION_STATUSES)}"
            )
        return v
