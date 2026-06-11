from backend.services.gemini import gemini


async def generate_outreach_email(
    user_profile: dict,
    job: dict,
    jd_analysis: dict,
    attempt: int,
) -> str:
    """Generate outreach email body based on attempt number.

    attempt=0: initial cold email, max 150 words, 3 paragraphs
    attempt=1: follow-up day 5, max 80 words, 2 paragraphs, warm tone
    attempt=2: final follow-up day 10, max 50 words, 2 sentences, gracious tone

    Returns plain text email body.
    """
    user_name = user_profile.get("full_name", "")
    job_title = job.get("title", "")
    company = job.get("company", "")
    skills = user_profile.get("skills", "[]")

    if attempt == 0:
        prompt = f"""Write a cold outreach email for a job application.

Candidate: {user_name}
Target Role: {job_title}
Company: {company}
Key Skills: {skills}
Required Skills for Role: {jd_analysis.get('required_skills', [])}

Requirements:
- Maximum 150 words
- Exactly 3 paragraphs:
  1. Brief introduction and the specific role you're interested in
  2. Your most relevant qualification or achievement
  3. Clear call to action requesting a conversation
- Professional but personable tone
- Do NOT use "I hope this email finds you well"
- Do NOT start with "I am writing to apply"
- Be specific about why you're a good fit

Return ONLY the email body text.
"""
    elif attempt == 1:
        prompt = f"""Write a follow-up email for a job application (first follow-up, sent 5 days after initial email).

Candidate: {user_name}
Target Role: {job_title}
Company: {company}

Requirements:
- Maximum 80 words
- Exactly 2 paragraphs:
  1. Brief reference to your previous email about the {job_title} role
  2. Reiterate interest and offer to provide additional information
- Warm and respectful tone
- Do NOT be pushy or desperate
- Do NOT use "I hope this email finds you well"

Return ONLY the email body text.
"""
    elif attempt == 2:
        prompt = f"""Write a final follow-up email for a job application (second and last follow-up).

Candidate: {user_name}
Target Role: {job_title}
Company: {company}

Requirements:
- Maximum 50 words
- Exactly 2 sentences:
  1. Acknowledge this is your final follow-up regarding the {job_title} position
  2. Express gratitude for their time and leave the door open
- Gracious and professional tone
- Do NOT be pushy

Return ONLY the email body text.
"""
    else:
        return ""

    result = await gemini.generate_text(prompt)
    return result.strip()
