from backend.services.gemini import gemini


async def score_match(user_profile: dict, jd_analysis: dict) -> dict:
    """Score the match between a user profile and a job description analysis.

    Returns JSON with keys:
        overall_score: int 0-100
        skill_match_score: int 0-100
        experience_match_score: int 0-100
        matched_skills: list[str]
        missing_skills: list[str]
        recommendation: str (strong_match|good_match|weak_match|skip)
    Only recommends applying if overall_score >= 60.
    """
    prompt = f"""You are a job matching expert. Compare the user profile against the job description analysis and score the match.

User Profile:
{user_profile}

Job Description Analysis:
{jd_analysis}

Return a JSON object with EXACTLY these keys:
- "overall_score": integer from 0 to 100 representing overall match quality
- "skill_match_score": integer from 0 to 100 representing how well the user's skills match
- "experience_match_score": integer from 0 to 100 representing how well the user's experience level matches
- "matched_skills": list of strings of skills the user has that match the job requirements
- "missing_skills": list of strings of required skills the user is missing
- "recommendation": a string, one of: "strong_match", "good_match", "weak_match", "skip"

Rules for recommendation:
- If overall_score >= 80: "strong_match"
- If overall_score >= 60: "good_match"
- If overall_score >= 40: "weak_match"
- If overall_score < 40: "skip"
- Only recommend applying (strong_match or good_match) if overall_score >= 60
"""
    result = await gemini.generate_json(prompt)

    # Ensure all required keys exist
    result.setdefault("overall_score", 0)
    result.setdefault("skill_match_score", 0)
    result.setdefault("experience_match_score", 0)
    result.setdefault("matched_skills", [])
    result.setdefault("missing_skills", [])

    # Enforce recommendation logic based on score
    score = result.get("overall_score", 0)
    if score >= 80:
        result["recommendation"] = "strong_match"
    elif score >= 60:
        result["recommendation"] = "good_match"
    elif score >= 40:
        result["recommendation"] = "weak_match"
    else:
        result["recommendation"] = "skip"

    return result
