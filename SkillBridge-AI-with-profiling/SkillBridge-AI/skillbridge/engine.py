from pathlib import Path
import pandas as pd

def load_data(data_dir="data"):
    p=Path(data_dir)/"raw"
    names=["Employee","Role","Skill","RoleSkillTarget","EmployeeSkill","Course","CourseSkill","Prerequisite","Enrollment","Completion","Budget"]
    return {n:pd.read_csv(p/f"{n}.csv") for n in names}

def employee_gap(data, employee_id):
    e=data["Employee"].loc[data["Employee"].employee_id==employee_id]
    if e.empty: return pd.DataFrame()
    role_id=e.iloc[0].role_id
    targets=data["RoleSkillTarget"].loc[data["RoleSkillTarget"].role_id==role_id]
    current=data["EmployeeSkill"].loc[data["EmployeeSkill"].employee_id==employee_id]
    merged=targets.merge(data["Skill"][["skill_id","skill_name"]],on="skill_id",how="left").merge(current[["skill_id","proficiency"]],on="skill_id",how="left")
    merged["current_proficiency"]=merged.proficiency.fillna(0).astype(int)
    merged["gap"]= (merged.target_proficiency-merged.current_proficiency).clip(lower=0)
    merged["gap_status"]=merged.gap.apply(lambda x:"Gap" if x>0 else "Met")
    return merged[["skill_id","skill_name","current_proficiency","target_proficiency","gap","gap_status"]]

def recommend_courses(data, employee_id, budget_limit=None):
    gaps=employee_gap(data,employee_id)
    gaps=gaps[gaps.gap>0]
    if gaps.empty: return pd.DataFrame(columns=["course_id","course_name","skills_covered","cost","duration_hours","feasible","reason","score"])
    current=data["EmployeeSkill"].loc[data["EmployeeSkill"].employee_id==employee_id]
    completed_ids=set(data["Enrollment"].merge(data["Completion"],on="enrollment_id",how="inner").loc[lambda x:x.employee_id==employee_id,"course_id"])
    course_skills=data["CourseSkill"].merge(gaps[["skill_id","gap"]],on="skill_id",how="inner")
    results=[]
    emp=data["Employee"].loc[data["Employee"].employee_id==employee_id].iloc[0]
    budget=data["Budget"].loc[data["Budget"].department==emp.department]
    remaining=float(budget.iloc[0].remaining_amount) if not budget.empty else 0
    if budget_limit is not None: remaining=min(remaining,float(budget_limit))
    for cid, group in course_skills.groupby("course_id"):
        c=data["Course"].loc[data["Course"].course_id==cid].iloc[0]
        prereqs=data["Prerequisite"].loc[data["Prerequisite"].course_id==cid]
        prereq_ok=True
        for _,pr in prereqs.iterrows():
            if pr.prerequisite_course_id not in completed_ids:
                prereq_ok=False
        available=(str(c.status)=="Available" and str(c.available_from)<="2026-12-31" and str(c.available_to)>="2026-11-10")
        budget_ok=float(c.cost)<=remaining
        capacity_ok=int(c.capacity)>0
        feasible=prereq_ok and available and budget_ok and capacity_ok and cid not in completed_ids
        reasons=[]
        if not prereq_ok: reasons.append("Prerequisite not completed")
        if not available: reasons.append("Unavailable in planning period")
        if not budget_ok: reasons.append("Insufficient budget")
        if not capacity_ok: reasons.append("No capacity")
        if cid in completed_ids: reasons.append("Already completed")
        score=int(group.gap.sum()*10 + group.proficiency_gain.sum()*3 - float(c.cost)/1000 - float(c.duration_hours)/10)
        results.append({"course_id":cid,"course_name":c.course_name,"skills_covered":", ".join(gaps[gaps.skill_id.isin(group.skill_id)].skill_name.tolist()),"cost":int(c.cost),"duration_hours":int(c.duration_hours),"feasible":feasible,"reason":"; ".join(reasons) if reasons else "Meets rules","score":score})
    return pd.DataFrame(results).sort_values(["feasible","score"],ascending=[False,False]).head(30)

def validation_summary(data):
    checks=[]
    for table,key in [("Employee","employee_id"),("Role","role_id"),("Skill","skill_id"),("Course","course_id"),("Enrollment","enrollment_id"),("Completion","completion_id")]:
        df=data[table]; checks.append({"check":f"{table} primary key unique","passed":not df[key].duplicated().any(),"details":f"{df[key].nunique()} unique / {len(df)} rows"})
    fk=[("Employee","role_id","Role","role_id"),("RoleSkillTarget","role_id","Role","role_id"),("RoleSkillTarget","skill_id","Skill","skill_id"),("EmployeeSkill","employee_id","Employee","employee_id"),("EmployeeSkill","skill_id","Skill","skill_id"),("CourseSkill","course_id","Course","course_id"),("CourseSkill","skill_id","Skill","skill_id"),("Enrollment","employee_id","Employee","employee_id"),("Enrollment","course_id","Course","course_id"),("Completion","enrollment_id","Enrollment","enrollment_id")]
    for child,col,parent,pcol in fk:
        valid=set(data[parent][pcol])
        ok=data[child][col].dropna().isin(valid).all()
        checks.append({"check":f"{child}.{col} foreign key","passed":bool(ok),"details":"All references valid" if ok else "Invalid references found"})
    return pd.DataFrame(checks)
