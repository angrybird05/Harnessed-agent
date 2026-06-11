from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.application import Application
from backend.models.user import User
from backend.utils.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return dashboard statistics for the current user.

    Returns:
        total_applications, outreach_sent, applied_direct, interviews_scheduled,
        rejected, no_reply, response_rate (float 1dp), avg_match_score (float 1dp),
        applications_this_week
    """
    user_id = current_user.id
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)

    # Single aggregated query replacing 8 separate round-trips
    result = await db.execute(
        select(
            func.count(Application.id).label("total_applications"),
            func.sum(
                case((Application.status == "outreach_sent", 1), else_=0)
            ).label("outreach_sent"),
            func.sum(
                case((Application.status == "applied", 1), else_=0)
            ).label("applied_direct"),
            func.sum(
                case((Application.status == "interview_scheduled", 1), else_=0)
            ).label("interviews_scheduled"),
            func.sum(
                case((Application.status == "rejected", 1), else_=0)
            ).label("rejected"),
            func.sum(
                case((Application.status == "no_reply", 1), else_=0)
            ).label("no_reply"),
            func.sum(
                case(
                    (Application.status.in_(
                        ["interview_scheduled", "request_for_info", "rejected", "selected"]
                    ), 1),
                    else_=0
                )
            ).label("responded_count"),
            func.avg(Application.match_score).label("avg_match_score"),
            func.sum(
                case((Application.created_at >= week_ago, 1), else_=0)
            ).label("applications_this_week"),
        ).where(Application.user_id == user_id)
    )
    row = result.one()

    total_applications = row.total_applications or 0
    outreach_sent = int(row.outreach_sent or 0)
    applied_direct = int(row.applied_direct or 0)
    interviews_scheduled = int(row.interviews_scheduled or 0)
    rejected = int(row.rejected or 0)
    no_reply = int(row.no_reply or 0)
    responded_count = int(row.responded_count or 0)
    avg_match_score = round(float(row.avg_match_score or 0.0), 1)
    applications_this_week = int(row.applications_this_week or 0)

    response_rate = round(
        (responded_count / total_applications * 100) if total_applications > 0 else 0.0,
        1,
    )

    return {
        "total_applications": total_applications,
        "outreach_sent": outreach_sent,
        "applied_direct": applied_direct,
        "interviews_scheduled": interviews_scheduled,
        "rejected": rejected,
        "no_reply": no_reply,
        "response_rate": response_rate,
        "avg_match_score": avg_match_score,
        "applications_this_week": applications_this_week,
    }
