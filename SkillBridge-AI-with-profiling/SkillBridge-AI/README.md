# SkillBridge AI — Workforce Skill Gap & Learning Recommendation Platform

A beginner-friendly, hackathon-ready synthetic-data application that identifies role-based employee skill gaps and recommends feasible learning options while checking prerequisites, availability, capacity and department budgets.

## Features
- Synthetic master and transaction data generator with fixed seed `20261022`.
- Employee, role, skill, target, employee skill, course, course mapping, prerequisite, enrollment, completion and budget CSV tables.
- Employee skill-gap analysis against role targets.
- Transparent course recommendation heuristic.
- Prerequisite, availability, budget and capacity checks.
- Separate `ground_truth/ground_truth.csv` anomaly labels.
- Streamlit dashboard with overview, employee analysis, recommendations, validation and data explorer.
- Pytest starter test.

## Requirements
- Python 3.10+
- Windows, macOS or Linux

## Setup (Windows PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
If PowerShell blocks activation, run:
```powershell
.venv\Scripts\activate.bat
```

## Generate a starter dataset
```bash
python -m skillbridge.generator --employees 250 --skills 100 --courses 150 --enrollments 500
```

## Generate the suggested full dataset
```bash
python -m skillbridge.generator --employees 5000 --skills 500 --courses 1000 --enrollments 10000
```

## Run the application
```bash
streamlit run app.py
```
Open the local URL printed in the terminal (usually http://localhost:8502).

## Run tests
```bash
python -m pytest -q
```

## Output files
- `data/raw/*.csv` — generated input tables.
- `data/ground_truth/ground_truth.csv` — separate known anomaly labels.
- `data/source_manifest.json` — seed, generation date, row counts and provenance note.

## Data model and key relationships
- Employee → Role: many employees belong to one role.
- Role ↔ Skill: many-to-many through RoleSkillTarget.
- Employee ↔ Skill: many-to-many through EmployeeSkill.
- Course ↔ Skill: many-to-many through CourseSkill.
- Course ↔ Course: prerequisite self-reference through Prerequisite.
- Employee → Enrollment: one employee can have many enrollments.
- Course → Enrollment: one course can have many enrollments.
- Enrollment → Completion: zero or one completion in the baseline model (completion events are retained as separate rows).
- Department → Budget: one annual budget record per department.

## Important implementation notes
- IDs are deterministic in format and immutable within a generated dataset.
- Generator uses a fixed seed; use the same parameters and seed for repeatable output.
- The dashboard recommendation score is a transparent heuristic, not a trained AI model.
- `ground_truth.csv` is for evaluation and must not be joined into recommendation features.
- This starter version creates labelled anomaly scenarios in the ground-truth file; the baseline operational tables remain referentially valid.
- Budget spend is derived from active/completed enrollment costs. The sample generator does not silently alter source costs to fit budgets.
- The starter app is designed for a local hackathon demo. Review and extend lifecycle event handling before production use.

## Lawful provenance
All generated employee, course and assessment records are synthetic. No confidential or personal employee dataset is collected. No external dataset is redistributed.

## Employee Skill Profiling (new)
- Register an employee and assign a current role from the Role master.
- The app displays required skills and target proficiency from RoleSkillTarget.
- Upload PDF/DOCX resumes for keyword-based matching against the Skill master, or enter skills manually.
- Employees/managers assign proficiency (1-5) after reviewing extracted skills. Resume mentions are not treated as verified proficiency.
- Current EmployeeSkill values are updated, while each assessment is appended to `data/raw/SkillAssessmentHistory.csv`.
- Resume content is processed in memory and is not saved by the application. Scanned/image-only PDFs may require OCR, which is not included in this version.

Install the added resume parsers through `pip install -r requirements.txt`.
