import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from analyzer import (
    SAMPLE_RESUME,
    SAMPLE_JD,
    analyze_resume_jd,
    simulate_what_if,
    extract_text_from_pdf,
)

st.set_page_config(
    page_title="Resume & JD Skill Gap Analyzer",
    page_icon="🎯",
    layout="wide",
)
sns.set_theme(style="whitegrid")

st.title("🎯 Resume-to-JD Match & Skill Gap Analyzer")
st.caption("Interactive NLP & Skill-Gap Simulator built with Python, Scikit-Learn, Matplotlib, and Streamlit")

# Sample loader buttons
col_s1, col_s2, _ = st.columns([1, 1, 4])
if "resume_input" not in st.session_state:
    st.session_state.resume_input = SAMPLE_RESUME.strip()
if "jd_input" not in st.session_state:
    st.session_state.jd_input = SAMPLE_JD.strip()

with col_s1:
    if st.button("Load Sample Data"):
        st.session_state.resume_input = SAMPLE_RESUME.strip()
        st.session_state.jd_input = SAMPLE_JD.strip()
        st.rerun()

with col_s2:
    if st.button("Clear Inputs"):
        st.session_state.resume_input = ""
        st.session_state.jd_input = ""
        st.rerun()

col_left, col_right = st.columns(2)

with col_left:
    uploaded_pdf = st.file_uploader("📎 Upload Resume (PDF)", type=["pdf"])
    if uploaded_pdf is not None:
        file_key = f"{uploaded_pdf.name}_{uploaded_pdf.size}"
        if st.session_state.get("last_uploaded_pdf") != file_key:
            try:
                extracted = extract_text_from_pdf(uploaded_pdf)
                if extracted:
                    st.session_state.resume_input = extracted
                    st.session_state.last_uploaded_pdf = file_key
                    st.success(f"Extracted text from `{uploaded_pdf.name}`!")
                    st.rerun()
                else:
                    st.warning("PDF se text nahi mil paya. Aap text paste kar sakte hain.")
            except Exception as e:
                st.error(f"PDF read error: {e}")

    resume_text = st.text_area(
        "📄 Paste Resume Text",
        value=st.session_state.resume_input,
        height=220,
        placeholder="Upload a PDF above or paste resume content here...",
    )
    

with col_right:
    jd_text = st.text_area(
        "💼 Paste Job Description (JD)",
        value=st.session_state.jd_input,
        height=240,
        placeholder="Paste target job description here...",
    )

if st.button("🚀 Analyze Match & Skill Gaps", type="primary"):
    if not resume_text.strip() or not jd_text.strip():
        st.warning("Kripya Resume aur Job Description dono mein text daalein.")
    else:
        result = analyze_resume_jd(resume_text, jd_text)
        st.session_state.analysis_result = result
        st.session_state.analyzed_resume = resume_text
        st.session_state.analyzed_jd = jd_text

if "analysis_result" in st.session_state:
    res = st.session_state.analysis_result
    st.divider()

    # Top KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Overall Match Score", f"{res['match_score']}%")
    k2.metric("Matched JD Skills", len(res["matched_skills"]))
    k3.metric("Missing JD Skills", len(res["missing_skills"]))
    k4.metric("Bonus Resume Skills", len(res["extra_skills"]))

    # Skill Lists & Chart
    c_skills, c_chart = st.columns([1.2, 1])

    with c_skills:
        st.subheader("✅ Matched Skills")
        if res["matched_skills"]:
            st.write(", ".join([f"`{s}`" for s in res["matched_skills"]]))
        else:
            st.info("No direct skill overlap detected yet.")

        st.subheader("⚠️ Missing Skills (From JD)")
        if res["missing_skills"]:
            st.write(", ".join([f"`{s}`" for s in res["missing_skills"]]))
        else:
            st.success("All detected JD skills are present in the resume!")

        st.subheader("✨ Additional Skills in Resume")
        if res["extra_skills"]:
            st.write(", ".join([f"`{s}`" for s in res["extra_skills"]]))
        else:
            st.caption("None outside the JD skill list.")

    with c_chart:
        st.subheader("📊 Skill Coverage Breakdown")
        labels = ["Matched Skills", "Missing Skills", "Bonus Skills"]
        counts = [
            len(res["matched_skills"]),
            len(res["missing_skills"]),
            len(res["extra_skills"]),
        ]
        fig, ax = plt.subplots(figsize=(5, 3.5))
        sns.barplot(x=labels, y=counts, ax=ax, palette=["#2e7d32", "#c62828", "#1565c0"])
        ax.set_ylabel("Skill Count")
        ax.set_xlabel("")
        st.pyplot(fig)
        plt.close(fig)

    # Interactive What-If Simulator
    st.divider()
    st.subheader("🔮 Interactive 'What-If' Match Score Simulator")
    st.markdown("Select missing skills below to see how adding them impacts the match score:")

    if res["missing_skills"]:
        selected_boost_skills = st.multiselect(
            "Simulate adding missing skills to resume:",
            options=res["missing_skills"],
            default=res["missing_skills"][:1],
        )
        simulated_score = simulate_what_if(
            st.session_state.analyzed_resume,
            st.session_state.analyzed_jd,
            selected_boost_skills,
        )
        delta = round(simulated_score - res["match_score"], 1)
        st.metric(
            label="Simulated Match Score",
            value=f"{simulated_score}%",
            delta=f"{delta:+.1f}%",
        )
    else:
        st.success("No missing skills to simulate—your resume already covers the detected JD skills!")

       