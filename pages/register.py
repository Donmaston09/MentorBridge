import streamlit as st
import hashlib, datetime
from utils.cv_parser import extract_cv_text, parse_skills_from_text
from utils.storage import save_student, save_mentor

def render():
    if st.session_state.get("pending_mentor"):
        st.markdown("## 🔐 Verify Your Email")
        st.info(f"We have sent a 6-digit OTP code to **{st.session_state.pending_mentor['email']}**.\n\n*(For this demo, the code is **123456**)*")
        
        otp = st.text_input("Enter OTP Code")
        if st.button("Verify & Create Account"):
            if otp == "123456":
                email = st.session_state.pending_mentor['email']
                name = st.session_state.pending_mentor['name']
                st.session_state.mentors[email] = st.session_state.pending_mentor
                save_mentor(st.session_state.pending_mentor)
                del st.session_state.pending_mentor
                
                st.success(f"✅ Welcome, {name}! Your mentor profile is live.")
                st.info("👉 Please log in to access your dashboard.")
                if st.button("Go to Login →"):
                    st.session_state.current_page = "🔑 Login"
                    st.rerun()
            else:
                st.error("Invalid OTP code. Please try again.")
        if st.button("← Cancel & Back"):
            del st.session_state.pending_mentor
            st.rerun()
        return

    st.markdown("## 📝 Create Your Account")
    st.markdown("Join MentorBridge — free mentoring for students, powered by volunteer mentors.")
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    default_role = 0 if st.session_state.get("register_role", "Student") == "Student" else 1
    role = st.radio("I am a …", ["🎓 Student", "👨‍💼 Mentor"], index=default_role, horizontal=True)
    role_key = "student" if "Student" in role else "mentor"

    with st.form("register_form", clear_on_submit=False):
        st.markdown(f"### {'Student' if role_key=='student' else 'Mentor'} Registration")

        c1, c2 = st.columns(2)
        with c1:
            first = st.text_input("First Name *")
            email = st.text_input("Email Address *")
            country = st.selectbox("Country *", [
                "Nigeria", "Ghana", "Kenya", "South Africa", "Ethiopia",
                "Senegal", "Uganda", "Tanzania", "Rwanda", "Cameroon",
                "Egypt", "Morocco", "United Kingdom", "United States",
                "Canada", "Germany", "France", "Other",
            ])
        with c2:
            last = st.text_input("Last Name *")
            password = st.text_input("Password *", type="password")
            phone = st.text_input("Phone (optional)")

        st.markdown("---")

        if role_key == "student":
            st.markdown("#### Academic Details")
            c1, c2 = st.columns(2)
            with c1:
                university = st.text_input("University / Institution *")
                year = st.selectbox("Year of Study *", ["1st Year", "2nd Year", "3rd Year", "4th Year", "5th Year+"])
            with c2:
                course = st.text_input("Course / Programme *")
                gpa = st.text_input("GPA / Grade (optional)")

            goals = st.multiselect("Mentorship Goals *", [
                "Career guidance", "Research support", "Internship/job search",
                "Entrepreneurship", "Graduate school applications",
                "Technical skills", "Leadership", "Networking",
            ])
            interests = st.multiselect("Areas of Interest *", [
                "Technology / Software", "Finance / Banking", "Healthcare / Medicine",
                "Engineering", "Business / Management", "Law", "Education",
                "Public Policy", "Data Science / AI", "Media / Communications",
                "Agriculture", "Energy / Sustainability",
            ])
            cv_file = st.file_uploader("Upload Your CV (PDF or DOCX) *", type=["pdf", "docx"])
            
            st.markdown("#### Commitment")
            student_commitment = st.checkbox(
                "I understand mentoring is free, and I will support MentorBridge with a success payment after securing my first job."
            )
            st.info(
                "There is no subscription. Students can access mentoring for free and are invited to make a first-job success payment once they land their first role."
            )

        else:  # mentor
            st.markdown("#### Professional Details")
            c1, c2 = st.columns(2)
            with c1:
                job_title = st.text_input("Job Title *")
                company = st.text_input("Organisation *")
                years_exp = st.selectbox("Years of Experience *", ["5-7", "8-10", "11-15", "15+"])
            with c2:
                industry = st.selectbox("Industry *", [
                    "Technology / Software", "Finance / Banking", "Healthcare / Medicine",
                    "Engineering", "Academia / Research", "Consulting",
                    "Government / Policy", "NGO / International Dev", "Energy",
                    "Media / Communications", "Other",
                ])
                linkedin = st.text_input("LinkedIn URL (optional)")

            expertise = st.multiselect("Areas of Expertise *", [
                "Career guidance", "Research & Academia", "Entrepreneurship",
                "Technical mentoring", "Graduate school", "Leadership",
                "Networking", "Interview preparation", "CV review",
            ])
            evidence = st.text_input("Evidence of Expertise (Portfolio URL, Webpage, etc) *")
            mentor_cv = st.file_uploader("Upload Your CV (PDF or DOCX) *", type=["pdf", "docx"], key="mentor_cv")
            bio = st.text_area("Short Bio (2–3 sentences) *", height=100,
                               placeholder="Tell students about your background and what drives you to mentor…")

            st.markdown("#### Volunteering & Availability")
            volunteer_commitment = st.checkbox(
                "I understand mentor participation is voluntary and unpaid, and I am joining to support students."
            )
            session_types = st.multiselect("Session Durations Offered *", ["30 minutes", "1 hour"])
            platforms = st.multiselect("Preferred Platform *", ["Microsoft Teams", "Google Meet", "Zoom"])
            max_students = st.slider("Max simultaneous students", 1, 10, 3)

        st.markdown("---")
        agree = st.checkbox("I agree to the Terms of Service and Privacy Policy *")
        submitted = st.form_submit_button("🚀 Create Account", use_container_width=True)

    if submitted:
        # Basic validation
        errors = []
        if not first or not last:     errors.append("Full name required.")
        if not email or "@" not in email: errors.append("Valid email required.")
        if not password or len(password) < 6: errors.append("Password must be 6+ characters.")
        if not agree:                  errors.append("You must accept the Terms.")

        if role_key == "student":
            if not university: errors.append("University required.")
            if not course:     errors.append("Course required.")
            if not goals:      errors.append("Select at least one mentorship goal.")
            if not interests:  errors.append("Select at least one area of interest.")
            if not cv_file:    errors.append("CV upload required.")
            if not student_commitment: errors.append("Please confirm the first-job success payment commitment.")
        else:
            if not job_title:  errors.append("Job title required.")
            if not company:    errors.append("Organisation required.")
            if not expertise:  errors.append("Select at least one area of expertise.")
            if not evidence:   errors.append("Evidence of expertise required.")
            if not mentor_cv:  errors.append("CV upload required.")
            if not bio:        errors.append("Bio required.")
            if not session_types: errors.append("Select at least one session duration.")
            if not platforms:  errors.append("Select at least one platform.")
            if not volunteer_commitment: errors.append("Please confirm that mentoring is voluntary and unpaid.")
            
        if email in st.session_state.students or email in st.session_state.mentors:
            errors.append("An account with this email already exists.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            pw_hash = hashlib.sha256(password.encode()).hexdigest()
            name = f"{first} {last}"

            if role_key == "student":
                # Parse CV
                cv_text = ""
                extracted_skills = []
                if cv_file:
                    cv_text = extract_cv_text(cv_file)
                    extracted_skills = parse_skills_from_text(cv_text)

                st.session_state.students[email] = {
                    "name": name, "email": email, "password": pw_hash,
                    "country": country, "phone": phone,
                    "university": university, "course": course,
                    "year": year, "gpa": gpa,
                    "goals": goals, "interests": interests,
                    "cv_text": cv_text, "skills": extracted_skills,
                    "payment_model": "First job success payment",
                    "first_job_payment_status": "pending",
                    "registered": datetime.date.today().isoformat(),
                    "avatar": first[0].upper() + last[0].upper(),
                }
                save_student(st.session_state.students[email])
                st.success(f"✅ Welcome, {name}! Your student account is ready.")
                st.info(f"🤖 CV analysed — detected skills: {', '.join(extracted_skills[:8]) if extracted_skills else 'No skills auto-detected (you can add them in your profile).'}")
                st.info(
                    "Mentoring is free. When you secure your first job, please support MentorBridge with your success payment and consider backing the creator at paypal.me/Onoja412."
                )

            else:
                cv_text = ""
                extracted_skills = []
                if mentor_cv:
                    cv_text = extract_cv_text(mentor_cv)
                    extracted_skills = parse_skills_from_text(cv_text)

                st.session_state.pending_mentor = {
                    "name": name, "email": email, "password": pw_hash,
                    "country": country, "phone": phone,
                    "job_title": job_title, "company": company,
                    "industry": industry, "years_exp": years_exp,
                    "linkedin": linkedin, "expertise": expertise,
                    "evidence": evidence, "cv_text": cv_text, "skills": extracted_skills,
                    "bio": bio,
                    "mentor_type": "Volunteer Mentor",
                    "session_types": session_types,
                    "platforms": platforms,
                    "max_students": max_students,
                    "availability": {},   # day → list of slots
                    "registered": datetime.date.today().isoformat(),
                    "avatar": first[0].upper() + last[0].upper(),
                    "rating": None, "total_sessions": 0,
                }
                st.rerun()

            if role_key == "student":
                st.info("👉 Please log in to access your dashboard.")
                if st.button("Go to Login →"):
                    st.session_state.current_page = "🔑 Login"
                    st.rerun()
