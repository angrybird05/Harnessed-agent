import json
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    # FIX HIGH-07: Use EmailStr instead of str for proper email format validation
    email: EmailStr
    password: str
    full_name: Optional[str] = None

    # FIX HIGH-08: Enforce password strength on the backend (not just frontend)
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserLogin(BaseModel):
    # FIX HIGH-07: Use EmailStr for consistent validation
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    id: int
    # FIX HIGH-07: Use EmailStr in response model too
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[str] = None
    education: Optional[str] = None
    experience: Optional[str] = None
    projects: Optional[str] = None
    certifications: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    preferred_roles: Optional[str] = None
    preferred_locations: Optional[str] = None
    years_of_experience: int = 0
    resume_summary: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


def _validate_json_array(v: Optional[str]) -> Optional[str]:
    """Validate that a string value is a valid JSON array."""
    if v is None:
        return v
    try:
        parsed = json.loads(v) if isinstance(v, str) else v
        if not isinstance(parsed, list):
            raise ValueError("Must be a JSON array (e.g., [\"item1\", \"item2\"])")
        return v
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON — {exc}") from exc


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    # FIX MED-07: Validate JSON array fields to prevent corrupted data
    skills: Optional[str] = None
    education: Optional[str] = None
    experience: Optional[str] = None
    projects: Optional[str] = None
    certifications: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    preferred_roles: Optional[str] = None
    preferred_locations: Optional[str] = None
    years_of_experience: Optional[int] = None
    resume_summary: Optional[str] = None

    @field_validator(
        "skills", "education", "experience", "projects",
        "certifications", "preferred_roles", "preferred_locations",
        mode="before",
    )
    @classmethod
    def validate_json_arrays(cls, v: Optional[str]) -> Optional[str]:
        return _validate_json_array(v)
