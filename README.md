# Traveloop



<p align="center">
  <strong>A dark, full-stack travel planning workspace for building itineraries, managing budgets, sharing trips, and exploring community travel plans.</strong>
</p>

<p align="center">
  <a href="https://www.python.org/"><img alt="Python" src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white"></a>
  <a href="https://flask.palletsprojects.com/"><img alt="Flask" src="https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white"></a>
  <a href="https://docs.astral.sh/uv/"><img alt="uv" src="https://img.shields.io/badge/uv-managed-654FF0?style=for-the-badge"></a>
  <a href="https://tailwindcss.com/"><img alt="TailwindCSS" src="https://img.shields.io/badge/TailwindCSS-3-38BDF8?style=for-the-badge&logo=tailwindcss&logoColor=white"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/License-MIT-10B981?style=for-the-badge"></a>
</p>

---

## Overview

Traveloop is a Flask application for planning real trips from one polished dashboard. It combines authentication, itinerary building, trip sharing, community discovery, budget tools, packing lists, notes, weather context, and an admin analytics area.

The app is now dark-mode only, ships with local development seed accounts, and is designed to run quickly with `uv`.

## Highlights

| Area | What Traveloop Gives You |
| --- | --- |
| Trip planning | Create trips, stops, activities, packing items, notes, and budgets. |
| Dashboard | View travel summaries, upcoming trips, and trip statistics. |
| Community | Publish trips publicly and discover itineraries from other users. |
| Sharing | Generate read-only public links and clone shared trips. |
| Admin | Admin login, platform analytics, and user role management. |
| Developer setup | `uv.lock`, Flask-Migrate, SQLite defaults, local seed users, and optional Tailwind build tooling. |

## Tech Stack

| Layer | Tools |
| --- | --- |
| Backend | Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Login, Flask-WTF |
| Database | SQLite by default, PostgreSQL-compatible config |
| Frontend | Jinja2 templates, Tailwind CSS CDN/classes, Flowbite, Font Awesome, Chart.js, Leaflet |
| Tooling | uv, npm, Alembic migrations |
| Entry points | `main.py` for development, `wsgi.py` for production |

## Requirements

Install these first:

- Git
- Node.js 16 or newer
- npm
- uv

Python does not need to be installed separately if you use uv to manage it, but Python 3.8+ is supported.

## Install uv

Official uv installation docs: <https://docs.astral.sh/uv/getting-started/installation/>

macOS or Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If `curl` is not available:

```bash
wget -qO- https://astral.sh/uv/install.sh | sh
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Check installation:

```bash
uv --version
```

Optional: let uv install Python for you.

```bash
uv python install
```

## Quick Start

Clone the project:

```bash
git clone https://github.com/Varun0006/Traveloop.git
cd Traveloop
```

Install Python dependencies from the lockfile:

```bash
uv sync
```

Install frontend tooling:

```bash
npm install
```

Create your local environment file:

```bash
cp .env.example .env
```

Apply database migrations:

```bash
uv run flask --app main db upgrade
```

Run the app:

```bash
uv run python main.py
```

Open:

```text
http://localhost:5000
```

## Development Mode

Terminal 1, start Flask:

```bash
uv run python main.py
```

Terminal 2, optional Tailwind watcher:

```bash
npm run dev
```

The app uses Tailwind CDN in templates, so the Flask app can run without the watcher. Use the watcher when you are actively changing local CSS build output.

## Local Seed Accounts

In development, Traveloop creates local users automatically on startup. The seeding is idempotent, so rerunning the app will not duplicate accounts.

| Role | Username | Email | Password |
| --- | --- | --- | --- |
| Admin | `admin` | `admin@traveloop.local` | `Admin123!` |
| Test user | `testuser` | `testuser@traveloop.local` | `Test123!` |
| Traveler | `traveler` | `traveler@traveloop.local` | `Traveler123!` |

Admin login:

```text
http://localhost:5000/auth/admin/login
```

Normal login:

```text
http://localhost:5000/auth/login
```

Disable automatic development seeding:

```bash
AUTO_SEED_USERS=false uv run python main.py
```

Create or promote an admin manually:

```bash
uv run flask --app main create-admin admin admin@example.com "StrongPassword123!"
```

## Environment Variables

Minimum local `.env`:

```env
FLASK_ENV=development
FLASK_PORT=5000
SECRET_KEY=change-this-local-secret
SQLALCHEMY_DATABASE_URI=sqlite:///traveloop.db
AUTO_SEED_USERS=true
```

Optional integrations:

```env
GEODB_API_KEY=
OPENTRIPMAP_API_KEY=
OPENWEATHERMAP_API_KEY=
OPENROUTESERVICE_API_KEY=
UNSPLASH_API_KEY=
```

For PostgreSQL:

```env
SQLALCHEMY_DATABASE_URI=postgresql://username:password@localhost:5432/traveloop_db
```

## Useful Commands

| Task | Command |
| --- | --- |
| Install Python deps | `uv sync` |
| Run app | `uv run python main.py` |
| Run with custom port | `FLASK_PORT=5001 uv run python main.py` |
| Apply migrations | `uv run flask --app main db upgrade` |
| Create migration | `uv run flask --app main db migrate -m "Describe change"` |
| Create admin | `uv run flask --app main create-admin admin admin@example.com "StrongPassword123!"` |
| Install frontend deps | `npm install` |
| Watch CSS | `npm run dev` |
| Build CSS | `npm run build` |
| Production WSGI | `uv run --with gunicorn gunicorn wsgi:app` |

## Project Structure

```text
Traveloop/
├── app/
│   ├── models/          # SQLAlchemy models
│   ├── routes/          # Flask blueprints and API endpoints
│   ├── services/        # Business logic
│   ├── static/          # CSS and JavaScript
│   └── templates/       # Jinja pages and components
├── config/              # Environment-specific Flask config
├── docs/                # Setup and structure notes
├── migrations/          # Alembic / Flask-Migrate revisions
├── scripts/             # Utility scripts
├── tests/               # Test package
├── main.py              # Development server
├── wsgi.py              # Production WSGI entry point
├── pyproject.toml       # Python project metadata
├── uv.lock              # Locked Python dependencies
└── package.json         # Frontend tooling
```

## Database Notes

SQLite is the default:

```text
instance/traveloop.db
```

For a fresh local reset:

```bash
rm instance/traveloop.db
uv run flask --app main db upgrade
uv run python main.py
```

The app also calls `db.create_all()` during startup, which helps local development. Migrations are still the recommended path when schema changes are involved.

## Troubleshooting

CSRF token is missing:

```text
Make sure pages are loaded from the Flask app and forms include the generated csrf_token.
Restart the server after pulling the latest changes.
```

Port 5000 is already in use:

```bash
FLASK_PORT=5001 uv run python main.py
```

Dependencies are out of date:

```bash
uv sync
npm install
```

Migration command cannot find the app:

```bash
uv run flask --app main db upgrade
```

Need a clean Python environment:

```bash
rm -rf .venv
uv sync
```

Git pull is blocked by local changes:

```bash
git status
git add -A
git commit -m "Describe your changes"
git pull --rebase origin main
```

## Production Notes

Before production:

- Set `FLASK_ENV=production`.
- Set a strong `SECRET_KEY`.
- Use PostgreSQL or another managed database.
- Set `AUTO_SEED_USERS=false`.
- Run migrations with `uv run flask --app main db upgrade`.
- Serve through Gunicorn, Nginx, or your platform’s WSGI runner.

Example:

```bash
uv sync --frozen
uv run flask --app main db upgrade
uv run --with gunicorn gunicorn wsgi:app
```

## Documentation

- [Setup Guide](docs/SETUP.md)
- [Project Structure](docs/STRUCTURE.md)
- [Development Plan](plan.md)
- [License](LICENSE)

## License

Traveloop is released under the MIT License. See [LICENSE](LICENSE).
