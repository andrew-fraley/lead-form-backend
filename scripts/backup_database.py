"""
NAME: backup_database.py
PURPOSE: Create a consistent backup of the SQLite database.
DATE: 09-10-2026
"""
import sqlite3
from datetime import datetime
from pathlib import Path

from app.config import DB_PATH

# Store backups in a dedicated folder in the project root.
BACKUP_DIR = Path(DB_PATH).parent / "backups"

def backup_database():
    # Stop if the source database does not exist.
    source_path = Path(DB_PATH)

    if not source_path.exists():
        raise FileNotFoundError(f"Database not found: {source_path}")

    # Create the backup folder if it does not exist.
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # Give each backup a timestamped filename.
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = BACKUP_DIR / f"lead-form-database_{timestamp}.db"

    # SQLite's backup API safely copies a database while it is in use.
    with sqlite3.connect(source_path) as source:
        with sqlite3.connect(backup_path) as destination:
            source.backup(destination)

    print(f"Database backup created: {backup_path}")

if __name__ == "__main__":
    backup_database()
