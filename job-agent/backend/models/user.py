from sqlalchemy import Column, Integer, String, Text, DateTime, func
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    phone = Column(String(50))
    skills = Column(Text)  # JSON array string
    education = Column(Text)  # JSON array string
    experience = Column(Text)  # JSON array string
    projects = Column(Text)  # JSON array string
    certifications = Column(Text)  # JSON array string
    github_url = Column(String(255))
    linkedin_url = Column(String(255))
    portfolio_url = Column(String(255))
    preferred_roles = Column(Text)  # JSON array string
    preferred_locations = Column(Text)  # JSON array string
    years_of_experience = Column(Integer, default=0)
    resume_summary = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
