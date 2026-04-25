"""
MentorBridge AI Matching Engine
================================
Computes a compatibility score [0-1] between a student and a mentor using a
weighted multi-factor approach.  In production you would replace / augment this
with a trained ML model (e.g. sentence-transformers for CV-bio embedding
similarity, gradient-boosted ranker, or collaborative-filtering from session
feedback).
"""

from __future__ import annotations
import re

# ─── weights (must sum to 1.0) ───────────────────────────────────────────────
W_INTERESTS   = 0.35   # student interests ↔ mentor industry/expertise
W_GOALS       = 0.30   # student goals ↔ mentor expertise areas
W_SKILLS      = 0.20   # student CV skills ↔ mentor expertise keywords
W_EXPERIENCE  = 0.10   # mentor seniority bonus
W_GEO         = 0.05   # same-country bonus (encourages local role models)

# keyword expansion maps ──────────────────────────────────────────────────────
INTEREST_TO_EXPERTISE: dict[str, list[str]] = {
    "Technology / Software":  ["Technical mentoring", "Career guidance"],
    "Data Science / AI":      ["Technical mentoring", "Research & Academia"],
    "Finance / Banking":      ["Career guidance", "Leadership", "Networking"],
    "Healthcare / Medicine":  ["Research & Academia", "Graduate school", "Career guidance"],
    "Engineering":            ["Technical mentoring", "Career guidance"],
    "Business / Management":  ["Leadership", "Networking", "Entrepreneurship"],
    "Law":                    ["Career guidance", "Networking"],
    "Education":              ["Research & Academia", "Career guidance"],
    "Public Policy":          ["Career guidance", "Leadership"],
    "Agriculture":            ["Entrepreneurship", "Career guidance"],
    "Energy / Sustainability":["Career guidance", "Entrepreneurship"],
    "Media / Communications": ["Networking", "Career guidance"],
}

GOAL_TO_EXPERTISE: dict[str, list[str]] = {
    "Career guidance":               ["Career guidance"],
    "Research support":              ["Research & Academia"],
    "Internship/job search":         ["Career guidance", "Networking", "Interview preparation"],
    "Entrepreneurship":              ["Entrepreneurship"],
    "Graduate school applications":  ["Graduate school", "Research & Academia"],
    "Technical skills":              ["Technical mentoring"],
    "Leadership":                    ["Leadership"],
    "Networking":                    ["Networking"],
}

SKILL_KEYWORDS: dict[str, list[str]] = {
    "python":          ["Technical mentoring"],
    "machine learning":["Technical mentoring", "Research & Academia"],
    "data":            ["Technical mentoring", "Research & Academia"],
    "sql":             ["Technical mentoring"],
    "finance":         ["Career guidance"],
    "excel":           ["Career guidance"],
    "research":        ["Research & Academia"],
    "writing":         ["Career guidance"],
    "public health":   ["Research & Academia", "Graduate school"],
    "engineering":     ["Technical mentoring"],
    "java":            ["Technical mentoring"],
    "javascript":      ["Technical mentoring"],
    "react":           ["Technical mentoring"],
    "cloud":           ["Technical mentoring"],
    "leadership":      ["Leadership"],
    "management":      ["Leadership"],
    "entrepreneurship":["Entrepreneurship"],
    "startup":         ["Entrepreneurship"],
}

EXP_BONUS: dict[str, float] = {
    "5-7": 0.5, "8-10": 0.70, "11-15": 0.85, "15+": 1.0,
}


def score_match(student: dict, mentor: dict) -> float:
    """Return a compatibility score in [0, 1]."""
    if not student or not mentor:
        return 0.0

    mentor_expertise = set(mentor.get("expertise", []))

    # ── 1. Interest overlap ──────────────────────────────────────────────────
    interest_hits = 0
    interest_total = max(len(student.get("interests", [])), 1)
    for interest in student.get("interests", []):
        mapped = INTEREST_TO_EXPERTISE.get(interest, [])
        if any(m in mentor_expertise for m in mapped):
            interest_hits += 1
        # also check direct industry match
        if interest == mentor.get("industry", ""):
            interest_hits += 0.5
    s_interests = min(interest_hits / interest_total, 1.0)

    # ── 2. Goal overlap ──────────────────────────────────────────────────────
    goal_hits = 0
    goal_total = max(len(student.get("goals", [])), 1)
    for goal in student.get("goals", []):
        mapped = GOAL_TO_EXPERTISE.get(goal, [])
        if any(m in mentor_expertise for m in mapped):
            goal_hits += 1
    s_goals = min(goal_hits / goal_total, 1.0)

    # ── 3. CV skill keyword overlap ──────────────────────────────────────────
    cv_text  = (student.get("cv_text", "") + " " + " ".join(student.get("skills", []))).lower()
    skill_hits = 0
    skill_total = max(len(SKILL_KEYWORDS), 1)
    for kw, mapped in SKILL_KEYWORDS.items():
        if kw in cv_text and any(m in mentor_expertise for m in mapped):
            skill_hits += 1
    s_skills = min(skill_hits / max(skill_total * 0.3, 1), 1.0)

    # ── 4. Experience seniority bonus ────────────────────────────────────────
    s_exp = EXP_BONUS.get(mentor.get("years_exp", "5-7"), 0.5)

    # ── 5. Geographic affinity ───────────────────────────────────────────────
    s_geo = 0.0
    if student.get("country") and mentor.get("country"):
        if student["country"] == mentor["country"]:
            s_geo = 1.0
        else:
            # both African countries → partial bonus
            african = {
                "Nigeria","Ghana","Kenya","South Africa","Ethiopia","Senegal",
                "Uganda","Tanzania","Rwanda","Cameroon","Egypt","Morocco","Sudan",
            }
            if student["country"] in african and mentor["country"] in african:
                s_geo = 0.5

    raw = (W_INTERESTS * s_interests +
           W_GOALS     * s_goals     +
           W_SKILLS    * s_skills    +
           W_EXPERIENCE* s_exp       +
           W_GEO       * s_geo)

    # clamp to [0.1, 0.99] so there's always a meaningful range
    return round(max(0.10, min(raw, 0.99)), 3)


def rank_mentors(student: dict, mentors: dict[str, dict]) -> list[tuple[str, float]]:
    """Return list of (mentor_email, score) sorted descending."""
    scored = [(email, score_match(student, m)) for email, m in mentors.items()]
    return sorted(scored, key=lambda x: x[1], reverse=True)
