# SkillBridge AI — Workforce Skill Gap & Learning Recommendation Platform

SkillBridge AI is a workforce skill intelligence and employee profiling application built using Python and Streamlit. It helps organizations understand employee skills, identify skill gaps, and recommend suitable learning courses based on budget, prerequisites, availability, and capacity.

The application provides an interactive dashboard for employee skill analysis, learning recommendations, data exploration, and data quality validation.

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

🚀 Project Overview

Organizations often struggle to understand their employees' existing skills and identify the training required to meet business requirements.

SkillBridge AI addresses this challenge by providing a centralized platform to:

Analyze employee skills and proficiency levels.

Identify gaps between current and target proficiency.

Recommend relevant learning courses.

Consider learning budgets and course feasibility.

Generate workforce datasets for analysis.

Validate data quality and identify anomalies.

✨ Key Features

1. Employee Skill Profiling

Register employee profiles.

Store employee skill information.

Track employee proficiency levels.

2. Skill Gap Analysis

Compare current and target skill proficiency.

Identify missing or insufficient skills.

Display skill gap analysis through interactive visualizations.

3. Budget-Aware Course Recommendations

Recommend learning courses based on identified skill gaps.

Consider prerequisites and course availability.

Apply budget and capacity constraints.

Rank feasible learning recommendations.

4. Resume Parsing and Skill Extraction

Extract text from resumes.

Identify relevant skills from extracted resume content.

Support employee skill profiling workflows.

5. Workforce Data Generation

Generate synthetic employee datasets.

Create sample skills, courses, and enrolment records.

Support testing and demonstration without real employee data.

6. Data Quality & Validation

Perform data validation checks.

Display passed and failed validation results.

Review ground-truth anomaly scenarios.

7. Interactive Data Explorer

Explore available datasets.

View employee, skill, course, and enrolment information.

🛠️ Technology Stack

Technology

Purpose

Python

Core programming language

Streamlit

Interactive web application

Pandas

Data processing and analysis

Plotly

Interactive visualizations

Pathlib

File and directory management

CSV

Dataset storage and handling

📂 Project Structure

SkillBridge-AI/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── DATA_DICTIONARY.md
├── .gitignore
│
├── skillbridge/
│   ├── __init__.py
│   ├── generator.py
│   ├── engine.py
│   ├── resume_parser.py
│   ├── skill_extractor.py
│   └── profiling.py
│
├── data/
│   ├── raw/
│   └── ground_truth/
│
├── tests/
│
└── venv/

Note: The structure above describes the intended organization. Keep only files and folders that actually exist in your repository. The virtual environment (venv/) should not be uploaded to GitHub.

⚙️ Installation & Setup

Prerequisites

Python 3.10 or later

Git

Visual Studio Code (recommended)

Step 1: Clone the Repository

git clone https://github.com/YOUR_USERNAME/skillbridge-ai.git

Step 2: Navigate to the Project Directory

cd skillbridge-ai

Step 3: Create a Virtual Environment

python -m venv venv

Step 4: Activate the Virtual Environment

Windows PowerShell:

.\venv\Scripts\Activate.ps1

Step 5: Install Dependencies

python -m pip install -r requirements.txt

Step 6: Run the Application

python -m streamlit run app.py

Step 7: Open in Browser

Visit:

http://localhost:8501

📊 Application Modules

Module

Responsibility

app.py

Streamlit application and dashboard

config.py

Application configuration

generator.py

Synthetic dataset generation

engine.py

Skill gap analysis and recommendations

resume_parser.py

Resume text extraction

skill_extractor.py

Skill identification

profiling.py

Employee profiling and skill storage

🔮 Future Enhancements

Add a dedicated resume upload interface.

Support PDF resume preview and storage.

Introduce advanced NLP-based skill extraction.

Add role-based skill recommendations.

Implement employee login and authentication.

Add advanced workforce analytics.

Integrate AI-powered personalized learning recommendations.

🎯 Project Objective

The primary objective of SkillBridge AI is to help organizations make better workforce development decisions through employee skill profiling, skill gap identification, and budget-aware learning recommendations.

👩‍💻 Author

Sherla Suchithra

B.Tech Graduate | Python Full Stack Developer | Aspiring AI Developer
