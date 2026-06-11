from urllib.parse import urlparse
from backend.services.gemini import gemini


async def find_contact(company: str, job_url: str) -> dict:
    """Find contact email for a company using LLM inference.

    Extracts domain from job_url and asks Gemini for the most likely
    public careers email.

    Returns:
        {careers_email: str, source: 'llm_inference'} if confidence is 'high'
        {careers_email: None, source: 'none_found'} otherwise
    """
    parsed = urlparse(job_url)
    domain = parsed.netloc if parsed.netloc else parsed.path.split("/")[0]

    # Remove www. prefix if present
    if domain.startswith("www."):
        domain = domain[4:]

    prompt = f"""What is the most likely public careers or recruiting email address for the company "{company}" with domain "{domain}"?

Return a JSON object with EXACTLY these keys:
- "careers_email": the email address as a string, or null if you cannot determine one
- "confidence": one of "high", "medium", or "low"

Only return "high" confidence if you are very certain the email is correct and commonly used.
Common patterns include: careers@domain, recruiting@domain, jobs@domain, hr@domain, talent@domain.
"""
    result = await gemini.generate_json(prompt)

    careers_email = result.get("careers_email")
    confidence = result.get("confidence", "low")

    if confidence == "high" and careers_email:
        return {"careers_email": careers_email, "source": "llm_inference"}
    else:
        return {"careers_email": None, "source": "none_found"}
