import streamlit as st

def render():
    st.markdown("""
    <div class="hero">
        <h1>MentorBridge 🌍</h1>
        <p>AI-powered mentorship connecting African undergraduate students<br>
        with volunteer mentors — inside and beyond the continent.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label in zip(
        [c1, c2, c3, c4],
        ["2,400+", "380+", "54", "92%"],
        ["Students", "Mentors", "Countries", "Satisfaction"],
    ):
        col.markdown(f"""
        <div class="metric-tile">
            <div class="value">{val}</div>
            <div class="label">{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### How it works")
        steps = [
            ("📋", "Register & upload your CV", "Students create a profile and upload their CV for AI analysis."),
            ("🤖", "AI matching", "Our ML engine scores compatibility across skills, goals & industry."),
            ("📅", "Book a session", "Choose 30-min or 1-hour slots on Teams or Google Meet."),
            ("🚀", "Grow together", "Get free personalised coaching and, after your first job, give back through a success payment."),
        ]
        for icon, title, desc in steps:
            st.markdown(f"""
            <div class="mb-card">
                <h3>{icon} {title}</h3>
                <p style="margin:0;color:#555;font-size:.92rem">{desc}</p>
            </div>""", unsafe_allow_html=True)

    with col_b:
        st.markdown("### Featured mentors")
        mentors = [
            ("Dr Amara Diallo", "AI/ML Research", "Senegal 🇸🇳", ["Machine Learning", "Python", "NLP"]),
            ("Ngozi Okonkwo", "FinTech & Banking", "Nigeria 🇳🇬", ["Finance", "Excel", "Strategy"]),
            ("Kwame Mensah", "Software Engineering", "Ghana 🇬🇭 → UK 🇬🇧", ["React", "Node.js", "Cloud"]),
            ("Dr Fatima Al-Amin", "Public Health", "Sudan 🇸🇩 → USA 🇺🇸", ["Research", "Epidemiology"]),
        ]
        for name, role, loc, tags in mentors:
            pills = "".join(f'<span class="pill">{t}</span>' for t in tags)
            st.markdown(f"""
            <div class="mb-card">
                <h3 style="margin-bottom:2px">{name}</h3>
                <div style="color:var(--muted);font-size:.85rem">{role} · {loc}</div>
                <div style="margin-top:.5rem">{pills}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("### Community model")
    st.markdown("""
    <div class="mb-card">
        <h3>Free mentoring. Volunteer mentors. Pay-it-forward impact.</h3>
        <p style="margin:0;color:#555;font-size:.92rem">
            Students receive mentoring at no cost. Mentors volunteer their time to open doors, build confidence,
            and help students prepare for real opportunities. When students secure their first job, they are invited
            to make a success payment to support MentorBridge and help the community grow.
        </p>
    </div>
    <div class="mb-card">
        <h3>Created by Onoja</h3>
        <p style="margin:0;color:#555;font-size:.92rem">
            If you believe in this work, you can support the creator directly via
            <a href="https://paypal.me/Onoja412" target="_blank">paypal.me/Onoja412</a>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("#### Ready to start your journey?")
        ca, cb = st.columns(2)
        with ca:
            if st.button("📝 Register as Student", use_container_width=True, type="primary"):
                st.session_state.register_role = "Student"
                st.session_state.current_page = "📝 Register"
                st.rerun()
        with cb:
            if st.button("🎓 Join as Mentor", use_container_width=True, type="primary"):
                st.session_state.register_role = "Mentor"
                st.session_state.current_page = "📝 Register"
                st.rerun()
