from skillbridge.generator import generate_dataset
from skillbridge.engine import load_data, employee_gap, validation_summary

def test_small_dataset(tmp_path):
    generate_dataset(tmp_path, employees=30, skills=30, courses=40, enrollments=80)
    data=load_data(tmp_path)
    assert len(data["Employee"])==30
    assert len(data["Skill"])==30
    assert len(data["Course"])==40
    assert validation_summary(data).passed.all()
    assert not employee_gap(data,"EMP-000001").empty
