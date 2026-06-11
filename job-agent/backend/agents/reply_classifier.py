from backend.services.gemini import gemini


async def classify_reply(reply_text: str) -> str:
    """Classify an email reply into a status category.

    Returns one of:
        interview_scheduled | request_for_info | rejected | interested | out_of_office
    """
    prompt = f"""Classify the following email reply into exactly one of these categories:
- "interview_scheduled": The reply indicates an interview has been scheduled or they want to set up an interview
- "request_for_info": The reply asks for additional information, documents, or details
- "rejected": The reply indicates the candidate has been rejected or the position has been filled
- "interested": The reply shows general interest but no specific next steps
- "out_of_office": The reply is an automated out-of-office or vacation message

Email Reply:
{reply_text}

Return a JSON object with exactly one key:
- "status": one of "interview_scheduled", "request_for_info", "rejected", "interested", "out_of_office"
"""
    result = await gemini.generate_json(prompt)
    status = result.get("status", "request_for_info")

    valid_statuses = [
        "interview_scheduled",
        "request_for_info",
        "rejected",
        "interested",
        "out_of_office",
    ]
    if status not in valid_statuses:
        status = "request_for_info"

    return status
