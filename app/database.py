'''
NAME: database.py
PURPOSE:
- Opens SQLite connection
- Creates lead-form-database.db on first run
- Defines core schema for MVP
STRUCTURE:
    - lead-form-submission      → form submission data (mutable)
Date: 07-10-2026
'''
import sqlite3
from app.config import DB_PATH

def get_connection():
    # create and return a connection to the SQLite databse
    connection = sqlite3.connect(DB_PATH)
    # enable foreign-key enforcement for this connection
    # this allows for relationships to be made between tables
    connection.execute("PRAGMA foreign_keys = ON")

    return connection
    

def init_db():
    # create the databsae tables if they do not already exist
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sites (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               site_key TEXT NOT NULL UNIQUE,
               site_name TEXT NOT NULL,
               domain TEXT NOT NULL,
               notification_email TEXT NOT NULL,
               active INTEGER NOT NULL DEFAULT 1,
               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )

        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lead_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id INTEGER NOT NULL, 
                name TEXT,
                email TEXT NOT NULL,
                phone TEXT,
                message TEXT,
                page_url TEXT,
                form_context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notification_status TEXT NOT NULL DEFAULT 'pending',
                notification_attempted_at TIMESTAMP,
                notification_error TEXT,

                FOREIGN KEY (site_id) REFERENCES sites(id)
            )
        """)

        connection.commit()
    
    finally:
        connection.close()
