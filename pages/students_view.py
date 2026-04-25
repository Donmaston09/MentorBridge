import streamlit as st
from utils.matching import score_match

def render():
    st.markdown("## 🎓 My Students")
    email = st.session_state.user_email
    mentor = st.session_state.mentors.get(email, {})

    # Find students who have booked sessions with this mentor
    student_emails = list({s["student_email"] for s in st.session_state.sessions
                            if s.get("mentor_email") == email})

    if not student_emails:
        st.info("No students have booked with you yet. Make sure your availability is set and your profile is complete!")
        return

    st.markdown(f"**{len(student_emails)} student{'s' if len(student_emails)!=1 else ''}** currently connected")
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    for s_email in student_emails:
        student = st.session_state.students.get(s_email, {})
        if not student:
            continue
        score = score_match(student, mentor)
        pct   = int(score * 100)
        cls   = "score-high" if pct >= 70 else ("score-mid" if pct >= 45 else "score-low")
        pills = "".join(f'<span class="pill">{sk}</span>' for sk in student.get("skills",[])[:6])
        sessions_together = [s for s in st.session_state.sessions
                             if s.get("student_email")==s_email and s.get("mentor_email")==email]

        st.markdown(f"""
        <div class="mb-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div style="display:flex;gap:.8rem;align-items:flex-start">
                    <div style="width:50px;height:50px;border-radius:50%;background:var(--primary);
                                color:white;display:flex;align-items:center;justify-content:center;
                                font-weight:700;font-size:1.1rem;flex-shrink:0">
                        {student.get('avatar','?')}
                    </div>
                    <div>
                        <strong style="font-size:1.05rem">{student.get('name','?')}</strong>
                        <div style="font-size:.85rem;color:var(--muted)">
                            {student.get('course','?')} · {student.get('university','?')} · {student.get('year','?')}
                        </div>
                        <div style="font-size:.83rem;color:var(--muted);margin-top:.2rem">
                            🎯 Goals: {', '.join(student.get('goals',[])[:3])}
                        </div>
                        <div style="margin-top:.4rem">{pills}</div>
                    </div>
                </div>
                <div style="text-align:right">
                    <span class="score-badge {cls}">{pct}% match</span>
                    <div style="font-size:.82rem;color:var(--muted);margin-top:.3rem">
                        📅 {len(sessions_together)} session{'s' if len(sessions_together)!=1 else ''}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"📋 Session history with {student.get('name','').split()[0]}"):
            if sessions_together:
                for s in sorted(sessions_together, key=lambda x: x.get("date",""), reverse=True):
                    platform_icon = "🟦" if "Teams" in s.get("platform","") else "🟩"
                    st.markdown(f"- **{s.get('date','?')}** at {s.get('time','?')} · "
                                f"{s.get('duration','?')} · {platform_icon} {s.get('platform','?')} · "
                                f"_{s.get('status','?').capitalize()}_")
            else:
                st.caption("No sessions yet.")
