import os
from functools import lru_cache

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .skill_extractor import extract_skills


def text_similarity(first_text: str, second_text: str) -> float:
    """Return cosine similarity between two pieces of text, from 0 to 1."""
    if not first_text.strip() or not second_text.strip():
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform([first_text, second_text])
    return float(cosine_similarity(vectors[0:1], vectors[1:2])[0][0])


def semantic_similarity(first_text: str, second_text: str) -> float:
    """Return embedding cosine similarity using a lazily loaded transformer."""
    if not first_text.strip() or not second_text.strip():
        return 0.0

    model = _get_embedding_model()
    embeddings = model.encode([first_text, second_text], normalize_embeddings=True)
    score = float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0])
    return max(0.0, min(1.0, score))


@lru_cache(maxsize=1)
def _get_embedding_model():
    from sentence_transformers import SentenceTransformer

    model_name = os.getenv("SCREENING_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    return SentenceTransformer(model_name)


def skill_coverage(resume_text: str, job_description: str) -> float:
    """Return the fraction of job-description skills found in the resume."""
    required_skills = extract_skills(job_description)
    if not required_skills:
        return 0.0

    resume_skills = set(extract_skills(resume_text))
    return len(resume_skills.intersection(required_skills)) / len(required_skills)


def screening_score(
    resume_text: str,
    job_description: str,
    text_weight: float = 0.6,
    skill_weight: float = 0.4,
    use_semantic: bool = False,
) -> float:
    """Return a weighted resume match score from 0 to 100."""
    if text_weight < 0 or skill_weight < 0 or text_weight + skill_weight == 0:
        raise ValueError("Similarity weights must be non-negative and not both zero.")

    total_weight = text_weight + skill_weight
    text_score = (
        semantic_similarity(resume_text, job_description)
        if use_semantic
        else text_similarity(resume_text, job_description)
    )
    score = (
        text_score * text_weight
        + skill_coverage(resume_text, job_description) * skill_weight
    ) / total_weight
    return round(score * 100, 2)