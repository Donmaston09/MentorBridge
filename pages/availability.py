import streamlit as st
from utils.storage import save_mentor

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SLOTS = [f"{h:02d}:{m:02d}" for h in range(7, 23) for m in (0, 30)]

def render():
    st.markdown("## ⚙️ Manage Availability")
    st.markdown("Set the days and time slots when students can book sessions with you.")
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    email  = st.session_state.user_email
    mentor = st.session_state.mentors.get(email, {})
    avail  = mentor.get("availability", {})

    st.markdown("### Weekly Availability")
    st.caption("Select the time slots you are available each day (leave empty to mark as unavailable).")

    updated = {}
    for day in DAYS:
        existing = avail.get(day, [])
        chosen = st.multiselect(
            day,
            SLOTS,
            default=existing,
            key=f"avail_{day}",
        )
        if chosen:
            updated[day] = chosen

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Session Types")
        session_types = st.multiselect(
            "Durations you offer",
            ["30 minutes", "1 hour"],
            default=mentor.get("session_types", ["30 minutes"]),
            key="av_session_types",
        )
    with col2:
        st.markdown("### Platforms")
        platforms = st.multiselect(
            "Where you host sessions",
            ["Microsoft Teams", "Google Meet", "Zoom"],
            default=mentor.get("platforms", ["Google Meet"]),
            key="av_platforms",
        )

    st.markdown("### Student Capacity")
    max_s = st.slider("Max simultaneous students", 1, 15,
                      mentor.get("max_students", 3), key="av_max_students")

    if st.button("💾 Save Availability", use_container_width=True):
        mentor["availability"]  = updated
        mentor["session_types"] = session_types
        mentor["platforms"]     = platforms
        mentor["max_students"]  = max_s
        st.session_state.mentors[email] = mentor
        save_mentor(mentor)
        st.success("✅ Availability updated successfully!")

    # Preview
    if updated:
        st.markdown("---")
        st.markdown("### 📋 Your Availability Preview")
        for day, slots in updated.items():
            st.markdown(f"**{day}:** " + " · ".join(slots))
