import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from skillbridge.generator import generate_dataset
from skillbridge.engine import load_data, employee_gap, recommend_courses, validation_summary
from skillbridge.resume_parser import extract_resume_text
from skillbridge.skill_extractor import extract_skills
from skillbridge.profiling import register_employee, save_employee_skills

st.set_page_config(page_title="SkillBridge AI", page_icon="🎯", layout="wide")
st.markdown("""
<style>
.main {background:#f7f8fc;} .block-container {padding-top:1.5rem;}
.hero {padding:24px;border-radius:18px;background:linear-gradient(115deg,#172554,#4f46e5);color:white;margin-bottom:18px;}
.hero h1 {font-size:34px;margin:0;} .hero p {opacity:.9;margin-bottom:0;}
div[data-testid="stMetric"] {background:white;padding:14px;border-radius:12px;border:1px solid #e8eaf2;}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>🎯 SkillBridge AI</h1><p>Workforce skill intelligence · Learning paths · Budget-aware recommendations</p></div>', unsafe_allow_html=True)

DATA_DIR = "data"
data_path = Path(DATA_DIR) / "raw" / "Employee.csv"
if not data_path.exists():
    st.warning("Dataset not found. Generate a starter dataset to begin.")
    if st.button("Generate starter dataset (250 employees)"):
        with st.spinner("Generating synthetic data..."):
            generate_dataset(DATA_DIR, employees=250, skills=100, courses=150, enrollments=500)
        st.success("Starter dataset generated. Refreshing...")
        st.rerun()
    st.stop()
try:
    data = load_data(DATA_DIR)
except Exception as ex:
    st.error(f"Could not load dataset: {ex}")
    st.stop()

employees, courses, enroll, targets = data["Employee"], data["Course"], data["Enrollment"], data["RoleSkillTarget"]
c1,c2,c3,c4 = st.columns(4)
c1.metric("Employees", f"{len(employees):,}")
c2.metric("Skills", f"{len(data['Skill']):,}")
c3.metric("Courses", f"{len(courses):,}")
c4.metric("Enrollments", f"{len(enroll):,}")

pages = ["Overview", "Employee Skill Profiling", "Employee Skill Analysis", "Course Recommendations", "Data Quality & Exceptions", "Data Explorer", "Generate Dataset"]
page = st.sidebar.radio("Navigation", pages)

if page == "Overview":
    st.subheader("Workforce learning overview")
    a,b = st.columns(2)
    with a:
        dept = employees.groupby("department").size().reset_index(name="employees")
        st.plotly_chart(px.bar(dept, x="department", y="employees", title="Employees by department"), use_container_width=True)
    with b:
        status = enroll.groupby("status").size().reset_index(name="enrollments")
        st.plotly_chart(px.pie(status, names="status", values="enrollments", title="Enrollment lifecycle"), use_container_width=True)
    st.subheader("Budget position")
    st.dataframe(data["Budget"][["department","allocated_amount","spent_amount","remaining_amount"]], use_container_width=True, hide_index=True)
    st.caption("All generated records are synthetic. Financial amounts are INR.")

elif page == "Employee Skill Profiling":
    st.subheader("Employee registration and skill profiling")
    st.write("Register a new employee, assign their current job role, then add skills from a resume or manually.")
    roles = data["Role"].copy()
    with st.form("employee_registration"):
        employee_name = st.text_input("Employee full name")
        dept_options = sorted(data["Role"]["department"].dropna().unique().tolist())
        department = st.selectbox("Department", dept_options)
        role_options = roles[roles.department == department]
        role_labels = {f"{r.role_name} ({r.role_id})": r.role_id for _, r in role_options.iterrows()}
        selected_role_label = st.selectbox("Current job role", list(role_labels.keys()))
        location = st.selectbox("Location", ["Hyderabad", "Bengaluru", "Pune", "Chennai", "Remote"])
        create_employee = st.form_submit_button("Register employee")
    if create_employee:
        if not employee_name.strip():
            st.error("Please enter the employee name.")
        else:
            new_id = register_employee(DATA_DIR, employee_name, department, role_labels[selected_role_label], location)
            st.session_state["profile_employee_id"] = new_id
            st.success(f"Employee registered: {new_id}. Continue below to add skills.")
            st.rerun()

    st.divider()
    st.subheader("Add skills to an employee")
    employee_ids = employees.employee_id.tolist()
    default_emp = st.session_state.get("profile_employee_id", employee_ids[0] if employee_ids else None)
    if default_emp not in employee_ids and default_emp:
        # Reload after a registration rerun so the new employee is selectable.
        data = load_data(DATA_DIR); employees = data["Employee"]; employee_ids = employees.employee_id.tolist()
    chosen_emp = st.selectbox("Select employee", employee_ids, index=employee_ids.index(default_emp) if default_emp in employee_ids else 0, key="profile_employee_select")
    emp_row = employees.loc[employees.employee_id == chosen_emp].iloc[0]
    st.info(f"{emp_row.employee_name} · {emp_row.department} · {emp_row.role_id}")
    role_targets = data["RoleSkillTarget"].loc[data["RoleSkillTarget"].role_id == emp_row.role_id]
    target_view = role_targets.merge(data["Skill"][["skill_id","skill_name"]], on="skill_id", how="left")
    with st.expander("Required skills for this role", expanded=True):
        if target_view.empty:
            st.warning("No role-specific skill targets are configured for this role yet.")
        else:
            st.dataframe(target_view[["skill_name","target_proficiency"]].rename(columns={"skill_name":"Required skill","target_proficiency":"Target proficiency"}), use_container_width=True, hide_index=True)

    mode = st.radio("How would you like to provide skills?", ["Upload resume (PDF/DOCX)", "Enter skills manually"], horizontal=True)
    skill_master = data["Skill"][["skill_id","skill_name"]].copy()
    selected_items = []
    source = "Resume"
    if mode == "Upload resume (PDF/DOCX)":
        uploaded = st.file_uploader("Upload employee resume", type=["pdf","docx"], help="Resume is processed in memory and is not saved by this application.")
        if uploaded:
            try:
                resume_text = extract_resume_text(uploaded)
                found = extract_skills(resume_text, skill_master)
                if not found:
                    st.warning("No skills from the current Skill master were detected. Try manual entry or check whether the resume contains selectable text.")
                else:
                    st.success(f"Detected {len(found)} matching skills. Please confirm them and assign proficiency.")
                    found_ids = [x["skill_id"] for x in found]
                    selected_ids = st.multiselect("Confirm extracted skills", found_ids, default=found_ids, format_func=lambda sid: skill_master.loc[skill_master.skill_id == sid, "skill_name"].iloc[0])
                    source = "Resume (employee confirmed)"
                    for sid in selected_ids:
                        sname = skill_master.loc[skill_master.skill_id == sid, "skill_name"].iloc[0]
                        prof = st.select_slider(f"Proficiency — {sname}", options=[1,2,3,4,5], value=3, key=f"resume_prof_{sid}")
                        selected_items.append({"skill_id":sid,"proficiency":prof})
            except Exception as ex:
                st.error(f"Could not read this resume: {ex}")
    else:
        source = "Manual entry"
        all_ids = skill_master.skill_id.tolist()
        selected_ids = st.multiselect("Choose employee skills", all_ids, format_func=lambda sid: skill_master.loc[skill_master.skill_id == sid, "skill_name"].iloc[0])
        for sid in selected_ids:
            sname = skill_master.loc[skill_master.skill_id == sid, "skill_name"].iloc[0]
            prof = st.select_slider(f"Proficiency — {sname}", options=[1,2,3,4,5], value=3, key=f"manual_prof_{sid}")
            selected_items.append({"skill_id":sid,"proficiency":prof})
    assessor = st.selectbox("Who is providing/verifying this assessment?", ["Employee", "Manager", "HR Partner", "Technical Assessment"])
    if st.button("Save employee skills", type="primary", disabled=not selected_items):
        count = save_employee_skills(DATA_DIR, chosen_emp, selected_items, source, assessor)
        st.success(f"Saved {count} skill assessment(s) for {chosen_emp}. Assessment history was retained.")
        st.info("Return to Employee Skill Analysis to compare the updated skills with this employee's role targets.")

elif page == "Employee Skill Analysis":
    st.subheader("Employee skill gap analysis")
    employee_id = st.selectbox("Select employee", employees.employee_id.tolist(), format_func=lambda x: f"{x} — {employees.loc[employees.employee_id==x,'employee_name'].iloc[0]}")
    e = employees.loc[employees.employee_id == employee_id].iloc[0]
    role_name = data["Role"].loc[data["Role"].role_id == e.role_id, "role_name"]
    st.write(f"**{e.employee_name}** · {e.department} · Role: {role_name.iloc[0] if not role_name.empty else e.role_id}")
    gaps = employee_gap(data, employee_id)
    if gaps.empty: st.info("No role skill targets found.")
    else:
        x,y,z = st.columns(3); x.metric("Target skills",len(gaps)); y.metric("Skills meeting target",int((gaps.gap==0).sum())); z.metric("Open skill gaps",int((gaps.gap>0).sum()))
        st.dataframe(gaps, use_container_width=True, hide_index=True)
        st.plotly_chart(px.bar(gaps, x="skill_name", y=["current_proficiency","target_proficiency"], barmode="group", title="Current vs target proficiency"), use_container_width=True)

elif page == "Course Recommendations":
    st.subheader("Budget-aware learning recommendations")
    employee_id = st.selectbox("Choose employee", employees.employee_id.tolist(), key="rec_emp")
    recs = recommend_courses(data, employee_id)
    if recs.empty: st.success("No skill gaps found or no mapped courses.")
    else:
        st.dataframe(recs, use_container_width=True, hide_index=True)
        st.caption("Feasible recommendations satisfy prerequisite, availability, budget and capacity checks. Ranking score is a transparent heuristic, not a trained AI model.")
        st.metric("Feasible options shown", int(recs.feasible.sum()))

elif page == "Data Quality & Exceptions":
    st.subheader("Data validation")
    checks = validation_summary(data); passed = int(checks.passed.sum())
    a,b = st.columns(2); a.metric("Checks passed",f"{passed}/{len(checks)}"); b.metric("Checks failed",len(checks)-passed)
    st.dataframe(checks, use_container_width=True, hide_index=True)
    gt = Path(DATA_DIR) / "ground_truth" / "ground_truth.csv"
    if gt.exists():
        st.subheader("Known anomaly scenarios (evaluation labels)")
        st.dataframe(pd.read_csv(gt), use_container_width=True, hide_index=True)
    st.info("Ground-truth labels are kept separate from recommendation input tables.")

elif page == "Data Explorer":
    st.subheader("Synthetic data tables")
    table = st.selectbox("Select table", list(data.keys()))
    st.write(f"{len(data[table]):,} rows")
    st.dataframe(data[table].head(500), use_container_width=True, hide_index=True)
    history_path = Path(DATA_DIR) / "raw" / "SkillAssessmentHistory.csv"
    if history_path.exists():
        st.subheader("Skill assessment event history")
        history = pd.read_csv(history_path)
        st.dataframe(history.tail(200), use_container_width=True, hide_index=True)

elif page == "Generate Dataset":
    st.subheader("Generate or scale the synthetic dataset")
    st.warning("Generating a new dataset replaces the CSV files in data/raw, including employee profiles. Export/backup custom records first.")
    with st.form("generate"):
        n_emp = st.number_input("Employees", min_value=50, max_value=5000, value=500, step=50)
        n_skills = st.number_input("Skills", min_value=30, max_value=500, value=100, step=10)
        n_courses = st.number_input("Courses", min_value=30, max_value=1000, value=200, step=10)
        n_enr = st.number_input("Enrollments", min_value=100, max_value=10000, value=1000, step=100)
        seed = st.number_input("Fixed seed", min_value=1, value=20261022)
        submitted = st.form_submit_button("Generate dataset")
    if submitted:
        with st.spinner("Generating records and exporting CSV files..."):
            manifest = generate_dataset(DATA_DIR, int(n_emp), int(n_skills), int(n_courses), int(n_enr), int(seed))
        st.success("Dataset generated successfully.")
        st.json(manifest)
        st.info("Use the sidebar to reload the new dataset.")
