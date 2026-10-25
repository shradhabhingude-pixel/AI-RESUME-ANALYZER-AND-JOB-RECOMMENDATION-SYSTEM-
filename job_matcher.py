"""TF-IDF and cosine-similarity job-role recommendations."""
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_job_roles(path: str | Path) -> list[dict[str, object]]:
    roles = []
    for row in pd.read_csv(Path(path)).fillna("").to_dict(orient="records"):
        required = [value.strip() for value in row["required_skills"].split("|") if value.strip()]
        roles.append({"role": row["role"], "description": row["description"], "required_skills": required})
    if not roles:
        raise ValueError("No roles found in data/job_roles.csv.")
    return roles

def recommend_roles(resume_text: str, found_skills: list[dict[str, str]], roles: list[dict[str, object]]) -> list[dict[str, object]]:
    """Rank roles using 65% TF-IDF cosine similarity and 35% skill coverage."""
    skill_names = [item["skill"] for item in found_skills]
    # Only extracted, job-related skills influence ranking. Personal details and
    # unrelated resume text are intentionally excluded from the score.
    resume_doc = " ".join(skill_names)
    role_docs = [f"{r['role']} {r['description']} {' '.join(r['required_skills'])}" for r in roles]
    vectors = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True).fit_transform([resume_doc, *role_docs])
    cosine = cosine_similarity(vectors[0:1], vectors[1:]).ravel()
    found = {name.casefold() for name in skill_names}
    results = []
    for role, similarity in zip(roles, cosine):
        required = role["required_skills"]
        coverage = sum(skill.casefold() in found for skill in required) / max(len(required), 1)
        score = round(100 * (0.65 * float(similarity) + 0.35 * coverage))
        results.append({"role": role["role"], "score": min(score, 100),
                        "cosine_similarity": round(float(similarity), 4), "skill_coverage": round(coverage, 4)})
    return sorted(results, key=lambda item: item["score"], reverse=True)
