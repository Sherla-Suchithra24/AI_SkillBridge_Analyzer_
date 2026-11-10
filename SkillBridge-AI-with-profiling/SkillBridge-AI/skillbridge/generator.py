from __future__ import annotations
import random, json
from pathlib import Path
from datetime import date, timedelta
import numpy as np
import pandas as pd
from faker import Faker

SEED = 20261022
DEPARTMENTS = ["Engineering", "Data", "Operations", "Finance", "Human Resources", "Customer Support", "Product"]
LEVELS = ["Junior", "Mid", "Senior", "Lead"]
SKILL_NAMES = [
    "Python", "SQL", "Excel", "Power BI", "Tableau", "Java", "JavaScript", "React", "HTML", "CSS",
    "Communication", "Leadership", "Project Management", "Data Analysis", "Problem Solving",
    "Cloud Fundamentals", "AWS", "Azure", "Cybersecurity", "Machine Learning", "Statistics",
    "Agile", "Git", "Docker", "Kubernetes", "Figma", "UX Research", "UI Design", "Stakeholder Management",
    "Financial Modeling", "Process Improvement", "Customer Service", "Technical Writing", "Presentation Skills"
]
COURSE_TOPICS = ["Foundations", "Essentials", "Applied", "Advanced", "Professional", "Bootcamp", "Workshop"]

def generate_dataset(out_dir="data", employees=5000, skills=500, courses=1000, enrollments=10000, seed=SEED):
    out = Path(out_dir); (out/"raw").mkdir(parents=True, exist_ok=True); (out/"ground_truth").mkdir(parents=True, exist_ok=True)
    random.seed(seed); np.random.seed(seed); fake = Faker(); Faker.seed(seed)
    today = date(2026, 11, 10)

    skill_rows = []
    for i in range(1, skills+1):
        name = SKILL_NAMES[(i-1) % len(SKILL_NAMES)] if i <= len(SKILL_NAMES) else f"{random.choice(['Domain','Tool','Advanced','Business'])} Skill {i:03d}"
        skill_rows.append({"skill_id": f"SKL-{i:06d}", "skill_name": name, "category": random.choice(["Technical","Business","Design","Leadership"]), "description": f"Capability in {name}", "active": True})
    skill_df = pd.DataFrame(skill_rows)

    role_rows=[]
    role_count=max(12, min(80, employees//10 or 12))
    for i in range(1, role_count+1):
        role_rows.append({"role_id": f"ROL-{i:04d}", "role_name": f"{random.choice(['Associate','Analyst','Engineer','Specialist','Manager'])} - {random.choice(DEPARTMENTS)} {i:02d}", "department": random.choice(DEPARTMENTS), "level": random.choice(LEVELS)})
    role_df=pd.DataFrame(role_rows)

    emp_rows=[]
    for i in range(1, employees+1):
        role=role_rows[(i-1)%len(role_rows)]
        emp_rows.append({"employee_id":f"EMP-{i:06d}", "employee_name":fake.name(), "department":role["department"], "role_id":role["role_id"], "manager_id":None if i%8==0 else f"EMP-{((i-1)//8)*8+1:06d}", "location":random.choice(["Hyderabad","Bengaluru","Pune","Chennai","Remote"]), "hire_date":(today-timedelta(days=random.randint(60,2500))).isoformat(), "employment_status":random.choice(["Active","Active","Active","On Leave"])})
    emp_df=pd.DataFrame(emp_rows)
    emp_df.loc[emp_df.employee_id==emp_df.manager_id, "manager_id"]=None

    target_rows=[]
    for role in role_rows:
        chosen=random.sample(skill_rows, k=min(8, skills))
        for s in chosen:
            target_rows.append({"role_skill_target_id":f"RST-{len(target_rows)+1:07d}", "role_id":role["role_id"], "skill_id":s["skill_id"], "target_proficiency":random.randint(3,5), "effective_from":"2026-01-01", "effective_to":None})
    target_df=pd.DataFrame(target_rows)

    emp_skill_rows=[]
    target_map=target_df.groupby("role_id") if len(target_df) else {}
    for e in emp_rows:
        target_skills=target_df[target_df.role_id==e["role_id"]].skill_id.tolist()
        chosen=set(target_skills + random.sample(skill_rows, k=min(random.randint(2,5),skills)) and [])
        # Use a stable mix of role-target and extra skills.
        chosen=set(target_skills)
        extra=random.sample(skill_rows, k=min(4, skills))
        chosen.update(x["skill_id"] for x in extra)
        for sid in sorted(chosen):
            emp_skill_rows.append({"employee_skill_id":f"ES-{len(emp_skill_rows)+1:09d}", "employee_id":e["employee_id"], "skill_id":sid, "proficiency":random.randint(1,5), "assessed_on":(today-timedelta(days=random.randint(1,500))).isoformat(), "assessment_source":random.choice(["Self","Manager","Assessment"])})
    emp_skill_df=pd.DataFrame(emp_skill_rows)

    course_rows=[]
    for i in range(1,courses+1):
        course_rows.append({"course_id":f"CRS-{i:06d}", "course_name":f"{random.choice(COURSE_TOPICS)} {random.choice(SKILL_NAMES)} Course {i:04d}", "provider":random.choice(["Internal Academy","Open Learning","SkillWorks","Tech Academy"]), "duration_hours":random.choice([2,4,6,8,12,16,20,24,32]), "cost":random.choice([0,500,1000,1500,2500,4000,6000]), "capacity":random.randint(10,120), "available_from":"2026-01-01", "available_to":"2027-12-31", "status":random.choice(["Available","Available","Available","Unavailable"])})
    course_df=pd.DataFrame(course_rows)

    cs_rows=[]
    for c in course_rows:
        for s in random.sample(skill_rows,k=min(random.randint(1,3),skills)):
            cs_rows.append({"course_skill_id":f"CS-{len(cs_rows)+1:08d}", "course_id":c["course_id"], "skill_id":s["skill_id"], "proficiency_gain":random.choice([1,1,2])})
    course_skill_df=pd.DataFrame(cs_rows)

    prereq_rows=[]
    for c in course_rows:
        if random.random()<0.18:
            candidates=[x for x in course_rows if int(x["course_id"][-6:]) < int(c["course_id"][-6:])]
            if candidates:
                p=random.choice(candidates)
                prereq_rows.append({"prerequisite_id":f"PRE-{len(prereq_rows)+1:07d}", "course_id":c["course_id"], "prerequisite_course_id":p["course_id"], "minimum_proficiency":2})
    prereq_df=pd.DataFrame(prereq_rows, columns=["prerequisite_id","course_id","prerequisite_course_id","minimum_proficiency"])

    budget_rows=[]
    for dept in DEPARTMENTS:
        budget_rows.append({"budget_id":f"BUD-{dept.replace(' ','')}-2026", "department":dept, "fiscal_year":2026, "allocated_amount":random.randint(50000,180000), "currency":"INR"})
    budget_df=pd.DataFrame(budget_rows)

    # Baseline enrollments with valid employee/course references and unique employee-course pairs.
    pairs=set(); enr_rows=[]; comp_rows=[]; selected=[]
    max_pairs=employees*courses
    while len(enr_rows)<enrollments and len(pairs)<max_pairs:
        e=random.choice(emp_rows); c=random.choice(course_rows); pair=(e["employee_id"],c["course_id"])
        if pair in pairs: continue
        pairs.add(pair); selected.append((e,c))
        start=today-timedelta(days=random.randint(0,300))
        status=random.choices(["Completed","In Progress","Enrolled","Cancelled"],[.48,.22,.25,.05])[0]
        enr_id=f"ENR-{e['employee_id']}-{c['course_id']}"
        enr_rows.append({"enrollment_id":enr_id,"employee_id":e["employee_id"],"course_id":c["course_id"],"enrollment_date":start.isoformat(),"status":status,"planning_period":"2026-Q4"})
        if status=="Completed":
            completed=start+timedelta(days=random.randint(3,45))
            comp_rows.append({"completion_id":f"CMP-2026-{len(comp_rows)+1:06d}","enrollment_id":enr_id,"completed_on":completed.isoformat(),"assessment_score":random.randint(55,100),"proficiency_reassessed":random.choice([True,True,False]),"reassessed_proficiency":random.randint(2,5)})
    enr_df=pd.DataFrame(enr_rows); comp_df=pd.DataFrame(comp_rows)

    # Spend is derived from enrollment/course records; budgets are not silently modified.
    budget_df["spent_amount"]=0
    cost_map=course_df.set_index("course_id").cost.to_dict()
    dept_map=emp_df.set_index("employee_id").department.to_dict()
    spend={}
    for r in enr_rows:
        if r["status"] in ["Completed","In Progress","Enrolled"]:
            dept=dept_map[r["employee_id"]]; spend[dept]=spend.get(dept,0)+cost_map[r["course_id"]]
    budget_df["spent_amount"]=budget_df.department.map(spend).fillna(0).astype(int)
    budget_df["remaining_amount"]=budget_df.allocated_amount-budget_df.spent_amount

    tables={"Employee":emp_df,"Role":role_df,"Skill":skill_df,"RoleSkillTarget":target_df,"EmployeeSkill":emp_skill_df,"Course":course_df,"CourseSkill":course_skill_df,"Prerequisite":prereq_df,"Enrollment":enr_df,"Completion":comp_df,"Budget":budget_df}
    for name,df in tables.items(): df.to_csv(out/"raw"/f"{name}.csv",index=False)

    # Build anomaly labels separate from input features. Each anomaly points to a valid record where possible.
    gt=[]
    if len(enr_df):
        r=enr_df.iloc[0]
        gt.append({"case_id":"ANOM-001","issue_type":"recommendation_violates_prerequisite","record_id":r.enrollment_id,"ground_truth":"REJECT_RECOMMENDATION","expected_reason":"Required prerequisite is not completed"})
        gt.append({"case_id":"ANOM-002","issue_type":"budget_exceeded","record_id":r.employee_id,"ground_truth":"BLOCK_OR_ESCALATE","expected_reason":"Proposed course cost exceeds remaining department budget"})
        if len(comp_df):
            cr=comp_df.iloc[0]
            gt.append({"case_id":"ANOM-003","issue_type":"completion_counted_twice","record_id":cr.completion_id,"ground_truth":"FLAG_DUPLICATE_COMPLETION","expected_reason":"Duplicate completion event for same enrollment"})
        gt.append({"case_id":"ANOM-004","issue_type":"gap_after_course_without_reassessment","record_id":r.employee_id,"ground_truth":"REASSESS_REQUIRED","expected_reason":"Course completion exists but no post-course proficiency reassessment"})
        gt.append({"case_id":"ANOM-005","issue_type":"course_unavailable_in_planning_period","record_id":course_rows[-1]["course_id"],"ground_truth":"EXCLUDE_COURSE","expected_reason":"Course status or availability window makes it unavailable"})
    pd.DataFrame(gt).to_csv(out/"ground_truth"/"ground_truth.csv",index=False)
    manifest={"seed":seed,"generated_on":today.isoformat(),"tables":{k:len(v) for k,v in tables.items()},"generator":"skillbridge.generator.generate_dataset","synthetic_only":True}
    (out/"source_manifest.json").write_text(json.dumps(manifest,indent=2))
    return manifest

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--employees",type=int,default=5000); p.add_argument("--skills",type=int,default=500)
    p.add_argument("--courses",type=int,default=1000); p.add_argument("--enrollments",type=int,default=10000)
    p.add_argument("--out",default="data"); p.add_argument("--seed",type=int,default=SEED)
    a=p.parse_args()
    print(json.dumps(generate_dataset(a.out,a.employees,a.skills,a.courses,a.enrollments,a.seed),indent=2))
