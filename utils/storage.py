"""Persistence helpers for MentorBridge.

Uses SQLAlchemy so accounts, sessions, and match history survive app restarts
and can be stored in PostgreSQL on Render.
"""

from __future__ import annotations

import json
import os
import logging
import socket
from urllib.parse import urlparse
from sqlalchemy import create_engine, Column, String, Integer, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError as SAOperationalError

_logger = logging.getLogger(__name__)

# On Render, provide the DATABASE_URL environment variable pointing to a PostgreSQL instance.
# Defaults to a local SQLite database for local development.
db_url = os.getenv("DATABASE_URL", "sqlite:///mentorbridge.db")

# SQLAlchemy 1.4+ removed support for the 'postgres://' URI scheme, which is what Render provides by default.
# It must be 'postgresql://' instead.
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Validate DB host early to provide a clearer error than an opaque SQLAlchemy/psycopg2 DNS error.
# If the hostname is a short token (no dot) it is likely missing the Render domain suffix
# (for example: use dpg-xxxx.region-postgres.render.com, not just dpg-xxxx).

def _validate_and_maybe_fallback(url: str) -> str:
    """Validate that the DB host resolves. Return the (possibly unchanged) URL.

    If the host part looks malformed (no dot) or DNS lookup fails, raise a helpful
    RuntimeError explaining how to fix DATABASE_URL. If the environment variable
    ALLOW_DB_FALLBACK=1 is set, fall back to a local sqlite DB instead of raising.
    """
    parsed = urlparse(url)
    hostname = parsed.hostname

    # Nothing to validate for sqlite or other non-network schemes
    if hostname is None:
        return url

    # Quick heuristic: require a dot in the hostname (FQDN). If missing, it's probably truncated.
    if "." not in hostname:
        msg = (
            f"Configured DATABASE_URL host looks incomplete: '{hostname}'.\n"
            "On Render you must use the full host name (for example: 'dpg-xxxx.region-postgres.render.com').\n"
            "Please update the DATABASE_URL environment variable to the full connection string from your Render Postgres dashboard."
        )
        if os.getenv("ALLOW_DB_FALLBACK") == "1":
            _logger.warning("%s Falling back to sqlite because ALLOW_DB_FALLBACK=1.", msg)
            return "sqlite:///mentorbridge.db"
        raise RuntimeError(msg)

    # Try to resolve the hostname to provide a clearer error if DNS fails.
    try:
        socket.gethostbyname(hostname)
    except OSError as e:
        msg = (
            f"Could not resolve database host '{hostname}': {e}.\n"
            "This usually means the DATABASE_URL is incorrect or DNS/networking prevents resolving the host.\n"
            "On Render copy the full connection string from the database dashboard (it typically ends with '.render.com')."
        )
        if os.getenv("ALLOW_DB_FALLBACK") == "1":
            _logger.warning("%s Falling back to sqlite because ALLOW_DB_FALLBACK=1.", msg)
            return "sqlite:///mentorbridge.db"
        raise RuntimeError(msg)

    return url

# Validate and possibly adjust the DB URL before creating the engine.
try:
    db_url = _validate_and_maybe_fallback(db_url)
except Exception:
    # Re-raise so the startup logs show a clear, actionable message instead of the raw psycopg2 DNS error.
    raise

# SQLite requires specific arguments to allow multi-threading, which Streamlit needs.
engine_args = {}
if db_url.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(db_url, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class StudentModel(Base):
    __tablename__ = "students"
    email = Column(String, primary_key=True, index=True)
    payload = Column(Text, nullable=False)

class MentorModel(Base):
    __tablename__ = "mentors"
    email = Column(String, primary_key=True, index=True)
    payload = Column(Text, nullable=False)

class SessionModel(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    payload = Column(Text, nullable=False)

class MatchModel(Base):
    __tablename__ = "matches"
    student_email = Column(String, primary_key=True, index=True)
    mentor_emails = Column(Text, nullable=False)

def init_db() -> None:
    try:
        Base.metadata.create_all(bind=engine)
    except SAOperationalError as e:
        # Provide a friendlier message for operational errors (DNS, auth, network).
        _logger.exception("Database initialization failed: %s", e)
        raise RuntimeError(
            "Failed to connect to the database during init_db().\n"
            "Check your DATABASE_URL environment variable and ensure the DB host is reachable.\n"
            "If you're deploying on Render, copy the full connection string from the database dashboard (it includes the .render.com host)."
        ) from e

def load_all_data() -> tuple[dict, dict, list, dict]:
    with SessionLocal() as db:
        students = {
            row.email: json.loads(row.payload)
            for row in db.query(StudentModel).all()
        }
        mentors = {
            row.email: json.loads(row.payload)
            for row in db.query(MentorModel).all()
        }
        sessions = []
        for row in db.query(SessionModel).order_by(SessionModel.id).all():
            payload = json.loads(row.payload)
            payload["id"] = row.id
            sessions.append(payload)
        matches = {
            row.student_email: json.loads(row.mentor_emails)
            for row in db.query(MatchModel).all()
        }
    return students, mentors, sessions, matches

def load_students() -> dict:
    with SessionLocal() as db:
        return {
            row.email: json.loads(row.payload)
            for row in db.query(StudentModel).all()
        }

def load_mentors() -> dict:
    with SessionLocal() as db:
        return {
            row.email: json.loads(row.payload)
            for row in db.query(MentorModel).all()
        }

def save_student(student: dict) -> None:
    _save_payload(StudentModel, student["email"], student)

def save_mentor(mentor: dict) -> None:
    _save_payload(MentorModel, mentor["email"], mentor)

def save_session(session: dict) -> dict:
    payload = dict(session)
    session_id = payload.pop("id", None)

    with SessionLocal() as db:
        if session_id is None:
            db_item = SessionModel(payload=json.dumps(payload))
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
            session_id = db_item.id
        else:
            db_item = db.query(SessionModel).filter(SessionModel.id == session_id).first()
            if db_item:
                db_item.payload = json.dumps(payload)
                db.commit()
            else:
                db_item = SessionModel(id=session_id, payload=json.dumps(payload))
                db.add(db_item)
                db.commit()

    saved = dict(payload)
    saved["id"] = session_id
    return saved

def replace_matches(student_email: str, mentor_emails: list[str]) -> None:
    with SessionLocal() as db:
        db_item = db.query(MatchModel).filter(MatchModel.student_email == student_email).first()
        if db_item:
            db_item.mentor_emails = json.dumps(mentor_emails)
        else:
            db_item = MatchModel(student_email=student_email, mentor_emails=json.dumps(mentor_emails))
            db.add(db_item)
        db.commit()

def _save_payload(model_class, email: str, payload: dict) -> None:
    with SessionLocal() as db:
        db_item = db.query(model_class).filter(model_class.email == email).first()
        if db_item:
            db_item.payload = json.dumps(payload)
        else:
            db_item = model_class(email=email, payload=json.dumps(payload))
            db.add(db_item)
        db.commit()
