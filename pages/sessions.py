import streamlit as st
import datetime

def render():
    st.markdown("## 📅 My Sessions")
    email = st.session_state.user_email
    role  = st.session_state.user_role

    key = "student_email" if role == "student" else "mentor_email"
    all_sessions = [s for s in st.session_state.sessions if s.get(key) == email]

    today = datetime.date.today().isoformat()
    upcoming = [s for s in all_sessions if s.get("date","") >= today and s.get("status") != "cancelled"]
    past     = [s for s in all_sessions if s.get("date","") < today or s.get("status") == "completed"]

    tab1, tab2 = st.tabs([f"⏳ Upcoming ({len(upcoming)})", f"✅ Past ({len(past)})"])

    with tab1:
        if not upcoming:
            st.info("No upcoming sessions." + (" Browse mentors to book one!" if role=="student" else " Share your availability link!"))
        for s in sorted(upcoming, key=lambda x: x.get("date","")):
            _session_card(s, role, show_join=True)

    with tab2:
        if not past:
            st.info("No past sessions yet.")
        for s in sorted(past, key=lambda x: x.get("date",""), reverse=True):
            _session_card(s, role, show_join=False)


def _session_card(s: dict, role: str, show_join: bool):
    if role == "student":
        other  = st.session_state.mentors.get(s.get("mentor_email",""), {})
        label  = "Mentor"
    else:
        other  = st.session_state.students.get(s.get("student_email",""), {})
        label  = "Student"

    platform_icon = "🟦" if "Teams" in s.get("platform","") else "🟩"
    status_color  = {"confirmed":"#27ae60","cancelled":"#c0392b","completed":"#888"}.get(
                        s.get("status","confirmed"), "#27ae60")

    st.markdown(f"""
    <div class="mb-card" style="padding:1.2rem 1.5rem">
        <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
                <strong style="font-size:1.05rem">{other.get('name','Unknown')}</strong>
                <span style="font-size:.78rem;background:{status_color};color:white;
                      border-radius:10px;padding:2px 10px;margin-left:.6rem">
                    {s.get('status','confirmed').capitalize()}
                </span>
                <div style="font-size:.88rem;color:var(--muted);margin-top:.3rem">
                    📅 {s.get('date','?')} &nbsp;·&nbsp; 🕐 {s.get('time','?')} &nbsp;·&nbsp;
                    ⏱ {s.get('duration','?')} &nbsp;·&nbsp; {platform_icon} {s.get('platform','?')}
                </div>
                {f"<div style='font-size:.83rem;margin-top:.3rem;color:#555'>📝 {s.get('note','')[:120]}</div>" if s.get('note') else ''}
            </div>
            {'<a href="' + s.get("link","#") + '" target="_blank" style="background:var(--accent);color:var(--dark);padding:7px 18px;border-radius:8px;font-weight:600;text-decoration:none;font-size:.9rem">Join →</a>' if show_join else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)
