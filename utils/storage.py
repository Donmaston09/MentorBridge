"""Persistence helpers for MentorBridge.

Uses SQLAlchemy so accounts, sessions, and match history survive app restarts
and can be stored in PostgreSQL on Render.
"""

from __future__ import annotations

import json
import os
from sqlalchemy import create_engine, Column, String, Integer, Text
from sqlalchemy.orm import declarative_base, sessionmaker

# On Render, provide the DATABASE_URL environment variable pointing to a PostgreSQL instance.
# Defaults to a local SQLite database for local development.
db_url = os.getenv("DATABASE_URL", "sqlite:///mentorbridge.db")

# SQLAlchemy 1.4+ removed support for the 'postgres://' URI scheme, which is what Render provides by default.
# It must be 'postgresql://' instead.
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

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
    Base.metadata.create_all(bind=engine)

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
