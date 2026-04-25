import streamlit as st
import hashlib
from utils.storage import save_student, save_mentor

def render():
    st.markdown("## 🔑 Log In")

    c1, _, c3 = st.columns([1, .15, 1])

    with c1:
        st.markdown("### Student Login")
        with st.form("student_login"):
            s_email = st.text_input("Email", key="sl_email")
            s_pass  = st.text_input("Password", type="password", key="sl_pass")
            s_sub   = st.form_submit_button("Login as Student", use_container_width=True)

        if s_sub:
            ph = hashlib.sha256(s_pass.encode()).hexdigest()
            students = st.session_state.get("students", {})
            if s_email in students and students[s_email]["password"] == ph:
                st.session_state.logged_in = True
                st.session_state.user_role = "student"
                st.session_state.user_email = s_email
                st.session_state.user_name = students[s_email]["name"]
                st.session_state.current_page = "🏠 Dashboard"
                st.rerun()
            else:
                st.error("Invalid email or password.")

    with c3:
        st.markdown("### Mentor Login")
        with st.form("mentor_login"):
            m_email = st.text_input("Email", key="ml_email")
            m_pass  = st.text_input("Password", type="password", key="ml_pass")
            m_sub   = st.form_submit_button("Login as Mentor", use_container_width=True)

        if m_sub:
            ph = hashlib.sha256(m_pass.encode()).hexdigest()
            mentors = st.session_state.get("mentors", {})
            if m_email in mentors and mentors[m_email]["password"] == ph:
                st.session_state.logged_in = True
                st.session_state.user_role = "mentor"
                st.session_state.user_email = m_email
                st.session_state.user_name = mentors[m_email]["name"]
                st.session_state.current_page = "🏠 Dashboard"
                st.rerun()
            else:
                st.error("Invalid email or password.")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("Don't have an account?")
    if st.button("📝 Register here"):
        st.session_state.current_page = "📝 Register"
        st.rerun()

    # Demo quick-login
    st.markdown("---")
    with st.expander("🧪 Demo accounts (pre-filled)"):
        st.markdown("""
        **Demo Student** — email: `student@demo.com`  password: `demo123`  
        **Demo Mentor** — email: `mentor@demo.com`  password: `demo123`
        """)
        if st.button("Create & load demo accounts"):
            _seed_demo()
            st.success("Demo accounts ready! Use the forms above to log in.")

def _seed_demo():
    import hashlib, datetime
    ph = hashlib.sha256(b"demo123").hexdigest()

    if "student@demo.com" not in st.session_state.students:
        st.session_state.students["student@demo.com"] = {
            "name": "Amina Kofi", "email": "student@demo.com", "password": ph,
            "country": "Ghana", "phone": "",
            "university": "University of Ghana", "course": "BSc Computer Science",
            "year": "3rd Year", "gpa": "3.7",
            "goals": ["Career guidance", "Technical skills", "Internship/job search"],
            "interests": ["Technology / Software", "Data Science / AI"],
            "cv_text": "Python, Machine Learning, Data Analysis, SQL, Research",
            "skills": ["Python", "Machine Learning", "SQL", "Data Analysis", "Research"],
            "payment_model": "First job success payment",
            "first_job_payment_status": "pending",
            "registered": datetime.date.today().isoformat(),
            "avatar": "AK",
        }
        save_student(st.session_state.students["student@demo.com"])

    demo_mentors = [
        {
            "name": "Dr James Osei", "email": "mentor@demo.com", "password": ph,
            "country": "United Kingdom", "phone": "",
            "job_title": "Senior Data Scientist", "company": "DeepMind",
            "industry": "Technology / Software", "years_exp": "7-10",
            "linkedin": "", "expertise": ["Technical mentoring", "Career guidance", "Research & Academia"],
            "bio": "Ghanaian data scientist at DeepMind. Passionate about nurturing African AI talent.",
            "mentor_type": "Volunteer Mentor",
            "session_types": ["30 minutes", "1 hour"],
            "platforms": ["Google Meet", "Microsoft Teams"],
            "max_students": 5,
            "availability": {
                "Monday": ["09:00", "10:00", "14:00", "16:00"],
                "Wednesday": ["11:00", "15:00"],
                "Friday": ["09:00", "13:00"],
            },
            "registered": datetime.date.today().isoformat(),
            "avatar": "JO",
            "rating": 4.9, "total_sessions": 47,
        },
        {
            "name": "Ngozi Okonkwo", "email": "ngozi@demo.com", "password": ph,
            "country": "United States", "phone": "",
            "job_title": "VP of Finance", "company": "Goldman Sachs",
            "industry": "Finance / Banking", "years_exp": "10+",
            "linkedin": "", "expertise": ["Career guidance", "Leadership", "Networking"],
            "bio": "Nigerian finance executive helping students break into global banking.",
            "mentor_type": "Volunteer Mentor",
            "session_types": ["30 minutes"],
            "platforms": ["Microsoft Teams"],
            "max_students": 3,
            "availability": {
                "Tuesday": ["18:00", "19:00"],
                "Thursday": ["17:00", "18:00", "19:00"],
                "Saturday": ["10:00", "11:00", "12:00"],
            },
            "registered": datetime.date.today().isoformat(),
            "avatar": "NO",
            "rating": 4.7, "total_sessions": 31,
        },
        {
            "name": "Dr Fatima Al-Amin", "email": "fatima@demo.com", "password": ph,
            "country": "United States", "phone": "",
            "job_title": "Public Health Researcher", "company": "Johns Hopkins",
            "industry": "Healthcare / Medicine", "years_exp": "7-10",
            "linkedin": "", "expertise": ["Research & Academia", "Graduate school", "Career guidance"],
            "bio": "Sudanese-American researcher supporting the next generation of African public health leaders.",
            "mentor_type": "Volunteer Mentor",
            "session_types": ["30 minutes", "1 hour"],
            "platforms": ["Google Meet"],
            "max_students": 2,
            "availability": {
                "Wednesday": ["14:00", "15:00", "16:00"],
                "Friday": ["13:00", "14:00"],
            },
            "registered": datetime.date.today().isoformat(),
            "avatar": "FA",
            "rating": 4.8, "total_sessions": 19,
        },
    ]
    for m in demo_mentors:
        if m["email"] not in st.session_state.mentors:
            st.session_state.mentors[m["email"]] = m
            save_mentor(m)
