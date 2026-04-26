import streamlit as st
import base64
import os
from utils.storage import init_db, load_all_data

st.set_page_config(
    page_title="MentorBridge Africa",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── shared CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --primary:   #1a472a;
    --accent:    #f4a228;
    --light:     #081a3a;
    --dark:      #eef4ff;
    --card:      #10264f;
    --muted:     #b8c7e6;
    --danger:    #c0392b;
    --success:   #27ae60;
    --rose:      #f26ca7;
    --sky:       #69bff8;
    --gold:      #ffd166;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--dark);
}

body {
    background:
        radial-gradient(circle at 12% 18%, rgba(242, 108, 167, 0.16), transparent 26%),
        radial-gradient(circle at 84% 14%, rgba(105, 191, 248, 0.18), transparent 24%),
        radial-gradient(circle at 78% 74%, rgba(255, 209, 102, 0.14), transparent 25%),
        linear-gradient(160deg, #06142d 0%, #0a1f45 45%, #102a59 100%);
}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewContainer"] .main .block-container {
    background:
        radial-gradient(circle at top left, rgba(255,255,255,0.06), transparent 28%),
        linear-gradient(160deg, #06142d 0%, #0a1f45 45%, #102a59 100%) !important;
    color: var(--dark) !important;
}

[data-testid="stAppViewContainer"] .main .block-container,
[data-testid="stMainBlockContainer"] {
    border-radius: 0 !important;
    box-shadow: none !important;
}

[data-testid="stHeader"] {
    background: rgba(8, 23, 50, 0.55);
    backdrop-filter: blur(10px);
}

h1, h2, h3, h4, h5, h6 { font-family: 'Playfair Display', serif; color: #f4f8ff; }
p, label, span, div { color: inherit; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #081732 0%, #0b2250 100%) !important;
    color: white;
}
section[data-testid="stSidebar"] * { color: white !important; }
section[data-testid="stSidebar"] .stRadio > div { gap: 0.4rem; }
[data-testid="stSidebarNav"] { display: none !important; }

/* Buttons */
div.stButton > button {
    background: linear-gradient(135deg, #f4a228 0%, #e08f10 100%);
    color: #0d1f14 !important;
    border: none;
    border-radius: 8px;
    font-weight: 700 !important;
    padding: 0.55rem 1.4rem;
    transition: all .2s;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(244,162,40,0.3);
}
div.stButton > button p {
    color: #0d1f14 !important;
    font-weight: 700 !important;
}

/* Cards */
.mb-card {
    background: rgba(16, 38, 79, 0.86);
    backdrop-filter: blur(14px);
    border-radius: 14px;
    padding: 1.6rem 1.8rem;
    box-shadow: 0 10px 24px rgba(0,0,0,.22);
    margin-bottom: 1rem;
    border-left: 4px solid var(--accent);
    border: 1px solid rgba(255,255,255,0.08);
}
.mb-card h3 { margin-top: 0; font-size: 1.15rem; }

/* Metric tiles */
.metric-tile {
    background:
        linear-gradient(135deg, rgba(26,71,42,0.94) 0%, rgba(45,106,79,0.92) 58%, rgba(105,191,248,0.78) 100%);
    color: white;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.18);
    box-shadow: 0 10px 24px rgba(26,71,42,0.16);
}
.metric-tile .value { font-size: 2rem; font-weight: 700; color: var(--accent); }
.metric-tile .label { font-size: 0.82rem; opacity: .8; }

/* Match score badge */
.score-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85rem;
}
.score-high  { background:#d4edda; color:#155724; }
.score-mid   { background:#fff3cd; color:#856404; }
.score-low   { background:#f8d7da; color:#721c24; }

/* Hero banner */
.hero {
    color: white;
    border-radius: 18px;
    padding: 3rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: '🌍';
    position: absolute;
    right: 2rem; top: 1rem;
    font-size: 7rem;
    opacity: .15;
}
.hero h1 { color: white; font-size: 2.4rem; margin: 0; }
.hero p  { color: rgba(255,255,255,.85); font-size: 1.05rem; margin-top: .5rem; }

/* Pills */
.pill {
    display: inline-block;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.78rem;
    margin: 2px;
    color: #eef4ff;
    font-weight: 500;
}

/* Form tweaks */
.stTextInput input, .stSelectbox select, .stTextArea textarea {
    border-radius: 8px !important;
    border: 1.5px solid rgba(255,255,255,0.15) !important;
    background: rgba(255,255,255,0.06) !important;
    color: #eef4ff !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(244,162,40,.2) !important;
}

.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div,
.stTextArea textarea,
.stFileUploader section,
.stRadio > div,
.stCheckbox > label,
.stSlider,
.stMarkdown,
.stCaption,
.stSubheader,
.stHeader,
.st-emotion-cache-10trblm,
.st-emotion-cache-16idsys p {
    color: #eef4ff !important;
}

div[data-baseweb="select"] *,
.stMultiSelect [data-baseweb="tag"] {
    color: #eef4ff !important;
    background: rgba(255,255,255,0.08) !important;
}

/* Session card */
.session-card {
    background: rgba(16, 38, 79, 0.9);
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: .8rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 10px 22px rgba(0,0,0,.22);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
}
.session-dot {
    width: 44px; height: 44px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary), #2d6a4f 58%, var(--sky));
    color: white;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; flex-shrink: 0;
}

/* Divider */
.divider { border: none; border-top: 1px solid rgba(255,255,255,0.12); margin: 1.5rem 0; }

/* Ambient background elements */
.bg-orb {
    position: fixed;
    border-radius: 50%;
    filter: blur(10px);
    pointer-events: none;
    z-index: 0;
    opacity: 0.95;
}

.bg-orb-1 {
    width: 260px;
    height: 260px;
    top: 110px;
    left: -70px;
    background: radial-gradient(circle at 30% 30%, rgba(242,108,167,0.62), rgba(242,108,167,0.08) 68%, transparent 74%);
}

.bg-orb-2 {
    width: 320px;
    height: 320px;
    top: 240px;
    right: -90px;
    background: radial-gradient(circle at 35% 35%, rgba(105,191,248,0.65), rgba(105,191,248,0.1) 65%, transparent 75%);
}

.bg-orb-3 {
    width: 220px;
    height: 220px;
    bottom: 30px;
    left: 18%;
    background: radial-gradient(circle at 40% 40%, rgba(255,209,102,0.58), rgba(255,209,102,0.08) 66%, transparent 74%);
}

.bg-ribbon {
    position: fixed;
    inset: auto;
    width: 480px;
    height: 480px;
    right: 14%;
    bottom: -180px;
    background: conic-gradient(from 120deg, rgba(242,108,167,0.18), rgba(255,209,102,0.14), rgba(105,191,248,0.18), rgba(242,108,167,0.18));
    border-radius: 38% 62% 53% 47% / 47% 42% 58% 53%;
    filter: blur(28px);
    opacity: 0.8;
    pointer-events: none;
    z-index: 0;
}

[data-testid="stSidebar"],
[data-testid="stAppViewContainer"] .main,
[data-testid="stHeader"] {
    position: relative;
    z-index: 1;
}

.stInfo, .stSuccess, .stWarning, .stError {
    border-radius: 12px;
}

[data-testid="stAppViewContainer"] .main *,
[data-testid="stMain"] * {
    color: inherit;
}

</style>
""", unsafe_allow_html=True)

hero_bg_path = "assets/hero_bg.png"
if os.path.exists(hero_bg_path):
    with open(hero_bg_path, 'rb') as f:
        bg_b64 = base64.b64encode(f.read()).decode()
    hero_bg = f'background: linear-gradient(135deg, rgba(26, 71, 42, 0.85) 0%, rgba(13, 31, 20, 0.95) 100%), url("data:image/png;base64,{bg_b64}") center/cover;'
else:
    hero_bg = 'background: linear-gradient(135deg, #1a472a 0%, #2d6a4f 60%, #1b4332 100%);'

st.markdown(f"""
<style>
.hero {{
    {hero_bg}
    box-shadow: 0 22px 48px rgba(20, 34, 28, 0.18);
    border: 1px solid rgba(255,255,255,0.12);
}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="bg-orb bg-orb-1"></div>
<div class="bg-orb bg-orb-2"></div>
<div class="bg-orb bg-orb-3"></div>
<div class="bg-ribbon"></div>
""", unsafe_allow_html=True)

# ── session-state defaults ────────────────────────────────────────────────────
defaults = {
    "logged_in": False,
    "user_role": None,        # "student" | "mentor"
    "user_email": None,
    "user_name": None,
    "current_page": "home",
    "students": {},           # email → profile dict
    "mentors": {},            # email → profile dict
    "sessions": [],           # list of session dicts
    "matches": {},            # student_email → [mentor_email, …]
    "pending_mentor": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

init_db()
students, mentors, sessions, matches = load_all_data()
st.session_state.students = students
st.session_state.mentors = mentors
st.session_state.sessions = sessions
st.session_state.matches = matches

# ── sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌍 MentorBridge")
    st.markdown("*Connecting Africa's future*")
    st.caption("Created by Onoja")
    st.markdown("[Support this work](https://paypal.me/Onoja412)")
    st.markdown("---")

    if not st.session_state.logged_in:
        public_pages = ["🏠 Home", "📝 Register", "🔑 Login"]
        current_page = st.session_state.get("current_page", "🏠 Home")
        if current_page not in public_pages:
            current_page = "🏠 Home"
        page = st.radio(
            "Navigate",
            public_pages,
            index=public_pages.index(current_page),
        )
        st.session_state.current_page = page
    else:
        role = st.session_state.user_role
        st.markdown(f"👤 **{st.session_state.user_name}**")
        st.markdown(f"`{role.capitalize()}`")
        st.markdown("---")

        if role == "student":
            private_pages = [
                "🏠 Dashboard",
                "👤 My Profile",
                "🤝 Find Mentors",
                "📅 My Sessions",
            ]
        else:
            private_pages = [
                "🏠 Dashboard",
                "👤 My Profile",
                "🎓 My Students",
                "📅 My Sessions",
                "⚙️ Availability",
            ]
        current_page = st.session_state.get("current_page", "🏠 Dashboard")
        if current_page not in private_pages:
            current_page = "🏠 Dashboard"
        page = st.radio(
            "Navigate",
            private_pages,
            index=private_pages.index(current_page),
        )
        st.session_state.current_page = page

        st.markdown("---")
        if st.button("🚪 Logout"):
            for k in ["logged_in", "user_role", "user_email", "user_name"]:
                st.session_state[k] = None if k != "logged_in" else False
            st.rerun()

# ── page routing ──────────────────────────────────────────────────────────────
page = st.session_state.current_page

if "Home" in page and not st.session_state.logged_in:
    from pages import home
    home.render()

elif "Register" in page:
    from pages import register
    register.render()

elif "Login" in page:
    from pages import login
    login.render()

elif st.session_state.logged_in:
    role = st.session_state.user_role

    if "Dashboard" in page:
        from pages import dashboard
        dashboard.render()
    elif "My Profile" in page or "Profile" in page:
        from pages import profile
        profile.render()
    elif "Find Mentors" in page:
        from pages import matching
        matching.render()
    elif "My Students" in page:
        from pages import students_view
        students_view.render()
    elif "My Sessions" in page:
        from pages import sessions
        sessions.render()
    elif "Availability" in page:
        from pages import availability
        availability.render()
else:
    from pages import home
    home.render()
