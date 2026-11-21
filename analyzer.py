import io
import re
import numpy as np
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



# Curated technical & analytics skill bank (easily expandable)
SKILL_BANK = [
    "python", "sql", "pandas", "numpy", "scikit-learn", "machine learning",
    "deep learning", "nlp", "data analysis", "exploratory data analysis",
    "eda", "statistics", "power bi", "tableau", "excel", "matplotlib",
    "seaborn", "streamlit", "git", "github", "docker", "fastapi", "flask",
    "mongodb", "postgresql", "mysql", "spark", "big data", "computer vision",
    "opencv", "tensorflow", "pytorch", "feature engineering", "data visualization"
]

SAMPLE_RESUME = """
Soyam Singh
B.Tech Computer Science and Engineering (Data Science)
Skills: Python, Pandas, NumPy, Matplotlib, Seaborn, Scikit-Learn, Streamlit, SQL, MS Excel, Git, GitHub.
Experience & Projects:
- Built an interactive Zomato Exploratory Data Analysis and Rating Predictor web app using Python, Scikit-Learn, and Streamlit.
- Performed data cleaning, feature engineering, and statistical analysis on structured datasets.
- Collaborated on a computer vision and data science minor project focusing on model evaluation and real-time inference.
"""

SAMPLE_JD = """
We are looking for a Junior Data Scientist / Data Analyst with strong skills in Python, SQL, Pandas,
and Scikit-Learn. Experience with Exploratory Data Analysis (EDA), feature engineering, data visualization
(Power BI, Matplotlib, or Seaborn), and building interactive dashboards or web apps using Streamlit is a plus.
Familiarity with Git, Docker, and basic Machine Learning workflows is desirable.
"""


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_skills(text: str) -> list[str]:
    cleaned = f" {clean_text(text)} "
    found = []
    for skill in SKILL_BANK:
        pattern = r"(?<![a-z0-9+#])" + re.escape(skill) + r"(?![a-z0-9+#])"
        if re.search(pattern, cleaned):
            found.append(skill)
    return sorted(set(found))


def compute_similarity_score(resume_text: str, jd_text: str) -> float:
    r_clean = clean_text(resume_text)
    j_clean = clean_text(jd_text)
    if not r_clean or not j_clean:
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform([r_clean, j_clean])
    sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

    # Blend TF-IDF cosine similarity with skill overlap for practical interpretability
    jd_skills = set(extract_skills(jd_text))
    resume_skills = set(extract_skills(resume_text))
    if jd_skills:
        skill_ratio = len(jd_skills & resume_skills) / len(jd_skills)
        blended = (0.45 * sim) + (0.55 * skill_ratio)
    else:
        blended = sim

    return round(float(np.clip(blended * 100, 0, 100)), 1)


def analyze_resume_jd(resume_text: str, jd_text: str) -> dict:
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    matched_skills = sorted(set(resume_skills) & set(jd_skills))
    missing_skills = sorted(set(jd_skills) - set(resume_skills))
    extra_skills = sorted(set(resume_skills) - set(jd_skills))

    base_score = compute_similarity_score(resume_text, jd_text)

    return {
        "match_score": base_score,
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "extra_skills": extra_skills,
    }


def simulate_what_if(resume_text: str, jd_text: str, added_skills: list[str]) -> float:
    if not added_skills:
        return compute_similarity_score(resume_text, jd_text)
    augmented_resume = resume_text + "\nAdditional Skills: " + ", ".join(added_skills)
    return compute_similarity_score(augmented_resume, jd_text)

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract readable text from an uploaded PDF file object."""
    reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
    pages_text = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages_text.append(page_text)
    return "\n".join(pages_text).strip()