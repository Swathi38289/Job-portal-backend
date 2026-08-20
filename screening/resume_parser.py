from pathlib import Path
from typing import BinaryIO


class UnsupportedResumeFormatError(ValueError):
    """Raised when a resume format is not supported by the parser."""


def parse_resume(resume: str | Path | BinaryIO) -> str:
    """Extract text from a PDF or DOCX resume."""
    filename = getattr(resume, "name", resume)
    suffix = Path(str(filename)).suffix.lower()

    if suffix == ".pdf":
        return _parse_pdf(resume)
    if suffix == ".docx":
        return _parse_docx(resume)
    raise UnsupportedResumeFormatError(
        "Only PDF and DOCX resumes are supported for text extraction."
    )


def _parse_pdf(resume: str | Path | BinaryIO) -> str:
    import fitz

    if hasattr(resume, "read"):
        document = fitz.open(stream=resume.read(), filetype="pdf")
    else:
        document = fitz.open(str(resume))

    with document:
        return "\n".join(page.get_text() for page in document).strip()


def _parse_docx(resume: str | Path | BinaryIO) -> str:
    from docx import Document

    document = Document(resume)
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs]
    return "\n".join(text for text in paragraphs if text).strip()