import base64
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from backend.config import settings

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]


def get_gmail_service():
    """Build and return Gmail API v1 service using OAuth2 credentials."""
    credentials = Credentials(
        token=None,
        refresh_token=settings.GMAIL_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GMAIL_CLIENT_ID,
        client_secret=settings.GMAIL_CLIENT_SECRET,
        scopes=SCOPES,
    )
    service = build("gmail", "v1", credentials=credentials)
    return service


def send_email(
    to: str,
    subject: str,
    body: str,
    attachment_path: Optional[str] = None,
    thread_id: Optional[str] = None,
) -> dict:
    """Send an email via Gmail API, optionally with attachment and thread_id.

    Returns the API result dict containing 'threadId' and 'id'.
    """
    service = get_gmail_service()

    message = MIMEMultipart()
    message["to"] = to
    message["from"] = settings.GMAIL_SENDER_EMAIL
    message["subject"] = subject

    message.attach(MIMEText(body, "plain"))

    if attachment_path and os.path.exists(attachment_path):
        filename = os.path.basename(attachment_path)
        with open(attachment_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        message.attach(part)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    body_payload = {"raw": raw_message}
    if thread_id:
        body_payload["threadId"] = thread_id

    result = (
        service.users()
        .messages()
        .send(userId="me", body=body_payload)
        .execute()
    )
    return result


def get_thread_messages(thread_id: str) -> list:
    """Return all messages in a thread via users().threads().get(format='full')."""
    service = get_gmail_service()
    thread = (
        service.users()
        .threads()
        .get(userId="me", id=thread_id, format="full")
        .execute()
    )
    return thread.get("messages", [])


def get_latest_reply_text(thread_id: str) -> Optional[str]:
    """Get the latest reply text from a thread that is NOT from the sender.

    Returns decoded string, or None if no reply found.
    """
    messages = get_thread_messages(thread_id)

    # Find messages not from us, get the latest
    replies = []
    for msg in messages:
        headers = msg.get("payload", {}).get("headers", [])
        from_header = ""
        for header in headers:
            if header.get("name", "").lower() == "from":
                from_header = header.get("value", "")
                break

        if settings.GMAIL_SENDER_EMAIL not in from_header:
            replies.append(msg)

    if not replies:
        return None

    latest_reply = replies[-1]

    # Decode the text/plain body
    payload = latest_reply.get("payload", {})
    body_data = _extract_text_plain(payload)

    if body_data:
        decoded = base64.urlsafe_b64decode(body_data).decode("utf-8", errors="replace")
        return decoded

    return None


def _extract_text_plain(payload: dict) -> Optional[str]:
    """Recursively extract text/plain body data from message payload."""
    mime_type = payload.get("mimeType", "")

    if mime_type == "text/plain":
        return payload.get("body", {}).get("data")

    parts = payload.get("parts", [])
    for part in parts:
        result = _extract_text_plain(part)
        if result:
            return result

    return None
