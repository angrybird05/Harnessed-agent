from typing import List


def deduplicate_jobs(jobs: List[dict]) -> List[dict]:
    """Deduplicate jobs by external_id first, then by normalized title+company.

    FIX MED-01: external_id is the authoritative unique identifier from the source
    API. Using title+company only as a fallback prevents dropping legitimate jobs
    with the same company/title but different IDs (e.g., different locations).
    """
    seen = set()
    unique_jobs = []

    for job in jobs:
        external_id = job.get("external_id")
        title = job.get("title", "").lower().strip()
        company = job.get("company", "").lower().strip()

        # Prefer external_id as primary key; fall back to title+company for
        # sources that don't provide stable external IDs.
        key = external_id if external_id else f"{title}_{company}"

        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

    return unique_jobs
