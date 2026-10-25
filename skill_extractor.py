"""Dictionary-based job skill extraction."""
import re
from pathlib import Path
import pandas as pd

def load_skill_dictionary(path: str | Path) -> list[dict[str, str]]:
    return pd.read_csv(Path(path)).fillna("").to_dict(orient="records")

def _contains(text: str, phrase: str) -> bool:
    phrase = phrase.strip().casefold()
    return bool(phrase and re.search(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])", text.casefold()))

def extract_skills(text: str, dictionary: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return canonical skill and category for every matched skill or alias."""
    result = []
    for row in dictionary:
        aliases = [row["skill"], *row.get("aliases", "").split("|")]
        if any(_contains(text, alias) for alias in aliases):
            result.append({"skill": row["skill"], "category": row.get("category", "Other")})
    return result
