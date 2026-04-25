import streamlit as st
import datetime
from utils.emailer import email_is_configured, send_booking_invites
from utils.matching import rank_mentors, score_match
from utils.meetings import generate_calendar_event
from utils.storage import replace_matches, save_session, save_mentor

def render():
    st.markdown("## 🤝 Find Your Mentor")
    st.markdown("Our AI engine analyses your CV, goals and interests to surface the best matches.")
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    email   = st.session_state.user_email
    student = st.session_state.students.get(email, {})
    mentors = st.session_state.mentors

    if not mentors:
        st.warning("No mentors are registered yet. Check back soon!")
        return

    # ── Run AI matching ───────────────────────────────────────────────────────
    ranked = rank_mentors(student, mentors)
    # store matches in session state
    st.session_state.matches[email] = [e for e, _ in ranked]
    replace_matches(email, st.session_state.matches[email])

    # ── Filters ───────────────────────────────────────────────────────────────
    with st.expander("🎛️ Filter mentors", expanded=False):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            filter_industry = st.multiselect("Industry", list({m.get("industry","") for m in mentors.values()}))
        with fc2:
            filter_platform = st.multiselect("Platform", ["Microsoft Teams", "Google Meet", "Zoom"])
        with fc3:
            filter_duration = st.multiselect("Session length", ["30 minutes", "1 hour"])
        min_score = st.slider("Minimum match score", 0, 100, 30, step=5)

    # Apply filters
    def passes(mentor_email, score):
        m = mentors[mentor_email]
        if int(score * 100) < min_score:
            return False
        if filter_industry and m.get("industry","") not in filter_industry:
            return False
        if filter_platform:
            if not any(p in m.get("platforms",[]) for p in filter_platform):
                return False
        if filter_duration:
            if not any(d in m.get("session_types",[]) for d in filter_duration):
                return False
        return True

    filtered = [(e, s) for e, s in ranked if passes(e, s)]

    st.markdown(f"**{len(filtered)} mentor{'s' if len(filtered)!=1 else ''} found** · "
                f"Sorted by AI match score")

    if not filtered:
        st.info("No mentors match your current filters. Try adjusting them.")
        return

    # ── Mentor cards ──────────────────────────────────────────────────────────
    for mentor_email, score in filtered:
        mentor = mentors[mentor_email]
        _mentor_card(student, mentor, score)


def _mentor_card(student: dict, mentor: dict, score: float):
    pct = int(score * 100)
    cls = "score-high" if pct >= 70 else ("score-mid" if pct >= 45 else "score-low")
    rating_str = f"⭐ {mentor.get('rating','New')}" if mentor.get("rating") else "⭐ New"
    sessions_str = f"· {mentor.get('total_sessions',0)} sessions"
    avail_days = list(mentor.get("availability", {}).keys())
    pills = "".join(f'<span class="pill">{e}</span>' for e in mentor.get("expertise",[])[:4])

    with st.container():
        st.markdown(f"""
        <div class="mb-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div>
                    <div style="display:flex;align-items:center;gap:.6rem">
                        <div style="width:46px;height:46px;border-radius:50%;background:var(--primary);
                                    color:white;display:flex;align-items:center;justify-content:center;
                                    font-weight:700;font-size:1rem;flex-shrink:0">
                            {mentor.get('avatar','?')}
                        </div>
                        <div>
                            <h3 style="margin:0;font-size:1.1rem">{mentor.get('name','?')}</h3>
                            <div style="font-size:.85rem;color:var(--muted)">
                                {mentor.get('job_title','?')} · {mentor.get('company','?')}
                            </div>
                        </div>
                    </div>
                    <div style="margin-top:.5rem;font-size:.83rem;color:var(--muted)">
                        {rating_str} {sessions_str} · {mentor.get('country','?')} · 
                        {mentor.get('years_exp','?')} yrs exp
                    </div>
                    <div style="margin-top:.5rem">{pills}</div>
                    <p style="margin:.6rem 0 0;font-size:.9rem;color:#444">{mentor.get('bio','')[:160]}…</p>
                </div>
                <span class="score-badge {cls}" style="font-size:1rem;padding:6px 16px;flex-shrink:0">
                    {pct}%
                </span>
            </div>
            <div style="margin-top:.8rem;font-size:.83rem;color:var(--muted)">
                📅 Available: {', '.join(avail_days) if avail_days else 'Contact mentor'} &nbsp;|&nbsp;
                ⏱ {', '.join(mentor.get('session_types',[]))} &nbsp;|&nbsp;
                {'🟦 Teams' if 'Microsoft Teams' in mentor.get('platforms',[]) else ''}
                {'🟩 Meet' if 'Google Meet' in mentor.get('platforms',[]) else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"📅 Book a session with {mentor.get('name','this mentor').split()[0]}"):
            _booking_form(student, mentor)

        st.markdown("")


def _booking_form(student: dict, mentor: dict):
    avail = mentor.get("availability", {})
    if not avail:
        st.warning("This mentor hasn't set availability yet.")
        return

    bc1, bc2, bc3 = st.columns(3)
    with bc1:
        day = st.selectbox("Day", list(avail.keys()),
                           key=f"day_{mentor['email']}")
    with bc2:
        slots = avail.get(day, [])
        time  = st.selectbox("Time slot", slots if slots else ["No slots"],
                             key=f"time_{mentor['email']}")
    with bc3:
        duration = st.selectbox("Duration",
                                mentor.get("session_types", ["30 minutes"]),
                                key=f"dur_{mentor['email']}")

    platforms = mentor.get("platforms", ["Google Meet"])
    platform = st.selectbox("Platform", platforms, key=f"plat_{mentor['email']}")

    # Compute next occurrence of chosen day
    days_map = {"Monday":0,"Tuesday":1,"Wednesday":2,"Thursday":3,
                "Friday":4,"Saturday":5,"Sunday":6}
    today   = datetime.date.today()
    target  = days_map.get(day, 0)
    delta   = (target - today.weekday()) % 7
    if delta == 0:
        delta = 7
    session_date = (today + datetime.timedelta(days=delta)).isoformat()

    note = st.text_area("Message to mentor (optional)",
                        placeholder="Tell the mentor what you'd like to focus on…",
                        key=f"note_{mentor['email']}", height=80)

    if st.button(f"✅ Confirm booking", key=f"book_{mentor['email']}"):
        if time == "No slots":
            st.error("No available slots for this day.")
            return
        event = generate_calendar_event(platform, student, mentor,
                                        session_date, time, duration)
        event["note"] = note
        saved_event = save_session(event)
        st.session_state.sessions.append(saved_event)
        mentor["total_sessions"] = mentor.get("total_sessions", 0) + 1
        st.session_state.mentors[mentor["email"]] = mentor
        save_mentor(mentor)
        st.success(f"🎉 Session booked for **{session_date} at {time}** on {platform}!")
        st.markdown(f"**Meeting link:** [{saved_event['link']}]({saved_event['link']})")
        sent, message = send_booking_invites(student, mentor, saved_event)
        if sent:
            st.success("Calendar invite emails were sent to both the mentor and the mentee.")
        elif email_is_configured():
            st.warning(f"The session was booked, but invite emails could not be sent: {message}")
        else:
            st.info("The session was booked. Set SMTP environment variables to email invites automatically.")
