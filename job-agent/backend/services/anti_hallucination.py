import json
from typing import List


def validate_resume(generated: dict, source_profile: dict) -> dict:
    """Validate generated resume data against source profile to prevent hallucination.

    Removes any skills or experience entries not present in the source profile.
    """
    validation_warnings: List[str] = []

    # Parse source skills
    source_skills_raw = source_profile.get("skills", "[]")
    if isinstance(source_skills_raw, str):
        try:
            source_skills = json.loads(source_skills_raw)
        except (json.JSONDecodeError, TypeError):
            source_skills = []
    else:
        source_skills = source_skills_raw if source_skills_raw else []

    source_skills_lower = [s.lower().strip() for s in source_skills]

    # Validate skills_ordered
    if "skills_ordered" in generated:
        cleaned_skills = []
        for skill in generated["skills_ordered"]:
            if skill.lower().strip() in source_skills_lower:
                cleaned_skills.append(skill)
            else:
                validation_warnings.append(
                    f"Removed hallucinated skill: '{skill}'"
                )
        generated["skills_ordered"] = cleaned_skills

    # Parse source experience
    source_experience_raw = source_profile.get("experience", "[]")
    if isinstance(source_experience_raw, str):
        try:
            source_experience = json.loads(source_experience_raw)
        except (json.JSONDecodeError, TypeError):
            source_experience = []
    else:
        source_experience = source_experience_raw if source_experience_raw else []

    source_titles_lower = []
    for exp in source_experience:
        if isinstance(exp, dict) and "title" in exp:
            source_titles_lower.append(exp["title"].lower().strip())
        elif isinstance(exp, str):
            source_titles_lower.append(exp.lower().strip())

    # Validate experience entries
    if "experience" in generated:
        cleaned_experience = []
        for entry in generated["experience"]:
            entry_title = entry.get("title", "").lower().strip()
            if entry_title in source_titles_lower:
                cleaned_experience.append(entry)
            else:
                validation_warnings.append(
                    f"Removed hallucinated experience: '{entry.get('title', 'unknown')}'"
                )
        generated["experience"] = cleaned_experience

    generated["validation_warnings"] = validation_warnings
    return generated
