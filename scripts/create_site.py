"""
NAME: create_site.py
PURPOSE: CLI script for adding a new website/client to the sites table.
USAGE:python scripts/create_site.py
DATE: 07-10-2026
"""
from app.db_functions import create_sites


def main():
    # Ask for the site information through the terminal.
    site_key = input("Input a site_key (example: examplesbiz-site-key): ")
    site_name = input("Input the site name: ")
    domain = input("Input the domain (example: examplebiz.com): ")
    notification_email = input("Input the notification email: ")

    # Add the site to the database.
    site_id = create_sites(
        site_key,
        site_name,
        domain,
        notification_email
    )

    print(f"\nSite created successfully. Site ID: {site_id}")


if __name__ == "__main__":
    main()
