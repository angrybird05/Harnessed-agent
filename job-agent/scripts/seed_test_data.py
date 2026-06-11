"""Seed the database with test data for development."""
import asyncio
import json
import sys
import os

# Add parent directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import AsyncSessionLocal
from backend.models.user import User
from backend.models.job import Job
from backend.models.application import Application
from backend.utils.auth import hash_password


async def seed_test_data():
    """Insert test users, jobs, and applications."""
    async with AsyncSessionLocal() as session:
        # Create test user
        test_user = User(
            email="testuser@example.com",
            hashed_password=hash_password("password123"),
            full_name="Jane Developer",
            phone="+1-555-0100",
            skills=json.dumps([
                "Python", "FastAPI", "React", "TypeScript",
                "PostgreSQL", "Docker", "AWS", "Redis",
                "Machine Learning", "Git"
            ]),
            education=json.dumps([
                {
                    "degree": "B.S. Computer Science",
                    "institution": "MIT",
                    "year": "2020"
                }
            ]),
            experience=json.dumps([
                {
                    "title": "Senior Software Engineer",
                    "company": "TechCorp",
                    "dates": "2022 - Present",
                    "bullets": [
                        "Led development of microservices architecture",
                        "Improved API response times by 40%",
                        "Mentored 3 junior developers"
                    ]
                },
                {
                    "title": "Software Engineer",
                    "company": "StartupXYZ",
                    "dates": "2020 - 2022",
                    "bullets": [
                        "Built real-time data processing pipeline",
                        "Developed REST APIs serving 10M+ requests/day",
                        "Implemented CI/CD with GitHub Actions"
                    ]
                }
            ]),
            projects=json.dumps([
                {
                    "name": "AI Job Agent",
                    "description": "Autonomous job application system using AI",
                    "tech": ["Python", "FastAPI", "Gemini", "Celery"]
                },
                {
                    "name": "Real-time Dashboard",
                    "description": "Live analytics dashboard with WebSocket updates",
                    "tech": ["React", "TypeScript", "WebSocket", "D3.js"]
                }
            ]),
            certifications=json.dumps([
                "AWS Solutions Architect Associate",
                "Google Cloud Professional Data Engineer"
            ]),
            github_url="https://github.com/janedeveloper",
            linkedin_url="https://linkedin.com/in/janedeveloper",
            portfolio_url="https://janedeveloper.com",
            preferred_roles=json.dumps([
                "Senior Software Engineer",
                "Backend Engineer",
                "Full Stack Developer"
            ]),
            preferred_locations=json.dumps(["Remote", "San Francisco", "New York"]),
            years_of_experience=5,
            resume_summary="Experienced software engineer with 5 years building scalable backend systems and AI-powered applications.",
        )
        session.add(test_user)
        await session.flush()

        # Create test jobs
        test_jobs = [
            Job(
                external_id="test_adzuna_1",
                source="adzuna",
                title="Senior Python Developer",
                company="DataFlow Inc",
                location="Remote",
                job_url="https://dataflow.io/careers/sr-python",
                apply_url="https://dataflow.io/apply/sr-python",
                description="We are looking for a Senior Python Developer with experience in FastAPI, PostgreSQL, and cloud services. Must have 4+ years experience.",
                salary_min=140000.0,
                salary_max=180000.0,
                is_remote=True,
                required_skills=json.dumps(["Python", "FastAPI", "PostgreSQL", "AWS"]),
                keywords=json.dumps(["python", "fastapi", "backend", "senior"]),
                experience_required=4,
                seniority_level="senior",
            ),
            Job(
                external_id="test_remotive_1",
                source="remotive",
                title="Full Stack Engineer",
                company="CloudNine Labs",
                location="Remote, Worldwide",
                job_url="https://cloudnine.io/careers/fullstack",
                apply_url="https://cloudnine.io/apply/fullstack",
                description="Join our team building the next-gen cloud platform. Looking for Full Stack Engineers with React and Python experience.",
                salary_min=120000.0,
                salary_max=160000.0,
                is_remote=True,
                required_skills=json.dumps(["React", "Python", "TypeScript", "Docker"]),
                keywords=json.dumps(["fullstack", "react", "python", "cloud"]),
                experience_required=3,
                seniority_level="mid",
            ),
            Job(
                external_id="test_adzuna_2",
                source="adzuna",
                title="Backend Engineer",
                company="FinTech Solutions",
                location="New York, NY",
                job_url="https://fintechsolutions.com/careers/backend",
                apply_url="https://fintechsolutions.com/apply/backend",
                description="Backend Engineer needed for our financial platform. Experience with Python, microservices, and payment systems required.",
                salary_min=150000.0,
                salary_max=200000.0,
                is_remote=False,
                required_skills=json.dumps(["Python", "Microservices", "PostgreSQL", "Redis"]),
                keywords=json.dumps(["backend", "fintech", "python", "payments"]),
                experience_required=5,
                seniority_level="senior",
            ),
        ]

        for job in test_jobs:
            session.add(job)
        await session.flush()

        # Create test applications
        test_applications = [
            Application(
                user_id=test_user.id,
                job_id=test_jobs[0].id,
                status="outreach_sent",
                match_score=85.0,
                resume_version="/app/resumes/test_1.pdf",
                cover_letter_text="Dear Hiring Manager, I am excited about the Senior Python Developer role...",
                thread_id="thread_abc123",
                followup_count=0,
            ),
            Application(
                user_id=test_user.id,
                job_id=test_jobs[1].id,
                status="applied",
                match_score=72.0,
                resume_version="/app/resumes/test_2.pdf",
                cover_letter_text="Dear CloudNine team, Your mission to build next-gen cloud infrastructure...",
            ),
            Application(
                user_id=test_user.id,
                job_id=test_jobs[2].id,
                status="interview_scheduled",
                match_score=90.0,
                resume_version="/app/resumes/test_3.pdf",
                cover_letter_text="Dear FinTech Solutions team, Building reliable financial systems...",
            ),
        ]

        for app in test_applications:
            session.add(app)

        await session.commit()
        print("Test data seeded successfully!")
        print(f"  - User: {test_user.email} (password: password123)")
        print(f"  - Jobs: {len(test_jobs)} test jobs created")
        print(f"  - Applications: {len(test_applications)} test applications created")


if __name__ == "__main__":
    asyncio.run(seed_test_data())
