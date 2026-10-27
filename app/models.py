'''
NAME: models.py

PURPOSE:
    - define BaseModels for the lead submissions from the frontend

Date: 07-10-2026
'''
from pydantic import BaseModel, EmailStr, Field

# This model describes the data that the API accepts
# basically this describes what a valid lead form submit should look like
class LeadCreate(BaseModel):
    # unique identifier sent with lead to identify the site the form is
    # submitted on for lead ownership purposes.
    site_key: str = Field(max_length=100) 
    # Optional fields (None = ) with reasonable size limits ( Field() )
    name: str | None = Field(default=None, max_length=100)  # name of client
    email: EmailStr = Field(max_length=254) # NOT Optional, email of client
    phone: str | None = Field(default=None, max_length=30) # phone number of client
    message: str | None = Field(default=None, max_length=2000) # message send by client with submission
    page_url: str | None = Field(default=None, max_length=2048) # url of the form submission
    form_context: str | None = Field(default=None, max_length=100) # details about where on the site the form was submitted
    honeypot: str | None = Field(default=None, max_length=100) #hidden field to trick automated form bots from inputting submissions

    #syntax explained: 
    # str | None is the value can be a string or None
    # default=None is the field is Optional
    # max_length=x Pydantic rejects strings longer than x characters


# This model describes what the API sends back
class SubmissionResponse(BaseModel):
    success: bool # true or false
    message: str # message for submission: success, error, failed


#The important concept is:
#
#Pydantic model
#       ↓
#defines the shape of incoming data
#       ↓
#FastAPI validates it automatically
#
#For example, conceptually:
#
#{
#    "name": "John",
#    "email": "john@example.com",
#    "message": "I need a website"
#}
