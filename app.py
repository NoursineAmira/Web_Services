import sqlite3
from uuid import uuid4

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash

from auth import TOKEN_TTL, create_token, require_role
from config import DEBUG, HOST, PORT
from db import INSERT_REPORT, INSERT_STUDENT, close_db, get_db, init_db
from validation import (
    ApiError,
    check_report_count,
    invalid,
    parse_id,
    validate_login,
    validate_report,
    validate_student,
)

app = Flask(__name__)
app.json.sort_keys = False
app.teardown_appcontext(close_db)
init_db()


def json_body():
    if not request.is_json:
        raise ApiError(415, "UNSUPPORTED_MEDIA_TYPE", "Content-Type must be application/json")
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ApiError(400, "VALIDATION_ERROR", "Request body must be a valid JSON object")
    return data


def find_student(student_id):
    student_id = parse_id(student_id, "student id")
    row = get_db().execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if row is None:
        raise ApiError(404, "NOT_FOUND", f"Student {student_id} not found")
    return row


def find_report(report_id):
    report_id = parse_id(report_id, "report id")
    row = get_db().execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    if row is None:
        raise ApiError(404, "NOT_FOUND", f"Report {report_id} not found")
    return row


def count_reports(student_id):
    return get_db().execute("SELECT COUNT(*) FROM reports WHERE student_id = ?", (student_id,)).fetchone()[0]


def reports_of(student_id):
    rows = get_db().execute(
        "SELECT * FROM reports WHERE student_id = ? ORDER BY release_date", (student_id,)
    ).fetchall()
    return [dict(row) for row in rows]


def student_json(row, with_reports=False):
    student = dict(row)
    student["double_major"] = bool(student["double_major"])
    if with_reports:
        student["reports"] = reports_of(student["id"])
    return student


def insert_reports(db, student_id, reports):
    for report in reports:
        db.execute(INSERT_REPORT, {**report, "id": str(uuid4()), "student_id": student_id})


@app.post("/auth/login")
def login():
    credentials = validate_login(json_body())
    user = get_db().execute("SELECT * FROM users WHERE username = ?", (credentials["username"],)).fetchone()
    if user is None or not check_password_hash(user["password_hash"], credentials["password"]):
        raise ApiError(401, "INVALID_CREDENTIALS", "Invalid username or password")
    return jsonify(
        {
            "access_token": create_token(user["username"], user["role"]),
            "token_type": "Bearer",
            "expires_in": int(TOKEN_TTL.total_seconds()),
            "role": user["role"],
        }
    )


@app.get("/students")
@require_role("admin")
def list_students():
    rows = get_db().execute("SELECT * FROM students ORDER BY last_name, first_name").fetchall()
    return jsonify([student_json(row) for row in rows])


@app.get("/students/<student_id>")
@require_role("admin")
def get_student(student_id):
    return jsonify(student_json(find_student(student_id), with_reports=True))


@app.get("/students/<student_id>/reports")
@require_role("admin")
def get_student_reports(student_id):
    return jsonify(reports_of(find_student(student_id)["id"]))


@app.post("/students")
@require_role("admin")
def create_student():
    student, reports = validate_student(json_body())
    check_report_count(student["level"], student["double_major"], len(reports))
    student["id"] = str(uuid4())

    db = get_db()
    with db:
        db.execute(INSERT_STUDENT, student)
        insert_reports(db, student["id"], reports)
    return jsonify(student_json(find_student(student["id"]), with_reports=True)), 201


@app.put("/students/<student_id>")
@require_role("admin")
def update_student(student_id):
    current = find_student(student_id)
    student, new_reports = validate_student(json_body())
    total = count_reports(current["id"]) + len(new_reports)
    check_report_count(student["level"], student["double_major"], total)
    student["id"] = current["id"]

    db = get_db()
    with db:
        db.execute(
            "UPDATE students SET first_name = :first_name, last_name = :last_name, "
            "double_major = :double_major, level = :level WHERE id = :id",
            student,
        )
        insert_reports(db, student["id"], new_reports)
    return jsonify(student_json(find_student(student["id"]), with_reports=True))


@app.delete("/students/<student_id>")
@require_role("admin")
def delete_student(student_id):
    student = find_student(student_id)
    db = get_db()
    with db:
        db.execute("DELETE FROM students WHERE id = ?", (student["id"],))
    return "", 204


@app.get("/reports")
@require_role("admin", "reader")
def list_reports():
    keyword = request.args.get("keyword", "").strip().lower()
    db = get_db()
    if keyword:
        rows = db.execute(
            "SELECT * FROM reports WHERE ? IN (lower(k1), lower(k2), lower(k3)) ORDER BY release_date DESC",
            (keyword,),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM reports ORDER BY release_date DESC").fetchall()
    return jsonify([dict(row) for row in rows])


@app.get("/reports/<report_id>")
@require_role("admin", "reader")
def get_report(report_id):
    return jsonify(dict(find_report(report_id)))


@app.post("/reports")
@require_role("admin")
def create_report():
    report = validate_report(json_body())
    student = find_student(report["student_id"])
    check_report_count(student["level"], student["double_major"], count_reports(student["id"]) + 1)

    db = get_db()
    with db:
        report_id = str(uuid4())
        db.execute(INSERT_REPORT, {**report, "id": report_id})
    return jsonify(dict(find_report(report_id))), 201


@app.put("/reports/<report_id>")
@require_role("admin")
def update_report(report_id):
    current = find_report(report_id)
    report = validate_report(json_body())
    if report["student_id"] != current["student_id"]:
        raise invalid({"student_id": "cannot be changed, a report always belongs to the same student"})
    report["id"] = current["id"]

    db = get_db()
    with db:
        db.execute(
            "UPDATE reports SET title = :title, type = :type, k1 = :k1, k2 = :k2, k3 = :k3, "
            "release_date = :release_date WHERE id = :id",
            report,
        )
    return jsonify(dict(find_report(current["id"])))


@app.delete("/reports/<report_id>")
@require_role("admin")
def delete_report(report_id):
    report = find_report(report_id)
    student = find_student(report["student_id"])
    check_report_count(student["level"], student["double_major"], count_reports(student["id"]) - 1)

    db = get_db()
    with db:
        db.execute("DELETE FROM reports WHERE id = ?", (report["id"],))
    return "", 204


@app.errorhandler(ApiError)
def handle_api_error(error):
    return jsonify(error.to_dict()), error.status


@app.errorhandler(HTTPException)
def handle_http_error(error):
    code = error.name.upper().replace(" ", "_")
    return handle_api_error(ApiError(error.code, code, error.description))


@app.errorhandler(sqlite3.IntegrityError)
def handle_integrity_error(error):
    return handle_api_error(ApiError(409, "CONSTRAINT_VIOLATION", "Database constraint violated"))


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    app.logger.exception(error)
    return handle_api_error(ApiError(500, "INTERNAL_ERROR", "An unexpected error occurred"))


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
