'''
NAME: db_functions.py
PURPOSE: module for all the database operation functions in the app
Date: 07-10-2026
'''
from app.database import get_connection

# I will build out a small python script to use this function to add clients and 
# sites to the databse, no need for an endpoint with this. 
def create_sites(site_key, site_name, domain, notification_email):
    # Add a website to the sites table.
    connection = get_connection()
    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO sites (
                   site_key,
                   site_name,
                   domain, 
                   notification_email
                )
                VALUES (?, ?, ?, ?)
        """, (
            site_key,
            site_name,
            domain,
            notification_email
        ))

        connection.commit()
        # lastrowid gives the ID of the row that was most recently insertd by that cursor
        return cursor.lastrowid 

    finally:
        connection.close()



# Check if the site exists during a lead submission POST
def get_site_by_key(site_key):
    # Find the site that matches the key sent by the frontend
    connection = get_connection()
    try:
        cursor = connection.cursor()
        # Find the site in the database with the site_key
        cursor.execute("""
            SELECT
                       id,
                       site_key,
                       site_name,
                       domain,
                       notification_email,
                       active
            FROM sites
            WHERE site_key = ?
        """, (site_key,))
        
        #site= the entire matching database row (id, site_key, site_name, domain, etc)
        return cursor.fetchone()

    finally:
        connection.close()


# This is a function to INSERT the lead form submission data into the SQLite database
# after validation from the BaseModel (frontend submission > Pydantic > FastAPI calls
# db_function to strucutre and submit to SQLite > email notification sent to client 
# (email notif system will be built after form submissions working)
def create_lead_submission(site_id, lead):
    # Store a lead submission belonging to a specific site.
    connection = get_connection()
    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO lead_submissions (
                       site_id,
                       name,
                       email,
                       phone,
                       message,
                       page_url,
                       form_context,
                       notification_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            site_id,
            lead.name,
            lead.email,
            lead.phone,
            lead.message,
            lead.page_url,
            lead.form_context,
            "pending"
        ))
        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()
    

def update_notification_status(submission_id, status, error=None):
    # Record the latest notification result for this lead.
    connection = get_connection()
    # Try to update lead_submissions table notification data
    try:
        cursor = connection.cursor()
        # updates the table for the lead_submissions with the id in argument
        # with the the current notification status value, and the error value
        cursor.execute("""
                       UPDATE lead_submissions
                       SET 
                        notification_status = ?,
                        notification_attempted_at = CURRENT_TIMESTAMP,
                        notification_error = ?
                       WHERE id = ?
        """, (status, error, submission_id))
        # If no submission with the id is found through the ValueError
        if cursor.rowcount == 0:
            raise ValueError(
                    f"Lead submission {submission_id} was not found."
                    )

        connection.commit()

    finally:
        connection.close()
