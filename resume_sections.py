"""Heading-based resume section detection and skill evidence review."""
import re

HEADING_ALIASES = {
    "summary": {"summary", "profile", "professional summary", "career objective", "objective"},
    "skills": {"skills", "technical skills", "core skills", "technical expertise", "core competencies"},
    "experience": {"experience", "work experience", "professional experience", "employment history", "internships", "internship experience"},
    "projects": {"projects", "academic projects", "personal projects", "project experience"},
    "education": {"education", "academic background", "qualifications"},
    "certifications": {"certifications", "certificates", "courses"},
}

def extract_resume_sections(text: str) -> dict[str, str]:
    """Split cleaned text at common standalone section headings."""
    sections: dict[str, list[str]] = {"other": []}
    active = "other"
    heading_lookup = {alias: section for section, aliases in HEADING_ALIASES.items() for alias in aliases}
    for line in text.splitlines():
        normalized = re.sub(r"^[\s\W]+|[\s\W]+$", "", line.casefold()).strip()
        normalized = re.sub(r"\s+", " ", normalized)
        normalized = re.sub(r"[:|]+$", "", normalized).strip()
        heading = heading_lookup.get(normalized)
        if heading:
            active = heading
            sections.setdefault(active, [])
            continue
        sections.setdefault(active, []).append(line.strip())
    return {name: content for name, lines in sections.items() if (content := "\n".join(lines).strip())}

def find_limited_evidence_skills(found_skills: list[dict[str, str]], dictionary: list[dict[str, str]], sections: dict[str, str]) -> list[str]:
    """Flag skills listed under Skills without a matching Experience or Projects mention."""
    skills_text = sections.get("skills", "").casefold()
    evidence_text = (sections.get("experience", "") + " " + sections.get("projects", "")).casefold()
    if not skills_text:
        return []
    aliases_by_skill = {row["skill"].casefold(): [row["skill"], *row.get("aliases", "").split("|")] for row in dictionary}
    limited = []
    for item in found_skills:
        canonical = item["skill"]
        aliases = aliases_by_skill.get(canonical.casefold(), [canonical])
        in_skills = any(_has_phrase(skills_text, alias) for alias in aliases)
        in_examples = any(_has_phrase(evidence_text, alias) for alias in aliases)
        if in_skills and not in_examples:
            limited.append(canonical)
    return limited

def _has_phrase(text: str, phrase: str) -> bool:
    phrase = phrase.strip().casefold()
    return bool(phrase and re.search(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])", text))
