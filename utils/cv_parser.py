"""CV parser — extracts raw text and detects skills from uploaded PDFs / DOCX."""

from __future__ import annotations
import re
import io

SKILL_PATTERNS = [
    # Programming & data
    r"\bPython\b", r"\bR\b(?=\s|,)", r"\bSQL\b", r"\bJava\b(?!Script)",
    r"\bJavaScript\b", r"\bTypeScript\b", r"\bC\+\+\b", r"\bC#\b",
    r"\bReact\b", r"\bNode\.?js\b", r"\bVue\b", r"\bAngular\b",
    r"\bMachine Learning\b", r"\bDeep Learning\b", r"\bNLP\b",
    r"\bData Analysis\b", r"\bData Science\b", r"\bStatistics\b",
    r"\bTensorFlow\b", r"\bPyTorch\b", r"\bKeras\b", r"\bscikit-learn\b",
    r"\bPandas\b", r"\bNumPy\b", r"\bMatplotlib\b", r"\bTableau\b",
    r"\bPower BI\b", r"\bExcel\b", r"\bSPSS\b", r"\bMATLAB\b",
    # Cloud / DevOps
    r"\bAWS\b", r"\bAzure\b", r"\bGoogle Cloud\b", r"\bGCP\b",
    r"\bDocker\b", r"\bKubernetes\b", r"\bGit\b", r"\bLinux\b",
    # Business
    r"\bProject Management\b", r"\bAgile\b", r"\bScrum\b", r"\bLeadership\b",
    r"\bCommunication\b", r"\bResearch\b", r"\bWriting\b", r"\bAnalysis\b",
    r"\bFinance\b", r"\bAccounting\b", r"\bMarketing\b", r"\bStrategic\b",
    # Science / Health
    r"\bPublic Health\b", r"\bEpidemiology\b", r"\bBiology\b",
    r"\bChemistry\b", r"\bBiostatistics\b", r"\bLaboratory\b",
]

def extract_cv_text(file) -> str:
    """Return plain text from a PDF or DOCX upload."""
    text = ""
    name = getattr(file, "name", "")
    raw  = file.read()

    if name.lower().endswith(".pdf"):
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(raw)) as pdf:
                text = "\n".join(p.extract_text() or "" for p in pdf.pages)
        except Exception:
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(io.BytesIO(raw))
                text = "\n".join(p.extract_text() or "" for p in reader.pages)
            except Exception:
                text = ""

    elif name.lower().endswith(".docx"):
        try:
            import docx
            doc  = docx.Document(io.BytesIO(raw))
            text = "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            text = ""

    return text.strip()


def parse_skills_from_text(text: str) -> list[str]:
    """Extract skill keywords from CV text."""
    found: list[str] = []
    for pattern in SKILL_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            found.append(m.group(0))
    # deduplicate preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for s in found:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique
