import streamlit as st
import pandas as pd
import mysql.connector

def connect_2_sql():
    cnx = mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        port=st.secrets["mysql"]["port"]
    )
    return cnx

def save(data):
    cnx = connect_2_sql()
    cursor = cnx.cursor()
    query = '''INSERT INTO gpa_records (department, semester, graded_courses, sgpa, sgpa_data, cgpa, cgpa_data) VALUES (%s, %s, %s, %s, %s, %s, %s)'''
    cursor.execute(query, (data["Department"],data["Semester"], data["Graded Courses Taken"], data["SGPA Obtained"], data["SGPA_DATA"], data["CGPA Obtained"], data["CGPA_DATA"]))
    cnx.commit()
    cnx.close()

st.set_page_config("CGPA/SGPA Calculator", page_icon="🎓",layout="wide")

grades = {
    "A+" : 10, "A":10, "A-":9, "B":8,"B-":7,"C":6, "C-":5,"D":4, "F": 0, "FS": 0, "I": 0
}

st.markdown(
    """
    <h1 style="text-align:center;">🎓 CGPA/SGPA Calculator</h1>
    <p style="text-align:center; color:gray;">
    Enter course credits and grades to compute your SGPA
    </p>
    """,
    unsafe_allow_html=True
)
st.divider()

if "last_sgpa" not in st.session_state:
    st.session_state["last_sgpa"] = None

if "last_cgpa" not in st.session_state:
    st.session_state["last_cgpa"] = None

if "courses" not in st.session_state:
    st.session_state["courses"] = []

if "cgpa_data" not in st.session_state:
    st.session_state["cgpa_data"] = []  

if "graded_courses_taken" not in st.session_state:
    st.session_state["graded_courses_taken"] = None

if "dep" not in st.session_state:
    st.session_state["dep"] = None

if "sem" not in st.session_state:
    st.session_state["sem"] = None

courses = st.number_input("Number of Graded Courses Taken :", min_value=1, step = 1)
con1, con2 = st.columns(2)
with con1:
    dep = st.selectbox("Enter your Department :", ["CSE", "AIDS", "ECE", "EE", "ME", "MSME", "MT"])
with con2:
    sem = st.selectbox("Semester Completed :",[1,2,3,4,5,6,7,8])

if (not dep) or (not sem):
    st.error("Please fill the Required Columns")

with st.form("sgpa_form"):
    course_data = []
    for i in range(courses):
        st.subheader(f"Course {i+1}", False)
        c1, c2 = st.columns(2)
        with c1:
            credit = st.number_input("Credits", min_value=0.5, step=0.5, key=f"credit_{i}")
        with c2:
            grade = st.selectbox( "Grade", options=list(grades.keys()), key=f"grade_{i}")
        course_data.append((credit, grades[grade]))
    submitted = st.form_submit_button("📊 Calculate SGPA")

run = False
if submitted:
    run = True
    total_credits = 0
    weighted_sum = 0
    for credit, grade in course_data:
        total_credits += credit
        weighted_sum += credit * grade
    sgpa = round(weighted_sum / total_credits, 2)

    st.session_state["graded_courses_taken"] = courses
    st.session_state["dep"] = dep
    st.session_state["sem"] = sem

    st.session_state["last_sgpa"] = sgpa
    st.session_state["courses"] = course_data

    if st.session_state["last_sgpa"] >= 8.0:
        st.balloons()
    st.toast(f"🎯 **SGPA Obtained: {sgpa}**")

if run:
    st.success(f"🎯 **SGPA Obtained: {sgpa}**")

st.divider()

if sem > 1:
        with st.form("cgpa_form"):
            cgpa_data = []
            for j in range(sem - 1):
                st.subheader(f"SEMESTER {j+1}", False)
                cgpa_sem = st.number_input(f"Grades Obtained in SEMESTER {j+1} :", min_value= 0.00, max_value=10.00,step = 0.01)
                cgpa_data.append(cgpa_sem)
            cgpa_data.append(st.session_state["last_sgpa"])
            sub = st.form_submit_button("📊 Calculate CGPA")

        if sub:
            cgpa = round(sum(cgpa_data)/sem, 2)
            st.session_state["last_cgpa"] = cgpa
            st.session_state["cgpa_data"] = cgpa_data
            if st.session_state["last_cgpa"] >= 8.0:
                st.balloons()
            st.success(f"🎯 **CGPA Obtained: {st.session_state["last_cgpa"]}**")
            st.toast(f"🎯 **CGPA Obtained: {st.session_state["last_cgpa"]}**")

    
if sem == 1 and submitted:
        st.session_state["last_cgpa"] = st.session_state["last_sgpa"]
        st.session_state["cgpa_data"] = [st.session_state["last_sgpa"]]
        st.success(f"🎯 **CGPA Obtained: {st.session_state["last_cgpa"]}**")
        st.toast(f"🎯 **CGPA Obtained: {st.session_state["last_cgpa"]}**")

if (sem > 1 and sub) or (sem == 1 and submitted):
    st.divider()

    user_data = { 
        "Department": st.session_state["dep"], 
        "Semester": st.session_state["sem"],
        "Graded Courses Taken": st.session_state["graded_courses_taken"],
        "SGPA Obtained": st.session_state["last_sgpa"],
        "SGPA_DATA": str(st.session_state["courses"]),
        "CGPA Obtained": st.session_state["last_cgpa"],
        "CGPA_DATA": str(st.session_state["cgpa_data"])
    }

    st.dataframe(pd.DataFrame([user_data]))
    save(user_data)

    df = pd.DataFrame(
        st.session_state["courses"],
        columns=["Credits", "Grade"]
    )
    st.dataframe(df, use_container_width=True)

