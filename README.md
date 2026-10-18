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

## Endpoints

| Method | Path | Role |
| --- | --- | --- |
| POST | `/auth/login` | public |
| GET | `/reports`, `/reports/<id>` (`?keyword=` to search) | admin, reader |
| POST, PUT, DELETE | `/reports`, `/reports/<id>` | admin |
| GET, POST, PUT, DELETE | `/students`, `/students/<id>`, `/students/<id>/reports` | admin |

Send the token from `/auth/login` as `Authorization: Bearer <token>`.
