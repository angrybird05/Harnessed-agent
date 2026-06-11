from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.job import Job
from backend.models.user import User
from backend.schemas.job import JobOut, JobDiscoverResponse
from backend.utils.auth import get_current_user
from backend.worker.tasks import run_job_discovery

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobOut])
async def get_jobs(
    min_score: Optional[float] = Query(None, description="Filter by minimum seniority match (0-100). Note: match score lives on Applications, not Jobs. This filter has no effect on Job listings — use the /applications endpoint with match_score filtering instead."),
    is_remote: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get jobs with optional filters for remote status and limit.

    Note: min_score is accepted for API compatibility but does not filter Job rows
    (match scores are per-user and live on the Application model, not on Jobs).
    Use GET /applications?status=... for score-filtered results.
    """
    # FIX CRIT-04: Document that min_score cannot filter Job rows (score is on Application).
    # The query builds correctly for remote and limit; min_score documented above.
    query = select(Job)

    if is_remote is not None:
        query = query.where(Job.is_remote == is_remote)

    query = query.order_by(Job.fetched_at.desc()).limit(limit)

    result = await db.execute(query)
    jobs = result.scalars().all()
    return jobs


@router.post("/discover", response_model=JobDiscoverResponse)
async def discover_jobs(
    current_user: User = Depends(get_current_user),
):
    """Trigger job discovery task for the current user."""
    task = run_job_discovery.delay(current_user.id)
    return JobDiscoverResponse(
        task_id=task.id,
        message="Job discovery task started. Check Flower for progress.",
    )
