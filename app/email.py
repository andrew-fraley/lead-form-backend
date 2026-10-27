'''
NAME: email.py
PURPOSE: Handle email notifications with lead data for site owners.
DATE: 09-10-2026
'''
import os
import html
import resend
from app import config

# Read email settings from the environment loaded by app.config
API_KEY = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")

# raise RuntimeError if required settings are missing.
if not API_KEY:
    raise RuntimeError("RESEND_API_KEY is not configured.")

if not EMAIL_FROM:
    raise RuntimeError("EMAIL_FROM is not configured.")

# To account for type errors, transform these values into strings.
email_from: str = EMAIL_FROM

# Give the Resend SDK the API key it uses for requests
resend.api_key = API_KEY

# Send a notification email for a newly saved lead.
async def send_lead_notification(
    to_email: str,       # Email address of the site owner.
    name: str | None,    # Lead's name; may be None.
    email: str,          # Lead's email address; required.
    phone: str | None,   # Phone number; may be None.
    message: str | None, # Message; may be None.
    page_url: str | None, # Page the form was submitted on.
    form_context: str | None, # Context of the site section the form was submitted on.
) -> str:  # -> str means this function returns a string.
    """Send an email notification and return its Resend ID."""
    # Escape submitted text before placing it in HTML.
    # "or" supplies fallback text when a value is None or empty.
    safe_name = html.escape(name or "Not provided")
    safe_email = html.escape(email)
    safe_phone = html.escape(phone or "Not provided")
    safe_message = html.escape(message or "Not provided")
    safe_page_url = html.escape(page_url or "Not provided")
    safe_context = html.escape(form_context or "Not provided")

    # Convert newline characters into HTML line breaks for readability.
    safe_message = safe_message.replace("\n", "<br>")

    # Define and format the email to be sent with the data.
    # This dictionary contains the fields Resend needs to send the email.
    # The type annotation enables editor autocomplete and type checking.
    params: resend.Emails.SendParams = {
            "from": email_from, # the .env defined domain I have for sending notifs
            "to": [to_email], # the site owner's email
            "reply_to": email, # the leads submitted email
            "subject": "New website lead received",
            "html": f"""
                <h2>New lead submission</h2>
                <p><strong>Name:</strong> {safe_name}</p>
                <p><strong>Email:</strong> {safe_email}</p>
                <p><strong>Phone:</strong> {safe_phone}</p>
                <p><strong>Message:</strong> {safe_message}</p>
                <p><strong>Page:</strong> {safe_page_url}</p>
                <p><strong>Form context:</strong> {safe_context}</p>
            """,
            # Plain-text alternative for email clients that don't use HTML.
            "text": (
                f"New lead submission\n\n"
                f"Name: {name or 'Not provided'}\n"
                f"Email: {email}\n"
                f"Phone: {phone or 'Not provided'}\n"
                f"Message: {message or 'Not provided'}\n"
                f"Page: {page_url or 'Not provided'}\n"
                f"Form context: {form_context or 'Not provided'}"
            ),
        }

    # await waits for the asynchronous API request to finish.
    # The result contains the ID returned by Resend.
    result = await resend.Emails.send_async(params)

    return result["id"]
