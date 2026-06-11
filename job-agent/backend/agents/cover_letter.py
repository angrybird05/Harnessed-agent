from backend.services.gemini import gemini


async def generate_cover_letter(
    user_profile: dict, job: dict, jd_analysis: dict
) -> str:
    """Generate a professional cover letter for a job application.

    Returns plain text string, 3 paragraphs, max 250 words.
    """
    prompt = f"""Write a professional cover letter for a job application.

User Profile:
Name: {user_profile.get('full_name', '')}
Skills: {user_profile.get('skills', '[]')}
Experience: {user_profile.get('experience', '[]')}
Projects: {user_profile.get('projects', '[]')}
Years of Experience: {user_profile.get('years_of_experience', 0)}

Job Details:
Title: {job.get('title', '')}
Company: {job.get('company', '')}
Location: {job.get('location', '')}

Job Analysis:
Required Skills: {jd_analysis.get('required_skills', [])}
Responsibilities: {jd_analysis.get('responsibilities', [])}
Tech Stack: {jd_analysis.get('tech_stack', [])}

Requirements:
- Write EXACTLY 3 paragraphs:
  1. Why this company and role excites you (specific to the company and position)
  2. Your strongest proof point — a concrete achievement or project that demonstrates your fit
  3. A confident call to action
- Maximum 250 words total
- Tone: professional and confident
- Do NOT start with "I am writing to apply"
- Do NOT use the phrase "I hope this email finds you well"
- Use the candidate's actual skills and experience only
- Be specific and avoid generic statements

Return ONLY the cover letter text, no JSON formatting.
"""
    result = await gemini.generate_text(prompt)
    return result.strip()
