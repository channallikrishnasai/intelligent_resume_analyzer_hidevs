# Intelligent Resume Analyzer

A local-only Python application that extracts explicit resume details, calculates transparent skill coverage, and saves a JSON review report. It supports human review; it does not rank, reject, recommend, or select candidates.

## Features

- Extracts a likely name, email, phone, skills, education lines, and date-range experience from plain-text resumes.
- Compares required skills and reports the matched skills, missing skills, and a simple coverage percentage.
- Saves results as JSON and reports unreadable or empty input files clearly.
- Uses only Python's standard library; resume text stays on the local machine.

## Run

Requires Python 3.10 or newer. No third-party packages are required.

    python intelligent_resume_analyzer.py sample_resume.txt --skills "Python, SQL, pandas" --output analysis.json

Input must be UTF-8 plain text. Convert PDF or DOCX files to text before use. Review the JSON output and verify every extracted field. Do not commit real resumes or analysis reports containing personal data.

## Output

The JSON report includes the parsed candidate fields, matched and missing job skills, the coverage score, and a review-required flag. Missing information remains null or an empty list; it is not inferred.

## Limitations and responsible use

The parser uses simple patterns and a small skill vocabulary. It can miss facts or misread dates, so every result needs human review. The score measures only the fraction of requested skills explicitly mentioned; it does not measure suitability, performance, or eligibility. Do not use this tool for automated employment decisions or decisions based on sensitive personal data. No resume content is sent to an API.

## Demo

Demonstrate the command-line run using the synthetic sample file, inspect the JSON result, and explain the limitations above. Do not use a real person's resume in a public demo.
