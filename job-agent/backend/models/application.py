from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, UniqueConstraint, func
from backend.database import Base


APPLICATION_STATUSES = [
    "pending",
    "outreach_sent",
    "applied",
    "interview_scheduled",
    "request_for_info",
    "rejected",
    "no_reply",
    "selected",
    "withdrawn",
    # FIX CRIT-03: These are returned by reply_classifier but were missing here,
    # causing corrupted data when written to the DB and 422 errors on subsequent
    # status updates via the API.
    "interested",
    "out_of_office",
]


class Application(Base):
    __tablename__ = "applications"
    # FIX HIGH-04: Unique constraint prevents duplicate applications from race
    # conditions when multiple Celery workers process the same user/job pair.
    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job_application"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    status = Column(String(50), default="pending")
    thread_id = Column(String(255))
    followup_count = Column(Integer, default=0)
    last_email_sent_at = Column(DateTime)
    celery_task_id = Column(String(255))
    resume_version = Column(String(255))
    cover_letter_text = Column(Text)
    match_score = Column(Float)
    applied_at = Column(DateTime)
    followup_due_at = Column(DateTime)
    response_received_at = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
