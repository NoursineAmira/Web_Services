# Web_Services

A Flask + SQLite REST API for students and their end-of-studies reports, with JWT role-based access.

- A single-major student can have at most 1 report, a double major at most 2.
- Final-year (level 4) students must have exactly that number.
- A double major is only allowed from level 3.

## Run

```
pip install -r requirements.txt
copy .env.example .env    # then set your own values
python app.py
```

The API runs on `http://127.0.0.1:5000`. The database is created and seeded on first run.

## Run with Docker

Both versions run as containers: this API (`api`) and the in-class version in `correction/` (`correction`).

```
copy .env.example .env    # then set your own values
docker compose up --build
```

- API: `http://localhost:5000`
- In-class version: `http://localhost:5001/student`

The SQLite database lives in the `school-data` volume, so it survives restarts. `docker compose down -v` deletes it.

## Configuration

Everything is set through environment variables (or `.env`):

| Variable | Default | Purpose |
| --- | --- | --- |
| `JWT_SECRET` | required | token signing key, at least 32 characters |
| `ADMIN_PASSWORD`, `READER_PASSWORD` | required | passwords of the seeded users |
| `TOKEN_TTL_HOURS` | `5` | token lifetime |
| `HOST` | `127.0.0.1` (`0.0.0.0` in Docker) | bind address |
| `PORT` | `5000` | port inside the process |
| `FLASK_DEBUG` | `0` | Flask debug mode |
| `DB_PATH` | `school.db` (`/data/school.db` in Docker) | SQLite file |
| `API_PORT`, `CORRECTION_PORT` | `5000`, `5001` | host ports published by docker compose |

## Endpoints

| Method | Path | Role |
| --- | --- | --- |
| POST | `/auth/login` | public |
| GET | `/reports`, `/reports/<id>` (`?keyword=` to search) | admin, reader |
| POST, PUT, DELETE | `/reports`, `/reports/<id>` | admin |
| GET, POST, PUT, DELETE | `/students`, `/students/<id>`, `/students/<id>/reports` | admin |

Send the token from `/auth/login` as `Authorization: Bearer <token>`.
