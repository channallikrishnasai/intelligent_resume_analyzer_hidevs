from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(?:\+?\d[\d().\s-]{5,}\d)")
YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\s*(?:-|–|to)\s*(present|current|19\d{2}|20\d{2})\b", re.I)

@dataclass
class Candidate:
    name: str | None
    email: str | None
    phone: str | None
    skills: list[str]
    experience_years: float | None
    education: list[str]
    source_file: str


def extract_candidate(text: str, source_file: str = "<text>") -> Candidate:
    """Extract explicit resume facts. This is a review aid, not a hiring decision."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    email_match = EMAIL_RE.search(text)
    phone_match = PHONE_RE.search(text)
    name = None
    for line in lines[:8]:
        if EMAIL_RE.search(line) or PHONE_RE.search(line) or len(line) > 60:
            continue
        words = re.findall(r"[A-Za-z][A-Za-z'.-]*", line)
        if 1 < len(words) <= 4 and all(w[0].isupper() or w.isupper() for w in words):
            name = " ".join(w.title() for w in words)
            break

    skill_bank = {
        "Python", "Java", "JavaScript", "TypeScript", "SQL", "C++", "C#", "Go",
        "React", "Node.js", "Django", "Flask", "FastAPI", "AWS", "Azure", "GCP",
        "Docker", "Kubernetes", "Git", "Linux", "Excel", "Power BI", "TensorFlow",
        "PyTorch", "pandas", "NumPy", "HTML", "CSS", "REST APIs", "PostgreSQL",
        "MongoDB", "Machine Learning", "Data Analysis", "Project Management",
    }
    lower_text = text.casefold()
    skills = sorted((s for s in skill_bank if s.casefold() in lower_text), key=str.casefold)
    years = []
    for start, end in YEAR_RE.findall(text):
        a = int(start)
        b = 2026 if end.casefold() in {"present", "current"} else int(end)
        if 0 <= b - a <= 60:
            years.append(b - a)
    exp = round(sum(years), 1) if years else None
    education = [line for line in lines if re.search(r"\b(bachelor|master|ph\.?d|associate|b\.?s\.?|m\.?s\.?|b\.?tech|m\.?tech|university|college)\b", line, re.I)]
    return Candidate(
        name=name,
        email=email_match.group(0).lower() if email_match else None,
        phone=phone_match.group(0).strip() if phone_match else None,
        skills=skills,
        experience_years=exp,
        education=education,
        source_file=Path(source_file).name,
    )


def score_match(candidate: Candidate, required_skills: list[str]) -> dict[str, Any]:
    """Calculate transparent skill coverage only; never rank or reject people."""
    available = {s.casefold(): s for s in candidate.skills}
    matched = [skill for skill in required_skills if skill.casefold() in available]
    missing = [skill for skill in required_skills if skill.casefold() not in available]
    score = round(100 * len(matched) / len(required_skills)) if required_skills else 0
    return {"match_score": score, "matched_skills": matched, "missing_skills": missing,
            "note": "Skill coverage is a review aid; do not use as an automated hiring decision."}


def analyze(resume_path: Path, required_skills: list[str]) -> dict[str, Any]:
    try:
        text = resume_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"Cannot read resume '{resume_path}': {exc}") from exc
    if not text.strip():
        raise ValueError("Resume file is empty.")
    candidate = extract_candidate(text, str(resume_path))
    return {"candidate": asdict(candidate), "job_match": score_match(candidate, required_skills),
            "review_required": True}


def main() -> int:
    parser = argparse.ArgumentParser(description="Local resume parsing and skill coverage review aid")
    parser.add_argument("resume", type=Path, help="UTF-8 plain-text resume file")
    parser.add_argument("--skills", default="", help="Comma-separated job skills")
    parser.add_argument("--output", type=Path, default=Path("analysis.json"), help="Output JSON path")
    args = parser.parse_args()
    try:
        result = analyze(args.resume, [s.strip() for s in args.skills.split(",") if s.strip()])
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(f"Saved review report to {args.output}")
    print("This tool does not make hiring recommendations or decisions; a human must review all extracted data.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
