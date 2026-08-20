from collections.abc import Iterable, Mapping
from typing import Any

from .similarity import screening_score


def rank_candidates(
    candidates: Iterable[Any],
    job_description: str,
    resume_text_getter=None,
    use_semantic: bool = False,
) -> list[dict[str, Any]]:
    """Score and rank candidates from highest to lowest match."""
    results = []
    for candidate in candidates:
        resume_text = (
            resume_text_getter(candidate)
            if resume_text_getter
            else _candidate_value(candidate, "resume_text", "")
        )
        results.append(
            {
                "candidate": candidate,
                "score": screening_score(
                    resume_text,
                    job_description,
                    use_semantic=use_semantic,
                ),
            }
        )

    results.sort(key=lambda result: result["score"], reverse=True)
    for rank, result in enumerate(results, start=1):
        result["rank"] = rank
    return results


def _candidate_value(candidate: Any, key: str, default: Any) -> Any:
    if isinstance(candidate, Mapping):
        return candidate.get(key, default)
    return getattr(candidate, key, default)