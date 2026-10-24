import sqlite3
from contextlib import closing

from flask import g
from werkzeug.security import generate_password_hash

from config import DB_PATH, require_env
from seed import REPORTS, STUDENTS, USERS

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id           TEXT PRIMARY KEY,
    first_name   TEXT NOT NULL,
    last_name    TEXT NOT NULL,
    double_major INTEGER NOT NULL CHECK (double_major IN (0, 1)),
    level        INTEGER NOT NULL CHECK (level BETWEEN 1 AND 4)
);

CREATE TABLE IF NOT EXISTS reports (
    id           TEXT PRIMARY KEY,
    student_id   TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    title        TEXT NOT NULL,
    type         TEXT NOT NULL,
    k1           TEXT NOT NULL,
    k2           TEXT,
    k3           TEXT,
    release_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id            TEXT PRIMARY KEY,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('admin', 'reader'))
);
"""

INSERT_USER = """
INSERT INTO users (id, username, password_hash, role)
VALUES (:id, :username, :password_hash, :role)
"""

INSERT_STUDENT = """
INSERT INTO students (id, first_name, last_name, double_major, level)
VALUES (:id, :first_name, :last_name, :double_major, :level)
"""

INSERT_REPORT = """
INSERT INTO reports (id, student_id, title, type, k1, k2, k3, release_date)
VALUES (:id, :student_id, :title, :type, :k1, :k2, :k3, :release_date)
"""


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db():
    if "db" not in g:
        g.db = connect()
    return g.db


def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with closing(connect()) as conn:
        conn.executescript(SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
            with conn:
                conn.executemany(INSERT_STUDENT, STUDENTS)
                conn.executemany(INSERT_REPORT, REPORTS)
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            with conn:
                conn.executemany(
                    INSERT_USER,
                    [{**user, "password_hash": generate_password_hash(require_env(user["password_env"]))} for user in USERS],
                )
