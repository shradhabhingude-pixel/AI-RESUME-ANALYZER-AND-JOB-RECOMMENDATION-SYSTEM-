"""Streamlit interface for the AI Resume Analyzer."""
from pathlib import Path
import json
import streamlit as st
import plotly.express as px
from job_matcher import load_job_roles, recommend_roles
from roadmap_generator import build_roadmap
from resume_parser import extract_resume_text
from skill_extractor import extract_skills, load_skill_dictionary
from text_cleaner import clean_text
from report_generator import create_analysis_pdf
from resume_sections import extract_resume_sections, find_limited_evidence_skills

ROOT = Path(__file__).parent
MAX_FILE_MB = 5
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")
st.title("AI Resume Analyzer and Job Recommendation System")
st.caption("Educational guidance only. Match scores are estimates, not hiring decisions.")
with st.sidebar:
    st.header("Analyze a resume")
    uploaded = st.file_uploader("Upload a PDF or DOCX", type=["pdf", "docx"])
    st.caption(f"Maximum file size: {MAX_FILE_MB} MB. Files are processed in memory and not saved.")
if uploaded is None:
    st.info("Upload a PDF or DOCX resume to view skills, matches, and a learning roadmap.")
    st.stop()
if uploaded.size > MAX_FILE_MB * 1024 * 1024:
    st.error(f"The file is larger than {MAX_FILE_MB} MB. Please upload a smaller resume.")
    st.stop()
try:
    resume_text = clean_text(extract_resume_text(uploaded.name, uploaded.getvalue()))
except Exception as exc:
    st.error(f"Could not read this resume: {exc}")
    st.stop()
if not resume_text:
    st.error("No readable text was found. Scanned PDFs may need OCR before upload.")
    st.stop()
st.caption(f"Uploaded file: **{uploaded.name}**")
roles = load_job_roles(ROOT / "data" / "job_roles.csv")
dictionary = load_skill_dictionary(ROOT / "data" / "skill_dictionary.csv")
skills = extract_skills(resume_text, dictionary)
sections = extract_resume_sections(resume_text)
limited_evidence = find_limited_evidence_skills(skills, dictionary, sections)
recommendations = recommend_roles(resume_text, skills, roles)
left, right = st.columns(2)
with left:
    st.subheader("Skills found")
    st.write(", ".join(item["skill"] for item in skills) if skills else "No dictionary skills detected.")
    if skills:
        st.caption("Categories: " + ", ".join(sorted({item["category"] for item in skills})))
    if limited_evidence:
        st.warning("Skills listed without a matching project or experience example: " + ", ".join(limited_evidence))
    else:
        st.caption("No skills were flagged as needing more project or experience context.")
with right:
    st.subheader("Role match scores")
    chart = [{"Role": item["role"], "Match score": item["score"]} for item in recommendations[:5]]
    st.plotly_chart(px.bar(chart, x="Match score", y="Role", orientation="h", range_x=[0, 100]), use_container_width=True)
st.subheader("Top three recommended roles")
for i, item in enumerate(recommendations[:3], 1):
    st.markdown(f"**{i}. {item['role']} — {item['score']}%**")
names = [role["role"] for role in roles]
default = recommendations[0]["role"]
target_name = st.selectbox("Select a target role", names, index=names.index(default))
target = next(role for role in roles if role["role"] == target_name)
found = {item["skill"].casefold() for item in skills}
required = target["required_skills"]
matched = [skill for skill in required if skill.casefold() in found]
missing = [skill for skill in required if skill.casefold() not in found]
target_match = next(item for item in recommendations if item["role"] == target_name)
c1, c2, c3 = st.columns(3)
c1.metric("Match estimate", f"{target_match['score']}%")
c2.metric("Required skills found", f"{len(matched)} / {len(required)}")
c3.metric("Missing keywords", len(missing))
st.write("**Detected for role:** " + (", ".join(matched) or "None detected"))
st.write("**Missing keywords:** " + (", ".join(missing) or "No gaps detected"))
st.caption("A missing keyword does not prove you lack the skill. Review the resume and results yourself.")
roadmap = build_roadmap(missing)
st.subheader("Suggested learning roadmap")
for week, topic in roadmap:
    st.write(f"**{week}:** {topic}")
with st.expander("Detected resume sections"):
    for section_name in ("summary", "skills", "experience", "projects", "education", "certifications", "other"):
        section_text = sections.get(section_name)
        if section_text:
            st.markdown(f"**{section_name.title()}**")
            st.write(section_text)
report = {"resume_file": uploaded.name, "target_role": target_name, "match_score_percent": target_match["score"],
          "skills_found": [item["skill"] for item in skills], "required_skills_found": matched,
          "missing_skills": missing, "limited_evidence_skills": limited_evidence,
          "resume_sections": {name: content[:600] for name, content in sections.items()},
          "recommended_roles": recommendations[:3],
          "roadmap": [{"week": week, "topic": topic} for week, topic in roadmap],
          "notice": "Educational estimate only; not a hiring decision."}
pdf_report = create_analysis_pdf(report, resume_text)
st.download_button("Download analysis report (PDF)", pdf_report,
                   file_name="resume_analysis_report.pdf", mime="application/pdf")
with st.expander("Download machine-readable report"):
    st.download_button("Download analysis data (JSON)", json.dumps(report, indent=2),
                       file_name="resume_analysis_report.json", mime="application/json")
with st.expander("View cleaned resume text"):
    st.text_area("Extracted text", resume_text, height=250, disabled=True)
