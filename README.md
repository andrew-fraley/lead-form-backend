# lead-form-backend

A small FastAPI backend that receives contact/lead form submissions from my websites, saves them to SQLite, and emails the site owner.

One backend serves multiple sites. Each site has a `site_key` that the form sends along with the submission.

## Stack

- Python 3.10
- FastAPI
- SQLite (stdlib `sqlite3`)
- Pydantic for request validation
- Resend for email notifications

## Project layout

```
app/
  main.py            FastAPI app, routes, CORS, startup
  config.py          Loads .env, paths, CORS origins
  database.py        SQLite connection and table creation
  db_functions.py    Insert/select/update queries
  models.py          Pydantic request/response models
  email.py           Resend email notification
  logging_config.py  Console + rotating file logs
scripts/
  create_site.py           Add a site to the database (CLI)
  backup_database.py       Timestamped SQLite backup
  test_database_restore.py Check that a backup restores cleanly
```

## Setup

```bash
git clone https://github.com/andrew-fraley/lead-form-backend.git
cd lead-form-backend

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
```

Edit `.env`:

| Variable         | Description                                          |
|------------------|------------------------------------------------------|
| `RESEND_API_KEY` | Resend API key                                       |
| `EMAIL_FROM`     | Sender address (must be a verified Resend domain)    |
| `CORS_ORIGINS`   | Comma-separated list of allowed origins              |

The app will not start if `RESEND_API_KEY` or `EMAIL_FROM` is missing. `CORS_ORIGINS` defaults to `http://localhost:1313`.

## Run

```bash
uvicorn app.main:app --reload
```

The database file (`lead-form-database.db`) is created in the project root on first startup. Tables are created if they don't exist.

## Add a site

Run from the project root:

```bash
python -m scripts.create_site
```

It prompts for a site key, site name, domain, and the email address that should receive notifications.

## API

### `GET /`

Health check. Returns `{"message": "Lead-form backend is working!"}`.

### `POST /leads`

Request body (JSON):

| Field          | Type   | Required | Max length |
|----------------|--------|----------|------------|
| `site_key`     | string | yes      | 100        |
| `email`        | email  | yes      | 254        |
| `name`         | string | no       | 100        |
| `phone`        | string | no       | 30         |
| `message`      | string | no       | 2000       |
| `page_url`     | string | no       | 2048       |
| `form_context` | string | no       | 100        |
| `honeypot`     | string | no       | 100        |

Example:

```bash
curl -X POST http://localhost:8000/leads \
  -H "Content-Type: application/json" \
  -d '{
    "site_key": "acme-plumbing",
    "name": "Jane",
    "email": "jane@example.com",
    "message": "Need a quote"
  }'
```

Responses:

- `200` `{"success": true, "message": "Lead submitted successfully."}`
- `403` unknown `site_key`, or the site is inactive
- `422` failed validation (bad email, field too long, missing required field)

## How a submission is handled

1. Request is validated by the Pydantic model.
2. If `honeypot` has a value, the request is treated as a bot. It is logged, nothing is saved, and a normal success response is returned.
3. The site is looked up by `site_key`. Unknown or inactive sites get a 403.
4. The lead is saved to `lead_submissions` with `notification_status = 'pending'`.
5. An email is sent to the site's `notification_email` through Resend.
6. `notification_status` is updated to `accepted` or `failed` (with the error text). If the email fails, the lead is still saved and the client still gets a success response.

## Database

Two tables:

- `sites`: `id`, `site_key` (unique), `site_name`, `domain`, `notification_email`, `active`, `created_at`
- `lead_submissions`: `id`, `site_id` (foreign key), `name`, `email`, `phone`, `message`, `page_url`, `form_context`, `created_at`, `notification_status`, `notification_attempted_at`, `notification_error`

## Backups

Create a backup (saved to `backups/` with a timestamp):

```bash
python -m scripts.backup_database
```

Test that a backup restores and passes SQLite's integrity check:

```bash
python -m scripts.test_database_restore backups/<backup-file>.db
```

The restore test writes to `restore-test.db` in the project root and refuses to run if that file already exists. Delete it when you are done.

## Logs

Logs go to the terminal and to `logs/lead-form-backend.log` (rotates at about 1 MB, keeps 5 old files).

## Not committed

`.env`, `*.db`, `backups/`, and `logs/` are in `.gitignore`.
