"""Extract text from PDF/DOCX resumes in memory; files are not stored."""
from io import BytesIO


def extract_resume_text(uploaded_file) -> str:
    name = uploaded_file.name.lower()
    content = uploaded_file.getvalue()
    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("Install pypdf: python -m pip install pypdf") from exc
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if name.endswith(".docx"):
        try:
            from docx import Document
        except ImportError as exc:
            raise RuntimeError("Install python-docx: python -m pip install python-docx") from exc
        doc = Document(BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError("Unsupported file. Please upload a PDF or DOCX resume.")
