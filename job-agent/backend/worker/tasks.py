import asyncio
import json
import logging
import os
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from backend.worker.celery_app import celery_app
from backend.config import settings
from backend.database import AsyncSessionLocal
from backend.models.user import User
from backend.models.job import Job
from backend.models.application import Application
from backend.agents.job_discovery import fetch_jobs
from backend.agents.jd_analyzer import analyze_jd
from backend.agents.match_scorer import score_match
from backend.agents.resume_engine import personalize_resume
from backend.agents.cover_letter import generate_cover_letter
from backend.agents.contact_finder import find_contact
from backend.agents.outreach_agent import generate_outreach_email
from backend.agents.apply_agent import auto_apply
from backend.agents.reply_classifier import classify_reply
from backend.services.pdf_generator import generate_resume_pdf
from backend.services.gmail import send_email, get_latest_reply_text

logger = logging.getLogger(__name__)


def _user_to_dict(user: User) -> dict:
    """Convert a User ORM object to a plain dict for agent functions."""
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "skills": user.skills,
        "education": user.education,
        "experience": user.experience,
        "projects": user.projects,
        "certifications": user.certifications,
        "github_url": user.github_url,
        "linkedin_url": user.linkedin_url,
        "portfolio_url": user.portfolio_url,
        "preferred_roles": user.preferred_roles,
        "preferred_locations": user.preferred_locations,
        "years_of_experience": user.years_of_experience,
        "resume_summary": user.resume_summary,
    }


def _job_to_dict(job: Job) -> dict:
    """Convert a Job ORM object to a plain dict for agent functions."""
    return {
        "id": job.id,
        "external_id": job.external_id,
        "source": job.source,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "job_url": job.job_url,
        "apply_url": job.apply_url,
        "description": job.description,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "is_remote": job.is_remote,
        "required_skills": job.required_skills,
        "keywords": job.keywords,
        "experience_required": job.experience_required,
        "seniority_level": job.seniority_level,
        "recruiter_email": job.recruiter_email,
        "careers_email": job.careers_email,
    }


async def _run_job_discovery(user_id: int):
    """Async implementation of job discovery task."""
    async with AsyncSessionLocal() as session:
        # 1. Load user
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            logger.error(f"User {user_id} not found")
            return

        user_profile = _user_to_dict(user)

        # 2. Parse preferred_roles and skills
        try:
            preferred_roles = json.loads(user.preferred_roles) if user.preferred_roles else []
        except (json.JSONDecodeError, TypeError):
            preferred_roles = []

        try:
            skills = json.loads(user.skills) if user.skills else []
        except (json.JSONDecodeError, TypeError):
            skills = []

        # 3. Fetch jobs
        keywords = preferred_roles + skills[:3]
        if not keywords:
            keywords = ["software engineer"]

        jobs_data = await fetch_jobs(keywords=keywords, location="remote")
        logger.info(f"Fetched {len(jobs_data)} jobs for user {user_id}")

        qualifying_count = 0

        for job_data in jobs_data:
            # 4. Save to DB if external_id not already present
            existing = await session.execute(
                select(Job).where(Job.external_id == job_data["external_id"])
            )
            if existing.scalar_one_or_none():
                continue

            job = Job(
                external_id=job_data.get("external_id"),
                source=job_data.get("source"),
                title=job_data.get("title", ""),
                company=job_data.get("company"),
                location=job_data.get("location"),
                job_url=job_data.get("job_url"),
                apply_url=job_data.get("apply_url"),
                description=job_data.get("description"),
                salary_min=job_data.get("salary_min"),
                salary_max=job_data.get("salary_max"),
                is_remote=job_data.get("is_remote", False),
            )
            session.add(job)
            await session.flush()

            # 5. Analyze JD
            if job.description:
                jd_result = await analyze_jd(job.description)
                job.required_skills = json.dumps(jd_result.get("required_skills", []))
                job.keywords = json.dumps(jd_result.get("keywords", []))
                job.experience_required = jd_result.get("experience_years", 0)
                job.seniority_level = jd_result.get("seniority_level")
                job.analyzed_at = datetime.now(timezone.utc)

                # 6. Score match
                match_result = await score_match(user_profile, jd_result)
                overall_score = match_result.get("overall_score", 0)

                # 7. If score >= 60, trigger application processing
                if overall_score >= 60:
                    qualifying_count += 1
                    await session.commit()
                    process_job_application.delay(user_id, job.id)
                else:
                    await session.commit()
            else:
                await session.commit()

        logger.info(
            f"Job discovery complete for user {user_id}: "
            f"{len(jobs_data)} found, {qualifying_count} qualifying"
        )


async def _process_job_application(user_id: int, job_id: int):
    """Async implementation of job application processing."""
    async with AsyncSessionLocal() as session:
        # 1. Load user and job
        user_result = await session.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            logger.error(f"User {user_id} not found")
            return

        job_result = await session.execute(select(Job).where(Job.id == job_id))
        job = job_result.scalar_one_or_none()
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        # 2. Check if application already exists
        existing = await session.execute(
            select(Application).where(
                Application.user_id == user_id,
                Application.job_id == job_id,
            )
        )
        if existing.scalar_one_or_none():
            logger.info(f"Application already exists for user {user_id}, job {job_id}")
            return

        user_profile = _user_to_dict(user)
        job_dict = _job_to_dict(job)

        # Build JD analysis from stored job data
        try:
            required_skills = json.loads(job.required_skills) if job.required_skills else []
        except (json.JSONDecodeError, TypeError):
            required_skills = []

        try:
            keywords = json.loads(job.keywords) if job.keywords else []
        except (json.JSONDecodeError, TypeError):
            keywords = []

        jd_analysis = {
            "required_skills": required_skills,
            "keywords": keywords,
            "experience_years": job.experience_required or 0,
            "seniority_level": job.seniority_level or "mid",
            "nice_to_have_skills": [],
            "responsibilities": [],
            "tech_stack": required_skills,
        }

        # 3. Personalize resume
        resume_data = await personalize_resume(user_profile, jd_analysis, job_dict)

        # 4. Generate PDF
        # FIX HIGH-05: Use settings.RESUME_STORAGE_PATH instead of hardcoded /app
        output_path = os.path.join(settings.RESUME_STORAGE_PATH, f"{user_id}_{job_id}.pdf")
        generate_resume_pdf(resume_data, user_profile, output_path)

        # 5. Generate cover letter
        cover_letter_text = await generate_cover_letter(user_profile, job_dict, jd_analysis)

        # 6. Find contact
        contact_result = await find_contact(
            job.company or "", job.job_url or ""
        )

        # Score match for the record
        match_result = await score_match(user_profile, jd_analysis)
        match_score_val = match_result.get("overall_score", 0)

        # 7. Create Application record
        application = Application(
            user_id=user_id,
            job_id=job_id,
            status="pending",
            match_score=float(match_score_val),
            resume_version=output_path,
            cover_letter_text=cover_letter_text,
        )
        session.add(application)

        try:
            await session.flush()  # Flush to catch UniqueConstraint violations early
        except IntegrityError:
            # FIX HIGH-04: Handle race condition where another worker inserted first
            logger.warning(
                f"Duplicate application detected (race condition) for user {user_id}, job {job_id}"
            )
            await session.rollback()
            return

        careers_email = contact_result.get("careers_email")

        # Persist found contact to job record for follow-up emails
        if careers_email and not job.careers_email:
            job.careers_email = careers_email

        if careers_email:
            # 8. Contact found - send outreach email
            email_body = await generate_outreach_email(
                user_profile, job_dict, jd_analysis, attempt=0
            )
            email_subject = (
                f"Application for {job.title} - {user.full_name or user.email}"
            )

            # FIX HIGH-02: Handle email send failure gracefully — don't set
            # "outreach_sent" status if the email never actually sent.
            try:
                email_result = send_email(
                    to=careers_email,
                    subject=email_subject,
                    body=email_body,
                    attachment_path=output_path,
                )

                # Store thread_id immediately after first email send
                application.status = "outreach_sent"
                application.thread_id = email_result.get("threadId")
                application.last_email_sent_at = datetime.now(timezone.utc)

                # Schedule follow-up
                eta = datetime.now(timezone.utc) + timedelta(days=5)
                followup_task = send_followup_email.apply_async(
                    args=[application.id, 1], eta=eta
                )
                application.celery_task_id = followup_task.id
                application.followup_due_at = eta

            except Exception as email_exc:
                logger.error(
                    f"Email send failed for application {application.id} "
                    f"(user={user_id}, job={job_id}): {email_exc}"
                )
                # Fall back to marking as applied with error note
                application.status = "applied"
                application.applied_at = datetime.now(timezone.utc)
                application.notes = f"Email send failed: {str(email_exc)}"
        else:
            # 9. No contact - try auto-apply
            apply_result = await auto_apply(
                job.apply_url or job.job_url or "",
                user_profile,
                output_path,
                cover_letter_text,
            )
            application.status = "applied"
            application.applied_at = datetime.now(timezone.utc)
            application.notes = apply_result.get("message", "")

        # 10. Commit
        await session.commit()
        logger.info(
            f"Processed application for user {user_id}, job {job_id}: "
            f"status={application.status}"
        )


async def _send_followup_email(application_id: int, attempt: int):
    """Async implementation of follow-up email task."""
    async with AsyncSessionLocal() as session:
        # 1. Load application
        result = await session.execute(
            select(Application).where(Application.id == application_id)
        )
        application = result.scalar_one_or_none()
        if not application:
            logger.error(f"Application {application_id} not found")
            return

        # 2. Check if we should stop
        terminal_statuses = [
            "interview_scheduled",
            "rejected",
            "selected",
            "withdrawn",
        ]
        if application.status in terminal_statuses:
            logger.info(
                f"Application {application_id} is in terminal status "
                f"{application.status}, skipping follow-up"
            )
            return

        # 3. Load job and user
        user_result = await session.execute(
            select(User).where(User.id == application.user_id)
        )
        user = user_result.scalar_one_or_none()

        job_result = await session.execute(
            select(Job).where(Job.id == application.job_id)
        )
        job = job_result.scalar_one_or_none()

        if not user or not job:
            logger.error("User or job not found for follow-up")
            return

        user_profile = _user_to_dict(user)
        job_dict = _job_to_dict(job)

        # Build JD analysis from stored data
        try:
            required_skills = json.loads(job.required_skills) if job.required_skills else []
        except (json.JSONDecodeError, TypeError):
            required_skills = []

        jd_analysis = {
            "required_skills": required_skills,
            "keywords": [],
            "experience_years": job.experience_required or 0,
            "seniority_level": job.seniority_level or "mid",
            "nice_to_have_skills": [],
            "responsibilities": [],
            "tech_stack": required_skills,
        }

        # 4. Generate follow-up email
        body = await generate_outreach_email(
            user_profile, job_dict, jd_analysis, attempt=attempt
        )

        # 5. Send email
        contact_email = job.careers_email or job.recruiter_email
        if not contact_email:
            logger.warning(f"No contact email for follow-up on application {application_id}")
            return

        email_subject = (
            f"Re: Application for {job.title} - {user.full_name or user.email}"
        )
        send_email(
            to=contact_email,
            subject=email_subject,
            body=body,
            thread_id=application.thread_id,
        )

        # 6. Update application
        application.followup_count = (application.followup_count or 0) + 1
        application.last_email_sent_at = datetime.now(timezone.utc)

        if attempt < 2:
            # 7. Schedule next follow-up (never schedule attempt=3)
            eta = datetime.now(timezone.utc) + timedelta(days=5)
            next_task = send_followup_email.apply_async(
                args=[application_id, attempt + 1], eta=eta
            )
            application.celery_task_id = next_task.id
            application.followup_due_at = eta

        if attempt == 2:
            # 8. Final follow-up - mark as no_reply
            application.status = "no_reply"

        # 9. Commit
        await session.commit()
        logger.info(
            f"Sent follow-up #{attempt} for application {application_id}"
        )


async def _poll_all_replies():
    """Async implementation of reply polling task."""
    async with AsyncSessionLocal() as session:
        # FIX HIGH-01: Poll BOTH "outreach_sent" AND "applied" applications.
        # Previously only "outreach_sent" was polled, missing replies to
        # applications submitted via auto-apply (which get status "applied").
        result = await session.execute(
            select(Application).where(
                Application.status.in_(["outreach_sent", "applied"]),
                Application.thread_id.isnot(None),
            )
        )
        applications = result.scalars().all()

        total_checked = len(applications)
        total_replies = 0

        for application in applications:
            # FIX HIGH-09: Wrap each application's polling in try/except so that
            # a Gmail API error on one application doesn't abort the entire loop.
            try:
                # 2a. Check for replies
                reply_text = get_latest_reply_text(application.thread_id)

                if reply_text:
                    # 2b. Classify the reply
                    classified_status = await classify_reply(reply_text)
                    application.status = classified_status
                    application.response_received_at = datetime.now(timezone.utc)

                    # Revoke scheduled follow-up if exists
                    if application.celery_task_id:
                        celery_app.control.revoke(
                            application.celery_task_id, terminate=True
                        )

                    await session.commit()
                    total_replies += 1

            except Exception as poll_exc:
                logger.error(
                    f"Failed to poll reply for application {application.id}: {poll_exc}"
                )
                # Continue processing remaining applications
                continue

        logger.info(
            f"Reply polling complete: {total_checked} checked, "
            f"{total_replies} replies found"
        )


# --- Celery Task Definitions ---
# FIX MED-09: Added max_retries=3 and default_retry_delay=60s to all tasks
# to prevent infinite retry loops on persistent failures.

@celery_app.task(name="tasks.run_job_discovery", max_retries=3, default_retry_delay=60)
def run_job_discovery(user_id: int):
    """Discover and process matching jobs for a user."""
    asyncio.run(_run_job_discovery(user_id))


@celery_app.task(name="tasks.process_job_application", max_retries=3, default_retry_delay=60)
def process_job_application(user_id: int, job_id: int):
    """Process a single job application."""
    asyncio.run(_process_job_application(user_id, job_id))


@celery_app.task(name="tasks.send_followup_email", max_retries=3, default_retry_delay=60)
def send_followup_email(application_id: int, attempt: int):
    """Send a follow-up email for an application."""
    asyncio.run(_send_followup_email(application_id, attempt))


@celery_app.task(name="tasks.poll_all_replies", max_retries=3, default_retry_delay=60)
def poll_all_replies():
    """Poll all outreach_sent and applied applications for replies."""
    asyncio.run(_poll_all_replies())
