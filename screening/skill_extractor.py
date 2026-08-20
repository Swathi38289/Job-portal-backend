import re
from collections.abc import Iterable


DEFAULT_SKILL_ALIASES = {
    "python": "Python",
    "django": "Django",
    "drf": "Django REST Framework",
    "django rest framework": "Django REST Framework",
    "rest api": "REST API",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "react": "React",
    "node.js": "Node.js",
    "sql": "SQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "git": "Git",
    "docker": "Docker",
    "aws": "AWS",
    "machine learning": "Machine Learning",
    "natural language processing": "Natural Language Processing",
    "nlp": "Natural Language Processing",
    "pandas": "pandas",
    "scikit-learn": "scikit-learn",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "html": "HTML",
    "css": "CSS",
}


def extract_skills(
    text: str,
    skill_aliases: dict[str, str] | None = None,
) -> list[str]:
    """Extract known skills from text, normalized and ordered by appearance."""
    aliases = {
        alias.lower(): normalized
        for alias, normalized in (skill_aliases or DEFAULT_SKILL_ALIASES).items()
    }
    matches = _find_terms(text, aliases)
    return _unique_in_order(match[2] for match in matches)


def extract_keywords(text: str, keywords: Iterable[str]) -> list[str]:
    """Extract requested keywords from text, preserving the input spelling."""
    terms = {
        keyword.lower(): keyword
        for keyword in keywords
        if keyword.strip()
    }
    matches = _find_terms(text, terms)
    return _unique_in_order(match[2] for match in matches)


def _find_terms(text: str, terms: dict[str, str]) -> list[tuple[int, int, str]]:
    if not text or not terms:
        return []

    pattern = "|".join(
        rf"(?<!\w){re.escape(term)}(?!\w)"
        for term in sorted(terms, key=len, reverse=True)
    )
    return [
        (match.start(), match.end(), terms[match.group(0).lower()])
        for match in re.finditer(pattern, text, flags=re.IGNORECASE)
    ]


def _unique_in_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result