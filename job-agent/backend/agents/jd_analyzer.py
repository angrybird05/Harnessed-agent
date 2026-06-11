from backend.services.gemini import gemini


async def analyze_jd(job_description: str) -> dict:
    """Analyze a job description and extract structured information.

    Returns JSON with keys:
        required_skills: list[str]
        nice_to_have_skills: list[str]
        keywords: list[str]
        experience_years: int
        seniority_level: str  (junior|mid|senior|lead)
        responsibilities: list[str] max 5 items
        tech_stack: list[str]
    """
    prompt = f"""Analyze the following job description and extract structured information.

Return a JSON object with EXACTLY these keys:
- "required_skills": a list of strings of required technical and soft skills
- "nice_to_have_skills": a list of strings of preferred/nice-to-have skills
- "keywords": a list of strings of important keywords from the job description
- "experience_years": an integer representing minimum years of experience required (0 if not specified)
- "seniority_level": a string, one of: "junior", "mid", "senior", "lead"
- "responsibilities": a list of strings of key responsibilities, maximum 5 items
- "tech_stack": a list of strings of technologies/frameworks/tools mentioned

Job Description:
{job_description}
"""
    result = await gemini.generate_json(prompt)

    # Ensure all required keys exist with correct types
    result.setdefault("required_skills", [])
    result.setdefault("nice_to_have_skills", [])
    result.setdefault("keywords", [])
    result.setdefault("experience_years", 0)
    result.setdefault("seniority_level", "mid")
    result.setdefault("responsibilities", [])
    result.setdefault("tech_stack", [])

    # Enforce max 5 responsibilities
    result["responsibilities"] = result["responsibilities"][:5]

    return result
