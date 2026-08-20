from pathlib import Path
from typing import BinaryIO

from .resume_parser import parse_resume


class UnsupportedJobDescriptionFormatError(ValueError):
    """Raised when a job description format is not supported."""


def parse_job_description(description: str | Path | BinaryIO) -> str:
    """Return plain text from a string, TXT, PDF, or DOCX job description."""
    if isinstance(description, str):
        return description.strip()

    filename = getattr(description, "name", description)
    suffix = Path(str(filename)).suffix.lower()

    if suffix in {".pdf", ".docx"}:
        return parse_resume(description)
    if suffix == ".txt":
        return _parse_text(description)
    raise UnsupportedJobDescriptionFormatError(
        "Job descriptions must be text, TXT, PDF, or DOCX files."
    )


def _parse_text(description: Path | BinaryIO) -> str:
    if hasattr(description, "read"):
        content = description.read()
    else:
        content = Path(description).read_bytes()

    if isinstance(content, bytes):
        content = content.decode("utf-8")
    return content.strip()