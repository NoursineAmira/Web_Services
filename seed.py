from uuid import uuid4

USERS = [
    {"id": str(uuid4()), "username": "admin", "password_env": "ADMIN_PASSWORD", "role": "admin"},
    {"id": str(uuid4()), "username": "reader", "password_env": "READER_PASSWORD", "role": "reader"},
]

STUDENTS = [
    {"id": str(uuid4()), "first_name": "Yasmine", "last_name": "Haddad", "double_major": 1, "level": 4},
    {"id": str(uuid4()), "first_name": "Omar", "last_name": "Benali", "double_major": 0, "level": 4},
    {"id": str(uuid4()), "first_name": "Lina", "last_name": "Mansour", "double_major": 1, "level": 3},
    {"id": str(uuid4()), "first_name": "Karim", "last_name": "Trabelsi", "double_major": 0, "level": 2},
    {"id": str(uuid4()), "first_name": "Sara", "last_name": "Jaziri", "double_major": 0, "level": 4},
    {"id": str(uuid4()), "first_name": "Mehdi", "last_name": "Gharbi", "double_major": 0, "level": 1},
]

REPORTS = [
    {
        "id": str(uuid4()),
        "student_id": STUDENTS[0]["id"],
        "title": "Fraud Detection in Mobile Payments",
        "type": "End of Year Internship",
        "k1": "machine learning",
        "k2": "fintech",
        "k3": "fraud",
        "release_date": "2026-06-20",
    },
    {
        "id": str(uuid4()),
        "student_id": STUDENTS[0]["id"],
        "title": "Pricing Models for Microinsurance",
        "type": "Mini Senior Project",
        "k1": "actuarial",
        "k2": "insurance",
        "k3": None,
        "release_date": "2026-06-27",
    },
    {
        "id": str(uuid4()),
        "student_id": STUDENTS[1]["id"],
        "title": "Container Orchestration for Small Teams",
        "type": "End of Year Internship",
        "k1": "kubernetes",
        "k2": "devops",
        "k3": "cloud",
        "release_date": "2026-07-02",
    },
    {
        "id": str(uuid4()),
        "student_id": STUDENTS[2]["id"],
        "title": "Sentiment Analysis of Arabic Tweets",
        "type": "Mini Senior Project",
        "k1": "nlp",
        "k2": "arabic",
        "k3": None,
        "release_date": "2025-12-15",
    },
    {
        "id": str(uuid4()),
        "student_id": STUDENTS[4]["id"],
        "title": "Energy Monitoring with IoT Sensors",
        "type": "End of Year Internship",
        "k1": "iot",
        "k2": "energy",
        "k3": "embedded",
        "release_date": "2026-06-30",
    },
]
