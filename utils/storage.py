"""Persistence helpers for MentorBridge.

Uses a small SQLite database so accounts, sessions, and match history
survive app restarts. On Render, point `MENTORBRIDGE_DB_PATH` at a
persistent disk mount (for example `/var/data/mentorbridge.db`).
"""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import closing


DB_PATH = os.getenv("MENTORBRIDGE_DB_PATH", "mentorbridge.db")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(_connect()) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                email TEXT PRIMARY KEY,
                payload TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS mentors (
                email TEXT PRIMARY KEY,
                payload TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payload TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS matches (
                student_email TEXT PRIMARY KEY,
                mentor_emails TEXT NOT NULL
            )
            """
        )
        conn.commit()


def load_all_data() -> tuple[dict, dict, list, dict]:
    with closing(_connect()) as conn:
        cur = conn.cursor()

        students = {
            row["email"]: json.loads(row["payload"])
            for row in cur.execute("SELECT email, payload FROM students")
        }
        mentors = {
            row["email"]: json.loads(row["payload"])
            for row in cur.execute("SELECT email, payload FROM mentors")
        }
        sessions = []
        for row in cur.execute("SELECT id, payload FROM sessions ORDER BY id"):
            payload = json.loads(row["payload"])
            payload["id"] = row["id"]
            sessions.append(payload)
        matches = {
            row["student_email"]: json.loads(row["mentor_emails"])
            for row in cur.execute("SELECT student_email, mentor_emails FROM matches")
        }

    return students, mentors, sessions, matches


def load_students() -> dict:
    students, _, _, _ = load_all_data()
    return students


def load_mentors() -> dict:
    _, mentors, _, _ = load_all_data()
    return mentors


def save_student(student: dict) -> None:
    _save_payload("students", student["email"], student)


def save_mentor(mentor: dict) -> None:
    _save_payload("mentors", mentor["email"], mentor)


def save_session(session: dict) -> dict:
    payload = dict(session)
    session_id = payload.pop("id", None)

    with closing(_connect()) as conn:
        cur = conn.cursor()
        if session_id is None:
            cur.execute("INSERT INTO sessions (payload) VALUES (?)", (json.dumps(payload),))
            session_id = cur.lastrowid
        else:
            cur.execute(
                "UPDATE sessions SET payload = ? WHERE id = ?",
                (json.dumps(payload), session_id),
            )
        conn.commit()

    saved = dict(payload)
    saved["id"] = session_id
    return saved


def replace_matches(student_email: str, mentor_emails: list[str]) -> None:
    with closing(_connect()) as conn:
        conn.execute(
            """
            INSERT INTO matches (student_email, mentor_emails)
            VALUES (?, ?)
            ON CONFLICT(student_email) DO UPDATE SET mentor_emails = excluded.mentor_emails
            """,
            (student_email, json.dumps(mentor_emails)),
        )
        conn.commit()


def _save_payload(table: str, email: str, payload: dict) -> None:
    with closing(_connect()) as conn:
        conn.execute(
            f"""
            INSERT INTO {table} (email, payload)
            VALUES (?, ?)
            ON CONFLICT(email) DO UPDATE SET payload = excluded.payload
            """,
            (email, json.dumps(payload)),
        )
        conn.commit()
