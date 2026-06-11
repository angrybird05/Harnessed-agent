from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, func
from backend.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), unique=True, index=True)
    source = Column(String(50))
    title = Column(String(255), nullable=False)
    company = Column(String(255))
    location = Column(String(255))
    job_url = Column(Text)
    apply_url = Column(Text)
    description = Column(Text)
    salary_min = Column(Float)
    salary_max = Column(Float)
    is_remote = Column(Boolean, default=False)
    required_skills = Column(Text)  # JSON array
    keywords = Column(Text)  # JSON array
    experience_required = Column(Integer)
    seniority_level = Column(String(50))
    recruiter_email = Column(String(255))
    careers_email = Column(String(255))
    fetched_at = Column(DateTime, server_default=func.now())
    analyzed_at = Column(DateTime)
