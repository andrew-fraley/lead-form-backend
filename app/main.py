# main.py
'''
NAME: main.py
PURPOSE: boots the FastAPI server, imports and registers all routes
Date: 07-10-2026
'''
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.database import init_db
from app.models import LeadCreate, SubmissionResponse
from app.db_functions import (
        create_lead_submission,
        get_site_by_key,
        update_notification_status,
        )
from app.email import send_lead_notification
from app.logging_config import configure_logging
from app.config import CORS_ORIGINS

# Set up the application's logging system:
# create the log directory and configure file and terminal output.
configure_logging()

# Gives the code a logger Python object it can use in this Python module
# __name__ contains the current Python module's name (e.g. app.main).
logger = logging.getLogger(__name__)

@asynccontextmanager #this lets you define what should run when the app starts and stops
async def lifespan(app: FastAPI):
    #Startup Code: this runs when the app starts
    init_db() #initialize your database
    # Record successful database initialization in the terminal and log file.
    logger.info("Database initialized")
    yield #yield control to let the app run

# Create FastAPI application
app = FastAPI(lifespan=lifespan) #create FastAPI app, tell to use lifespan func (startup/shutdown)

# Allow the Hugo development server to send requests to the API.
app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=False,
        allow_methods=["POST"],
        allow_headers=["Content-Type"],
        )

# Simple test endpoint
@app.get("/")
async def root():
    return {"message": "Lead-form backend is working!"}


# POST endpoint for receiving form data
@app.post("/leads", response_model=SubmissionResponse)
async def form_submission(lead: LeadCreate):
    # Reject submissions with a value in honeypot field
    # honeypot is part of LeadCreate but not part of create_lead_submission()
    # function so it never gets stored in the database
    if lead.honeypot:
        logger.warning("Honeypot triggered for site %s", lead.site_key)
        # return a success to the bots
        return {
                "success": True,
                "message": "Lead submitted successfully."
                }

    # Find the website this lead belongs to.
    site = get_site_by_key(lead.site_key)

    # Return response
    if site is None:
        logger.warning("Invalid site key: %s", lead.site_key)
        # Return an HTTP 403 when the submitted site does not exist.
        raise HTTPException(
                status_code=403, #403 becuase the site exists but is not permitted
                                 # to submit leads
                detail="Invalid site."
                )
    
    # site[5] is the value of the site table in the databse that has the active 
    # (value 1 for true) or inactive (value 0 for false) site state value saved in it.
    # this checks if the site is true (active) or false (inactive)
    if not site[5]:
        logger.warning(
                "Submission attempted for inactive site: %s",
                lead.site_key
                )
        # Reject submission from an inactive website.
        raise HTTPException(
                status_code=403,
                detail="Site is inactive"
                )

    # site[0] is the site's database ID.
    # save the lead first and capture its database ID
    submission_id = create_lead_submission(site[0], lead)

    logger.info(
            "Lead submitted %s saved for site: %s",
            submission_id,
            lead.site_key
            )

    # Notify the site owner without losing the saved lead if email fails.
    try:
        email_id = await send_lead_notification(
                to_email=site[4],
                name=lead.name,
                email=str(lead.email),
                phone=lead.phone,
                message=lead.message,
                page_url=lead.page_url,
                form_context=lead.form_context,
        )

    # catches most standard Python exceptions and stores the exception object in 
    # the variable exc
    except Exception as exc:
        # The lead is safe in SQLite even though the email failed.
        logger.exception(
                "Email notification failed for submission %s",
                submission_id
                )
        # Try to update the email notification status for lead_submissions
        try:
            update_notification_status(
                    submission_id,
                    "failed",
                    str(exc)[:1000]
                    )
        except Exception:
            logger.exception(
                    "Could not record notification failure for submission %s",
                    submission_id
                    )
    else:
        # Record success separately from the email request itself.
        try:
            update_notification_status(submission_id, "accepted")
            logger.info(
                    "Email notification accepted for submission %s; Resend ID: %s",
                    submission_id,
                    email_id
                    )
        except Exception:
            logger.exception(
                    "Email was accepted but its status could not be recorded "
                    "for submission %s",
                    submission_id
                    )

    return {"success": True, "message": "Lead submitted successfully."}
