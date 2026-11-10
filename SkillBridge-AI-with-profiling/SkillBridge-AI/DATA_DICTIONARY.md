# Data Dictionary (summary)

All IDs are required, unique primary keys unless identified as foreign keys. Dates use ISO `YYYY-MM-DD`. Money is INR. Proficiency is an integer 1–5.

| Entity | Primary key | Important fields | Relationships / validation |
|---|---|---|---|
| Employee | employee_id | employee_name, department, role_id, manager_id, hire_date, employment_status | role_id → Role; manager_id optional → Employee; status Active/On Leave |
| Role | role_id | role_name, department, level | Parent of RoleSkillTarget and Employee |
| Skill | skill_id | skill_name, category, description, active | Category Technical/Business/Design/Leadership |
| RoleSkillTarget | role_skill_target_id | role_id, skill_id, target_proficiency, effective dates | Role and Skill FKs; target 1–5 |
| EmployeeSkill | employee_skill_id | employee_id, skill_id, proficiency, assessed_on, assessment_source | Employee and Skill FKs; proficiency 1–5 |
| Course | course_id | course_name, provider, duration_hours, cost, capacity, availability dates, status | Duration > 0; cost ≥ 0; capacity ≥ 0 |
| CourseSkill | course_skill_id | course_id, skill_id, proficiency_gain | Course and Skill FKs; gain 1–2 |
| Prerequisite | prerequisite_id | course_id, prerequisite_course_id, minimum_proficiency | Both course FKs; no self-prerequisite |
| Enrollment | enrollment_id | employee_id, course_id, enrollment_date, status, planning_period | Employee and Course FKs; status Enrolled/In Progress/Completed/Cancelled |
| Completion | completion_id | enrollment_id, completed_on, assessment_score, proficiency_reassessed, reassessed_proficiency | Enrollment FK; score 0–100; reassessment optional |
| Budget | budget_id | department, fiscal_year, allocated_amount, spent_amount, remaining_amount, currency | Unique department-year; remaining = allocated − spent |

## Cardinality
- Role 1:N Employee.
- Role N:M Skill via RoleSkillTarget.
- Employee N:M Skill via EmployeeSkill.
- Course N:M Skill via CourseSkill.
- Course N:M Course via Prerequisite (directed prerequisite relationship).
- Employee 1:N Enrollment; Course 1:N Enrollment.
- Enrollment 1:0..1 Completion in baseline records.
- Department 1:1 Budget per fiscal year.
