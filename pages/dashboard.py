import streamlit as st
import datetime

def render():
    role  = st.session_state.user_role
    email = st.session_state.user_email
    name  = st.session_state.user_name

    st.markdown(f"""
    <div class="hero" style="padding:2rem 2.5rem">
        <h1 style="font-size:1.8rem">Welcome back, {name.split()[0]} 👋</h1>
        <p style="margin:0">{'Find your perfect mentor and book a session today.' if role=='student'
           else 'Manage your volunteer mentoring commitments and upcoming coaching sessions.'}</p>
    </div>
    """, unsafe_allow_html=True)

    sessions = [s for s in st.session_state.sessions
                if s.get("student_email") == email or s.get("mentor_email") == email]
    upcoming = [s for s in sessions if s.get("status") == "confirmed"
                and s.get("date", "") >= datetime.date.today().isoformat()]
    past     = [s for s in sessions if s.get("status") == "completed"]

    if role == "student":
        _student_dash(email, upcoming, past)
    else:
        _mentor_dash(email, upcoming, past)

# ─────────────────────────────────────────────
def _student_dash(email, upcoming, past):
    profile  = st.session_state.students.get(email, {})
    matches  = st.session_state.matches.get(email, [])

    c1, c2, c3, c4 = st.columns(4)
    for col, v, l in zip(
        [c1, c2, c3, c4],
        [len(matches), len(upcoming), len(past), profile.get("course","—")],
        ["Mentor Matches", "Upcoming Sessions", "Completed Sessions", "Course"],
    ):
        col.markdown(f"""
        <div class="metric-tile">
            <div class="value">{v}</div>
            <div class="label">{l}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns([1.4, 1])

    with col_a:
        st.markdown("### 📅 Upcoming Sessions")
        if upcoming:
            for s in upcoming[:4]:
                mentor = st.session_state.mentors.get(s["mentor_email"], {})
                _session_row("🎓", mentor.get("name","?"), s)
        else:
            st.info("No upcoming sessions. Find a mentor and book one!")
            if st.button("🤝 Find Mentors"):
                st.session_state.current_page = "🤝 Find Mentors"
                st.rerun()

    with col_b:
        st.markdown("### 🤖 Your Top Matches")
        if matches:
            from utils.matching import score_match
            student = st.session_state.students.get(email, {})
            for m_email in matches[:3]:
                mentor = st.session_state.mentors.get(m_email, {})
                score  = score_match(student, mentor)
                _mentor_mini_card(mentor, score)
        else:
            st.info("Complete your profile and upload your CV to see AI-matched mentors.")

        st.markdown("### 🏆 Skills Detected")
        skills = profile.get("skills", [])
        if skills:
            pills = "".join(f'<span class="pill">{s}</span>' for s in skills[:10])
            st.markdown(pills, unsafe_allow_html=True)
        else:
            st.caption("Upload your CV to auto-detect skills.")

    st.markdown("---")
    st.info("Mentoring is free. After landing your first job, you can make your success payment and support the creator at paypal.me/Onoja412.")

# ─────────────────────────────────────────────
def _mentor_dash(email, upcoming, past):
    profile  = st.session_state.mentors.get(email, {})
    n_students = len(set(s["student_email"] for s in
                         st.session_state.sessions if s.get("mentor_email") == email))

    c1, c2, c3, c4 = st.columns(4)
    for col, v, l in zip(
        [c1, c2, c3, c4],
        [n_students, len(upcoming), len(past), profile.get("rating","—")],
        ["Total Students", "Upcoming", "Completed", "Rating ⭐"],
    ):
        col.markdown(f"""
        <div class="metric-tile">
            <div class="value">{v}</div>
            <div class="label">{l}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns([1.4, 1])

    with col_a:
        st.markdown("### 📅 Upcoming Sessions")
        if upcoming:
            for s in upcoming[:5]:
                student = st.session_state.students.get(s["student_email"], {})
                _session_row("🎓", student.get("name","?"), s)
        else:
            st.info("No upcoming sessions yet. Make sure your availability is set!")
            if st.button("⚙️ Set Availability"):
                st.session_state.current_page = "⚙️ Availability"
                st.rerun()

    with col_b:
        st.markdown("### 📋 Profile Summary")
        avail = profile.get("availability", {})
        st.markdown(f"""
        <div class="mb-card">
            <div style="font-size:.85rem;color:var(--muted)">Job Title</div>
            <strong>{profile.get('job_title','—')}</strong><br><br>
            <div style="font-size:.85rem;color:var(--muted)">Organisation</div>
            <strong>{profile.get('company','—')}</strong><br><br>
            <div style="font-size:.85rem;color:var(--muted)">Available Days</div>
            <strong>{', '.join(avail.keys()) or 'Not set'}</strong><br><br>
            <div style="font-size:.85rem;color:var(--muted)">Session Types</div>
            <strong>{', '.join(profile.get('session_types',[]))}</strong>
        </div>""", unsafe_allow_html=True)

        st.markdown("### 🏅 Expertise")
        pills = "".join(f'<span class="pill">{e}</span>' for e in profile.get("expertise",[]))
        st.markdown(pills or "—", unsafe_allow_html=True)

        st.markdown("### 🤝 Volunteer Status")
        st.success("You are participating as a volunteer mentor. MentorBridge does not pay mentors for sessions.")

# ─────────────────────────────────────────────
def _session_row(icon, other_name, s):
    platform_icon = "🟦" if "Teams" in s.get("platform","") else "🟩"
    st.markdown(f"""
    <div class="session-card">
        <div class="session-dot">{icon}</div>
        <div style="flex:1">
            <strong>{other_name}</strong>
            <div style="font-size:.83rem;color:var(--muted)">
                {s.get('date','?')} at {s.get('time','?')} · {s.get('duration','?')} {platform_icon} {s.get('platform','?')}
            </div>
        </div>
        <a href="{s.get('link','#')}" target="_blank" style="background:var(--accent);color:var(--dark);
           padding:5px 14px;border-radius:8px;font-size:.82rem;text-decoration:none;font-weight:600">
           Join
        </a>
    </div>""", unsafe_allow_html=True)

def _mentor_mini_card(mentor, score):
    pct = int(score * 100)
    cls = "score-high" if pct >= 70 else ("score-mid" if pct >= 45 else "score-low")
    st.markdown(f"""
    <div class="mb-card" style="padding:1rem 1.2rem">
        <div style="display:flex;justify-content:space-between;align-items:center">
            <strong>{mentor.get('name','?')}</strong>
            <span class="score-badge {cls}">{pct}% match</span>
        </div>
        <div style="font-size:.82rem;color:var(--muted)">
            {mentor.get('job_title','?')} · {mentor.get('company','?')}
        </div>
    </div>""", unsafe_allow_html=True)
