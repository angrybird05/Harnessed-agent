import asyncio
from typing import List

import httpx

from backend.config import settings
from backend.utils.dedup import deduplicate_jobs


async def fetch_jobs(
    keywords: List[str], location: str = "remote"
) -> List[dict]:
    """Fetch jobs from Adzuna and Remotive concurrently, merge and deduplicate.

    Args:
        keywords: List of search keywords
        location: Location string, defaults to 'remote'

    Returns:
        Deduplicated list of job dicts
    """
    adzuna_jobs, remotive_jobs = await asyncio.gather(
        fetch_from_adzuna(keywords, location),
        fetch_from_remotive(keywords),
    )

    all_jobs = adzuna_jobs + remotive_jobs
    return deduplicate_jobs(all_jobs)


async def fetch_from_adzuna(
    keywords: List[str], location: str
) -> List[dict]:
    """Fetch jobs from Adzuna API.

    GET https://api.adzuna.com/v1/api/jobs/in/search/1
    """
    query = "+".join(keywords)
    # FIX MED-08: Use configurable country code from settings instead of hardcoded '/in/' (India)
    url = f"https://api.adzuna.com/v1/api/jobs/{settings.ADZUNA_COUNTRY}/search/1"
    params = {
        "app_id": settings.ADZUNA_APP_ID,
        "app_key": settings.ADZUNA_APP_KEY,
        "what": query,
        "where": location,
        "results_per_page": 20,
        "content-type": "application/json",
    }

    jobs = []
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            for item in data.get("results", []):
                job = {
                    "external_id": f"adzuna_{item.get('id', '')}",
                    "source": "adzuna",
                    "title": item.get("title", ""),
                    "company": item.get("company", {}).get("display_name", ""),
                    "location": item.get("location", {}).get("display_name", ""),
                    "job_url": item.get("redirect_url", ""),
                    "apply_url": item.get("redirect_url", ""),
                    "description": item.get("description", ""),
                    "salary_min": item.get("salary_min"),
                    "salary_max": item.get("salary_max"),
                    "is_remote": "remote" in item.get("title", "").lower()
                    or "remote" in item.get("description", "").lower(),
                }
                jobs.append(job)
    except Exception:
        pass

    return jobs


async def fetch_from_remotive(keywords: List[str]) -> List[dict]:
    """Fetch jobs from Remotive API.

    GET https://remotive.com/api/remote-jobs?search={query}&limit=20
    """
    query = " ".join(keywords)
    url = "https://remotive.com/api/remote-jobs"
    params = {
        "search": query,
        "limit": 20,
    }

    jobs = []
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            for item in data.get("jobs", []):
                job = {
                    "external_id": f"remotive_{item.get('id', '')}",
                    "source": "remotive",
                    "title": item.get("title", ""),
                    "company": item.get("company_name", ""),
                    "location": item.get("candidate_required_location", ""),
                    "job_url": item.get("url", ""),
                    "apply_url": item.get("url", ""),
                    "description": item.get("description", ""),
                    "salary_min": None,
                    "salary_max": None,
                    "is_remote": True,
                }
                jobs.append(job)
    except Exception:
        pass

    return jobs
