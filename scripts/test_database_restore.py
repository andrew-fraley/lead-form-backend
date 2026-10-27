"""
NAME: test_database_restore.py
PURPOSE: Test a database backup without changing the working database.
DATE: 10-10-2026
"""
import sqlite3
import sys
from pathlib import Path
from contextlib import closing

from app.config import BASE_DIR

def test_restore(backup_path):
    # Convert the supplied path into an absolute path and check that it exists.
    backup_path = Path(backup_path).resolve()

    if not backup_path.is_file():
        raise FileNotFoundError(f"Backup not found: {backup_path}")

    # Restore into a separate file so the working database stays untouched.
    # This test file must not already exist, to avoid overwritting previous data.
    restore_path = Path(BASE_DIR) / "restore-test.db"

    if restore_path.exists():
        raise FileExistsError(
                f"{restore_path} already exists. Inspect or remove it first."
                )
    
    # Use SQLite's backup API to copy the backup into the test database.
    # The source is the backup file; the destination is the new test file.
    with closing(sqlite3.connect(backup_path)) as source:
        with closing(sqlite3.connect(restore_path)) as destination:
            source.backup(destination)

    # Open the restored database so we can run checks against it.
    connection = sqlite3.connect(restore_path)

    try:
        # Check whether SQLite considers the database structurally sound.
        # A result of "ok" means the integrity check passed.
        result = connection.execute("PRAGMA integrity_check").fetchone()[0]

        if result != "ok":
            raise RuntimeError(f"Integrity check failed: {result}")

        # Read the names of all tables recorded in SQLite's internal schema.
        # A set makes it easy to compare the tables found with those required.
        tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                    )
                }

        # Confirm that the restored database has both core application tables.
        expected_tables = {"sites", "lead_submissions"}

        if not expected_tables.issubset(tables):
            raise RuntimeError(f"Missing tables: {expected_tables - tables}")

        # COUNT(*) returns the number of rows in each table.
        # fetchone()[0] retrieves the count from the first returned row.
        site_count = connection.execute(
                "SELECT COUNT(*) FROM sites"
                ).fetchone()[0]

        lead_count = connection.execute(
                "SELECT COUNT(*) FROM lead_submissions"
                ).fetchone()[0]

        # Report the results so we can compare them with the backup's contents.
        print("Restore test passed.")
        print(f"Integrity check: {result}")
        print(f"Sites recovered: {site_count}")
        print(f"Leads recovered: {lead_count}")
        print(f"Test database: {restore_path}")

    finally:
        # Close the connection even if one of the checks raise an exception.
        connection.close()

if __name__ == "__main__":
    # sys.argv contains the command-line arguments:
    # [0] is the script/module invocation; [1] should be the backup path.
    if len(sys.argv) != 2:
        raise SystemExit(
                "Usage: python3 -m scripts.test_database_restore PATH_TO_BACKUP"
                )

    # Pass the supplied backup path into the restore-test funciton.
    test_restore(sys.argv[1])
