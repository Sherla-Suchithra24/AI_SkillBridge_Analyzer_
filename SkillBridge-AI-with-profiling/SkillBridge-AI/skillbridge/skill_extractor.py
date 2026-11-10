"""Simple, explainable skill-name matching against the Skill master table."""
import re

ALIASES = {
    "javascript": ["javascript", "js"],
    "react": ["react", "react.js"],
    "power bi": ["power bi", "powerbi"],
    "machine learning": ["machine learning", "ml"],
    "ux research": ["ux research", "user research"],
    "ui design": ["ui design", "user interface design"],
    "communication": ["communication", "verbal communication", "written communication"],
}


def extract_skills(text: str, skills_df):
    text_l = text.lower()
    found = []
    for _, row in skills_df.iterrows():
        skill_name = str(row["skill_name"])
        candidates = ALIASES.get(skill_name.lower(), [skill_name.lower()])
        matched = False
        for term in candidates:
            pattern = r"(?<![a-z0-9+#])" + re.escape(term) + r"(?![a-z0-9+#])"
            if re.search(pattern, text_l):
                matched = True
                break
        if matched:
            found.append({"skill_id": row["skill_id"], "skill_name": skill_name})
    return found
