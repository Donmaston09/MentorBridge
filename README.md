# 🌍 MentorBridge Africa

AI-powered mentorship platform connecting African undergraduate students with volunteer mentors inside and beyond the continent.

---

## Features

| Feature | Details |
|---|---|
| **Student Registration** | Full profile + CV upload (PDF/DOCX) |
| **CV Parsing** | Auto-extracts skills using regex + `pdfplumber` / `python-docx` |
| **Mentor Registration** | Volunteer onboarding, expertise, availability |
| **AI Matching** | Multi-factor weighted scoring (interests, goals, skills, experience, geography) |
| **Session Booking** | Pick day/time slot, duration, platform |
| **Meeting Links** | Auto-generates Teams or Google Meet links |
| **Dashboards** | Role-specific views for students and mentors |
| **Availability Manager** | Mentors set weekly time slots |
| **Student Management** | Mentors see booked students + session history |
| **Mission Model** | Free mentoring, volunteer mentors, first-job success payment support |
| **Persistence** | Registrations, sessions, and matches saved in SQLite |

---

## Platform Model

- Students receive mentoring for free.
- Mentors join as volunteers and are not paid for sessions.
- Students are invited to make a payment after securing their first job.
- Creator support: [paypal.me/Onoja412](https://paypal.me/Onoja412)

---

## Quick Start

```bash
# 1. Clone / copy the project folder
cd mentorbridge

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app opens at **http://localhost:8501**.

Local data is stored in `mentorbridge.db` by default.

To choose a different database file, set:

```bash
export MENTORBRIDGE_DB_PATH=/absolute/path/to/mentorbridge.db
```

---

## Demo Accounts

On the Login page, click **"Create & load demo accounts"** then use:

| Role | Email | Password |
|---|---|---|
| Student | student@demo.com | demo123 |
| Mentor | mentor@demo.com | demo123 |

Three demo mentors are seeded with varied profiles and availability.

---

## Project Structure

```
mentorbridge/
├── app.py                  # Entry point + global CSS + routing
├── requirements.txt
├── pages/
│   ├── home.py             # Landing page
│   ├── register.py         # Student & mentor registration
│   ├── login.py            # Login + demo seeding
│   ├── dashboard.py        # Role-aware dashboard
│   ├── matching.py         # AI mentor search & booking
│   ├── sessions.py         # Upcoming / past sessions
│   ├── profile.py          # Editable profile
│   ├── availability.py     # Mentor availability manager
│   └── students_view.py    # Mentor's student list
└── utils/
    ├── matching.py         # Weighted AI match scoring engine
    ├── cv_parser.py        # PDF/DOCX text extraction + skill detection
    └── meetings.py         # Meeting link generator
```

---

## AI Matching Algorithm

`utils/matching.py` scores each student–mentor pair on five factors:

| Factor | Weight | Source |
|---|---|---|
| Interest ↔ Industry/Expertise | 35% | Student interests vs mentor expertise |
| Goals ↔ Expertise | 30% | Student goals vs mentor areas |
| CV Skills ↔ Expertise | 20% | Parsed CV keywords vs mentor expertise |
| Seniority Bonus | 10% | Mentor years of experience |
| Geographic Affinity | 5% | Same country / both African |

### Production ML upgrade path

Replace the scoring function with:
- **Sentence-Transformers** — embed student CV + mentor bio → cosine similarity
- **LightGBM / XGBoost ranker** — trained on session booking + satisfaction data  
- **Collaborative filtering** — "students like you also connected with…"

---

## Production Integrations

### Real Meeting Links
- **Microsoft Teams** → [Microsoft Graph API](https://learn.microsoft.com/en-us/graph/api/application-post-onlinemeetings)
- **Google Meet** → [Google Calendar API](https://developers.google.com/calendar/api/guides/create-events#conferencing)

### Success Payments
- Add a lightweight post-outcome payment flow for students after they secure their first job
- Creator support link: [paypal.me/Onoja412](https://paypal.me/Onoja412)

### Email Notifications
- SendGrid or AWS SES → confirmation emails on booking

### Persistent Storage
- Current: SQLite via `mentorbridge.db`
- Future upgrade: move to **PostgreSQL** (recommended for multi-instance production) or **Firebase Firestore**

### CV Parsing (Production)
- Replace regex with **spaCy NER** or call an LLM (e.g. Claude API) to extract structured data from CVs

---

## Roadmap

- [ ] Email verification on registration  
- [ ] First-job success payment tracking  
- [ ] Real Teams / Google Meet calendar invites  
- [ ] In-app messaging between student and mentor  
- [ ] Session rating & feedback system  
- [ ] Admin dashboard  
- [ ] Mobile-responsive PWA  
- [ ] LLM-powered CV analysis (Claude API)  
- [ ] Recommendation engine trained on session feedback  
