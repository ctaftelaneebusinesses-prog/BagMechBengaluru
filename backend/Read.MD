# BagMech Bengaluru — Run Guide

This project is a single FastAPI backend that also serves the frontend as
static files. There is no separate frontend dev server — running the
backend gives you the whole app.

## 1. Prerequisites

- Python 3.13 (a `venv` already exists at `backend/venv`)
- A Postgres database (this project targets Supabase — see `schema.sql`)

## 2. One-time setup

```powershell
cd backend
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/.env` from `.env.example` and fill in the values:

```
DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname
ALLOWED_ORIGINS=*

ENABLE_EMAIL_NOTIFICATIONS=false
SENDGRID_API_KEY=
NOTIFY_EMAIL_FROM=
NOTIFY_EMAIL_TO=

ENABLE_WHATSAPP_NOTIFICATIONS=false
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_FROM=
OWNER_WHATSAPP_NUMBER=

WHATSAPP_BUSINESS_NUMBER=
```

> Note: email notifications go through the **SendGrid HTTPS API**, not SMTP
> (raw SMTP is blocked on most PaaS hosts). `NOTIFY_EMAIL_FROM` must be a
> Single Sender verified in the SendGrid account.

If the database is empty, run `schema.sql` against it once (e.g. in the
Supabase SQL Editor, or via `psql`) to create the `zones`/`bookings`
tables and seed the zone list.

## 3. Run it

```powershell
cd backend
venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Then open **http://127.0.0.1:8000** — the frontend (`backend/static/index.html`)
is served at `/`, and the API lives under `/api/*` (e.g. `/api/zones`,
`/api/bookings`, `/health`).

## 4. Project layout

- `backend/app/main.py` — FastAPI app, routes, static file mount
- `backend/app/config.py` — settings loaded from `.env`
- `backend/app/models.py` / `schemas.py` — DB models and request/response shapes
- `backend/app/notifications.py` — SendGrid email + Twilio WhatsApp alerts on new bookings
- `backend/static/index.html` — the frontend
- `backend/schema.sql` — Postgres schema + seed data
