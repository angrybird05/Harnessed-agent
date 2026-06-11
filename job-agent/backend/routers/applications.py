from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.application import Application, APPLICATION_STATUSES
from backend.models.job import Job
from backend.models.user import User
from backend.schemas.application import ApplicationOut, ApplicationStatusUpdate
from backend.utils.auth import get_current_user
from backend.worker.celery_app import celery_app

router = APIRouter(prefix="/applications", tags=["applications"])


def _build_application_out(application: Application, job: Optional[Job] = None) -> ApplicationOut:
    """Build ApplicationOut from Application and optional Job."""
    data = {
        "id": application.id,
        "user_id": application.user_id,
        "job_id": application.job_id,
        "status": application.status,
        "thread_id": application.thread_id,
        "followup_count": application.followup_count,
        "last_email_sent_at": application.last_email_sent_at,
        "celery_task_id": application.celery_task_id,
        "resume_version": application.resume_version,
        "cover_letter_text": application.cover_letter_text,
        "match_score": application.match_score,
        "applied_at": application.applied_at,
        "followup_due_at": application.followup_due_at,
        "response_received_at": application.response_received_at,
        "notes": application.notes,
        "created_at": application.created_at,
        "updated_at": application.updated_at,
    }
    if job:
        data["job_title"] = job.title
        data["job_company"] = job.company
        data["job_location"] = job.location
        data["job_url"] = job.job_url
        data["is_remote"] = job.is_remote

    return ApplicationOut(**data)


@router.get("", response_model=list[ApplicationOut])
async def get_applications(
    application_status: Optional[str] = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get applications with optional status filter, joined with job data."""
    query = select(Application, Job).outerjoin(
        Job, Application.job_id == Job.id
    ).where(Application.user_id == current_user.id)

    if application_status:
        query = query.where(Application.status == application_status)

    query = query.order_by(Application.created_at.desc()).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    return [_build_application_out(app, job) for app, job in rows]


@router.get("/{application_id}", response_model=ApplicationOut)
async def get_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single application with job details."""
    result = await db.execute(
        select(Application, Job)
        .outerjoin(Job, Application.job_id == Job.id)
        .where(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
    )
    row = result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    app, job = row
    return _build_application_out(app, job)


@router.patch("/{application_id}/status", response_model=ApplicationOut)
async def update_application_status(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update application status. Validates against 9 valid status values."""
    result = await db.execute(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
    )
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    application.status = status_update.status
    await db.commit()
    await db.refresh(application)

    # Fetch job for response
    job_result = await db.execute(select(Job).where(Job.id == application.job_id))
    job = job_result.scalar_one_or_none()

    return _build_application_out(application, job)


@router.post("/{application_id}/withdraw", response_model=ApplicationOut)
async def withdraw_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Withdraw an application. Revokes any scheduled Celery tasks."""
    result = await db.execute(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
    )
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # Revoke celery_task_id if exists
    if application.celery_task_id:
        celery_app.control.revoke(application.celery_task_id, terminate=True)

    application.status = "withdrawn"
    await db.commit()
    await db.refresh(application)

    # Fetch job for response
    job_result = await db.execute(select(Job).where(Job.id == application.job_id))
    job = job_result.scalar_one_or_none()

    return _build_application_out(application, job)
