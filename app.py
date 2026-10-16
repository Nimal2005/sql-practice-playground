import re
import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(page_title="SQL Practice Playground", page_icon="🧠", layout="wide")
st.title("🧠 SQL Practice Playground")
st.write("Practice `SELECT`, `WHERE`, `GROUP BY`, `HAVING`, `ORDER BY`, and joins.")

@st.cache_resource
def create_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.executescript("""
    CREATE TABLE departments (department_id INTEGER PRIMARY KEY, department_name TEXT);
    INSERT INTO departments VALUES (1,'Engineering'),(2,'Data Science'),(3,'HR'),(4,'Sales');
    CREATE TABLE employees (
        employee_id INTEGER PRIMARY KEY, name TEXT, department_id INTEGER,
        salary INTEGER, city TEXT, years_experience INTEGER,
        FOREIGN KEY(department_id) REFERENCES departments(department_id)
    );
    INSERT INTO employees VALUES
    (1,'Ananya',1,72000,'Chennai',4),(2,'Rahul',2,68000,'Bengaluru',3),
    (3,'Priya',2,81000,'Chennai',5),(4,'Karthik',1,59000,'Coimbatore',2),
    (5,'Meera',3,52000,'Chennai',6),(6,'Arjun',4,61000,'Hyderabad',3),
    (7,'Divya',1,90000,'Bengaluru',7),(8,'Vikram',4,57000,'Chennai',1);
    """)
    return conn

conn = create_db()
examples = {
    "Select all employees": "SELECT * FROM employees;",
    "Employees in Chennai": "SELECT name, salary FROM employees WHERE city = 'Chennai' ORDER BY salary DESC;",
    "Average salary by department": "SELECT d.department_name, ROUND(AVG(e.salary), 2) AS avg_salary FROM employees e JOIN departments d ON e.department_id = d.department_id GROUP BY d.department_name ORDER BY avg_salary DESC;",
    "Departments with average salary above 65000": "SELECT d.department_name, AVG(e.salary) AS avg_salary FROM employees e JOIN departments d ON e.department_id = d.department_id GROUP BY d.department_name HAVING AVG(e.salary) > 65000;",
}
choice = st.selectbox("Load an example", list(examples))
query = st.text_area("SQL query", value=examples[choice], height=140)

def is_read_only_select(sql):
    cleaned = sql.strip()
    if not cleaned:
        return False
    # Permit one optional trailing semicolon only; reject multiple statements.
    cleaned = cleaned[:-1].strip() if cleaned.endswith(";") else cleaned
    if ";" in cleaned:
        return False
    if not re.match(r"^(SELECT|WITH)\b", cleaned, flags=re.IGNORECASE):
        return False
    forbidden = r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|ATTACH|DETACH|PRAGMA|REPLACE|VACUUM)\b"
    return re.search(forbidden, cleaned, flags=re.IGNORECASE) is None

if st.button("Run query", type="primary"):
    if not is_read_only_select(query):
        st.error("Only one read-only SELECT/WITH query is allowed.")
    else:
        try:
            df = pd.read_sql_query(query, conn)
            st.success(f"Query completed — {len(df)} row(s).")
            st.dataframe(df, use_container_width=True)
            st.download_button("Download results as CSV", df.to_csv(index=False), "query_results.csv", "text/csv")
        except Exception as exc:
            st.error(f"SQL error: {exc}")

with st.expander("Database schema"):
    st.code("employees(employee_id, name, department_id, salary, city, years_experience)\ndepartments(department_id, department_name)", language="text")
