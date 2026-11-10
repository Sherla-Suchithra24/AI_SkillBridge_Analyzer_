"""CSV-backed employee registration and skill assessment persistence."""
from pathlib import Path
import pandas as pd
from datetime import date


def _next_employee_id(df):
    nums = pd.to_numeric(df["employee_id"].astype(str).str.extract(r"EMP-(\d+)")[0], errors="coerce")
    return f"EMP-{int(nums.max() if nums.notna().any() else 0)+1:06d}"


def register_employee(data_dir, employee_name, department, role_id, location="Hyderabad"):
    raw = Path(data_dir) / "raw"
    employees = pd.read_csv(raw / "Employee.csv")
    employee_id = _next_employee_id(employees)
    new_row = {
        "employee_id": employee_id, "employee_name": employee_name.strip(),
        "department": department, "role_id": role_id, "manager_id": None,
        "location": location, "hire_date": date.today().isoformat(),
        "employment_status": "Active"
    }
    employees = pd.concat([employees, pd.DataFrame([new_row])], ignore_index=True)
    employees.to_csv(raw / "Employee.csv", index=False)
    return employee_id


def save_employee_skills(data_dir, employee_id, skill_rows, source, assessor="Employee"):
    raw = Path(data_dir) / "raw"
    path = raw / "EmployeeSkill.csv"
    existing = pd.read_csv(path)
    # Keep the latest assessment per employee/skill in the operational snapshot.
    # Append each new assessment to a separate immutable history file as well.
    history_path = raw / "SkillAssessmentHistory.csv"
    history = pd.read_csv(history_path) if history_path.exists() else pd.DataFrame(columns=[
        "assessment_id", "employee_id", "skill_id", "proficiency", "assessed_on", "assessment_source", "assessor"
    ])
    today = date.today().isoformat()
    history_rows = []
    for item in skill_rows:
        assessment_id = f"ASM-{len(history)+len(history_rows)+1:09d}"
        history_rows.append({"assessment_id": assessment_id, "employee_id": employee_id,
            "skill_id": item["skill_id"], "proficiency": int(item["proficiency"]),
            "assessed_on": today, "assessment_source": source, "assessor": assessor})
    if history_rows:
        history = pd.concat([history, pd.DataFrame(history_rows)], ignore_index=True)
        history.to_csv(history_path, index=False)
        for item in skill_rows:
            mask = (existing.employee_id == employee_id) & (existing.skill_id == item["skill_id"])
            new = {"employee_skill_id": f"ES-{len(existing)+1:09d}", "employee_id": employee_id,
                   "skill_id": item["skill_id"], "proficiency": int(item["proficiency"]),
                   "assessed_on": today, "assessment_source": source}
            if mask.any():
                idx = existing.index[mask][-1]
                for col, val in new.items():
                    if col != "employee_skill_id": existing.loc[idx, col] = val
            else:
                existing = pd.concat([existing, pd.DataFrame([new])], ignore_index=True)
        existing.to_csv(path, index=False)
    return len(history_rows)
