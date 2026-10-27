"""
NAME: config.py
PURPOSE: Application configuration
DATE: 07-10-2026
"""
import os
from dotenv import load_dotenv

# Project root: lead-form-backend/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from the project's .env file.
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

# SQLite database lives in the project root.
DB_PATH = os.path.join(BASE_DIR, "lead-form-database.db")

# Read allowed browser origins from .env
# Separate multiple origins with commas.
CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:1313"
            ).split(",")
        if origin.strip()
        ]
