from backend.services.gemini import gemini
from backend.services.anti_hallucination import validate_resume


async def personalize_resume(
    user_profile: dict, jd_analysis: dict, job: dict
) -> dict:
    """Generate a personalized resume tailored to a specific job.

    Calls Gemini to generate resume content, then validates against
    the source profile using anti_hallucination.validate_resume().

    Returns JSON with keys:
        summary: str
        skills_ordered: list[str]  (matched skills first)
        experience: list[{title, company, dates, bullets: list[str]}]
        projects: list[{name, description, tech: list[str]}]
        education: list[{degree, institution, year}]
        certifications: list[str]
        validation_warnings: list[str]
    """
    prompt = f"""You are an expert resume writer. Create a personalized resume for a specific job application.

CRITICAL CONSTRAINT: Only use skills, experience, and projects from the user_profile provided. Never add skills or experience not listed in the source profile.

User Profile:
{user_profile}

Job Description Analysis:
{jd_analysis}

Job Details:
Title: {job.get('title', '')}
Company: {job.get('company', '')}
Location: {job.get('location', '')}

Return a JSON object with EXACTLY these keys:
- "summary": a string, a compelling 2-3 sentence professional summary tailored to this role
- "skills_ordered": a list of strings, user's skills reordered with matched/relevant skills first
- "experience": a list of objects, each with keys: "title" (str), "company" (str), "dates" (str), "bullets" (list of strings, 2-4 achievement-focused bullet points tailored to this role)
- "projects": a list of objects, each with keys: "name" (str), "description" (str), "tech" (list of strings)
- "education": a list of objects, each with keys: "degree" (str), "institution" (str), "year" (str)
- "certifications": a list of strings

Remember: ONLY use information from the user profile. Do NOT invent or hallucinate any skills, experience, projects, or certifications.
"""
    result = await gemini.generate_json(prompt)

    # Ensure all required keys exist
    result.setdefault("summary", "")
    result.setdefault("skills_ordered", [])
    result.setdefault("experience", [])
    result.setdefault("projects", [])
    result.setdefault("education", [])
    result.setdefault("certifications", [])

    # Always validate against source profile before returning
    validated = validate_resume(result, user_profile)

    return validated
