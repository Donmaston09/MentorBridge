import streamlit as st
from utils.storage import save_student, save_mentor

def render():
    role  = st.session_state.user_role
    email = st.session_state.user_email

    st.markdown("## 👤 My Profile")

    if role == "student":
        _student_profile(email)
    else:
        _mentor_profile(email)


def _student_profile(email):
    profile = st.session_state.students.get(email, {})

    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown(f"""
        <div style="text-align:center;padding:1.5rem;background:var(--primary);
                    border-radius:16px;color:white">
            <div style="width:80px;height:80px;border-radius:50%;background:var(--accent);
                        color:var(--dark);display:flex;align-items:center;justify-content:center;
                        font-size:2rem;font-weight:700;margin:0 auto .8rem">
                {profile.get('avatar','?')}
            </div>
            <h3 style="color:white;margin:.3rem 0">{profile.get('name','')}</h3>
            <div style="opacity:.8;font-size:.9rem">{profile.get('course','')}</div>
            <div style="opacity:.7;font-size:.83rem">{profile.get('university','')}</div>
            <div style="opacity:.7;font-size:.83rem;margin-top:.3rem">{profile.get('country','')}</div>
            <div style="margin-top:.8rem;background:rgba(255,255,255,0.15);padding:.4rem 1rem;border-radius:20px;font-size:0.85rem;font-weight:bold;">
                Free Mentoring
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        with st.form("edit_student_profile"):
            st.markdown("### Edit Profile")
            c1, c2 = st.columns(2)
            with c1:
                university = st.text_input("University", value=profile.get("university",""))
                year = st.selectbox("Year", ["1st Year","2nd Year","3rd Year","4th Year","5th Year+"],
                                    index=["1st Year","2nd Year","3rd Year","4th Year","5th Year+"].index(
                                        profile.get("year","1st Year")))
            with c2:
                course = st.text_input("Course", value=profile.get("course",""))
                gpa    = st.text_input("GPA / Grade", value=profile.get("gpa",""))

            goals = st.multiselect("Mentorship Goals", [
                "Career guidance","Research support","Internship/job search",
                "Entrepreneurship","Graduate school applications",
                "Technical skills","Leadership","Networking",
            ], default=profile.get("goals",[]))
            interests = st.multiselect("Areas of Interest", [
                "Technology / Software","Finance / Banking","Healthcare / Medicine",
                "Engineering","Business / Management","Law","Education",
                "Public Policy","Data Science / AI","Media / Communications",
                "Agriculture","Energy / Sustainability",
            ], default=profile.get("interests",[]))

            st.markdown("##### Manual Skills (in addition to CV-detected)")
            manual_skills = st.text_input("Skills (comma-separated)",
                                          value=", ".join(profile.get("skills",[])))

            saved = st.form_submit_button("💾 Save Changes")

        if saved:
            profile.update({
                "university": university, "year": year,
                "course": course, "gpa": gpa,
                "goals": goals, "interests": interests,
                "skills": [s.strip() for s in manual_skills.split(",") if s.strip()],
            })
            st.session_state.students[email] = profile
            save_student(profile)
            st.success("Profile updated!")

    # CV skills
    st.markdown("---")
    st.info(
        "Mentoring stays free while you learn. Once you secure your first job, you can complete your success payment and support the creator at paypal.me/Onoja412."
    )
    st.markdown("---")
    st.markdown("### 🏅 Detected Skills")
    skills = profile.get("skills", [])
    if skills:
        pills = "".join(f'<span class="pill">{s}</span>' for s in skills)
        st.markdown(pills, unsafe_allow_html=True)
    else:
        st.info("Upload a CV to auto-detect skills, or add them manually above.")


def _mentor_profile(email):
    profile = st.session_state.mentors.get(email, {})

    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown(f"""
        <div style="text-align:center;padding:1.5rem;background:var(--primary);
                    border-radius:16px;color:white">
            <div style="width:80px;height:80px;border-radius:50%;background:var(--accent);
                        color:var(--dark);display:flex;align-items:center;justify-content:center;
                        font-size:2rem;font-weight:700;margin:0 auto .8rem">
                {profile.get('avatar','?')}
            </div>
            <h3 style="color:white;margin:.3rem 0">{profile.get('name','')}</h3>
            <div style="opacity:.8;font-size:.9rem">{profile.get('job_title','')}</div>
            <div style="opacity:.7;font-size:.83rem">{profile.get('company','')}</div>
            <div style="opacity:.7;font-size:.83rem;margin-top:.3rem">{profile.get('country','')}</div>
            <div style="margin-top:.6rem;font-size:.85rem">
                ⭐ {profile.get('rating','New')} · {profile.get('total_sessions',0)} sessions
            </div>
            <div style="margin-top:.8rem;background:rgba(255,255,255,0.15);padding:.4rem 1rem;border-radius:20px;font-size:0.85rem;font-weight:bold;">
                {profile.get('mentor_type', 'Volunteer Mentor')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        with st.form("edit_mentor_profile"):
            st.markdown("### Edit Profile")
            c1, c2 = st.columns(2)
            with c1:
                job_title = st.text_input("Job Title", value=profile.get("job_title",""))
                company   = st.text_input("Organisation", value=profile.get("company",""))
            with c2:
                industry  = st.selectbox("Industry", [
                    "Technology / Software","Finance / Banking","Healthcare / Medicine",
                    "Engineering","Academia / Research","Consulting",
                    "Government / Policy","NGO / International Dev","Energy",
                    "Media / Communications","Other",
                ], index=0)
                linkedin  = st.text_input("LinkedIn URL", value=profile.get("linkedin",""))

            expertise = st.multiselect("Areas of Expertise", [
                "Career guidance","Research & Academia","Entrepreneurship",
                "Technical mentoring","Graduate school","Leadership",
                "Networking","Interview preparation","CV review",
            ], default=profile.get("expertise",[]))

            bio = st.text_area("Bio", value=profile.get("bio",""), height=100)

            mentor_type = st.selectbox("Mentor Role", ["Volunteer Mentor"], index=0)

            saved = st.form_submit_button("💾 Save Changes")

        if saved:
            profile.update({
                "job_title": job_title, "company": company,
                "industry": industry, "linkedin": linkedin,
                "expertise": expertise, "bio": bio,
                "mentor_type": mentor_type,
            })
            st.session_state.mentors[email] = profile
            save_mentor(profile)
            st.success("Profile updated!")

    st.markdown("---")
    st.markdown("### 🏅 Expertise Tags")
    pills = "".join(f'<span class="pill">{e}</span>' for e in profile.get("expertise",[]))
    st.markdown(pills or "—", unsafe_allow_html=True)
