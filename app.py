from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from data_processing import (
    build_student_summary_table,
    dataframe_to_excel,
    load_student_dataframe,
    prepare_prediction_dataframe,
)
from evaluation import calculate_accuracy, compare_predictions
from scoring import build_performance_summary, calculate_score, classify_performance

PROJECT_ROOT = Path(__file__).parent
SAMPLE_PATH = PROJECT_ROOT / "data" / "sample_students.csv"
REQUIRED_COLUMNS_TEXT = (
    "Student ID, Student Name, Previous Grade %, Attendance %, Assignment %"
)

st.set_page_config(page_title="Student Performance Prediction", page_icon="🎓", layout="wide")


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #17212b;
            --muted: #62727d;
            --line: #d8e2e7;
            --teal: #1f6f8b;
            --teal-dark: #15546a;
            --paper: #ffffff;
        }
        .stApp { background: #f7f9fb; }
        .block-container { max-width: 1180px; padding: 3.2rem 2rem 4rem; }
        [data-testid="stSidebar"] { border-right: 1px solid var(--line); background: #eef4f6; }
        [data-testid="stSidebar"] > div:first-child { padding: 1.5rem 1.15rem; }
        [data-testid="stSidebar"] .stRadio > label { color: var(--muted); font-size: .72rem; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; }
        [data-testid="stSidebar"] .stRadio [role="radiogroup"] { gap: .2rem; }
        [data-testid="stSidebar"] .stRadio [role="radiogroup"] label { border-radius: 6px; color: var(--muted); padding: .42rem .5rem; transition: background .15s ease, color .15s ease; }
        [data-testid="stSidebar"] .stRadio [role="radiogroup"] label:hover { background: #dcebef; color: var(--teal-dark); }
        [data-testid="stSidebar"] .stRadio [role="radiogroup"] label:has(input:checked) { background: #d5e8ed; color: var(--teal-dark); font-weight: 750; }
        h1, h2, h3 { color: var(--ink); letter-spacing: 0; }
        h1 { font-size: 2.25rem; line-height: 1.15; margin-bottom: .25rem; }
        h2 { margin-top: 2rem; font-size: 1.35rem; }
        h3 { font-size: 1.05rem; }
        p, li, label { color: var(--muted); }
        .app-kicker { color: var(--teal); display: block; font-size: .72rem; font-weight: 800; letter-spacing: .12em; line-height: 1.5; margin: .15rem 0 .55rem; min-height: 1.1rem; overflow: visible; }
        .app-subtitle { color: var(--teal-dark); font-size: 1.05rem; font-weight: 650; margin-bottom: .35rem; }
        .app-intro { max-width: 720px; color: var(--muted); font-size: 1rem; line-height: 1.6; }
        .section-label { color: var(--teal); font-size: .72rem; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; margin-top: 2rem; }
        .sidebar-brand { color: var(--ink); font-size: 1.05rem; font-weight: 800; line-height: 1.25; margin-bottom: .25rem; }
        .sidebar-note { color: var(--muted); font-size: .78rem; line-height: 1.45; margin-bottom: 1.5rem; }
        .welcome-panel { background: linear-gradient(135deg, #e2f0f3 0%, #f8fbfc 100%); border: 1px solid #c9dfe5; border-radius: 10px; padding: 1.35rem 1.5rem; margin: 1rem 0 1.5rem; }
        .welcome-title { color: var(--ink); font-size: 1.18rem; font-weight: 750; margin-bottom: .35rem; }
        .welcome-copy { color: var(--muted); line-height: 1.55; margin-bottom: 0; }
        .info-card { background: var(--paper); border: 1px solid var(--line); border-radius: 8px; min-height: 148px; padding: 1.1rem 1.15rem; }
        .info-card h4 { color: var(--ink); font-size: .98rem; margin: 0 0 .55rem; }
        .info-card p { color: var(--muted); font-size: .88rem; line-height: 1.5; margin: 0; }
        .card-number { color: var(--teal); font-size: .72rem; font-weight: 800; letter-spacing: .08em; margin-bottom: .5rem; }
        .threshold-card { border-left: 4px solid var(--teal); background: var(--paper); border-top: 1px solid var(--line); border-right: 1px solid var(--line); border-bottom: 1px solid var(--line); border-radius: 0 7px 7px 0; padding: .85rem 1rem; margin-bottom: .65rem; }
        .threshold-card strong { color: var(--ink); }
        .threshold-card span { color: var(--muted); float: right; }
        [data-testid="stMetric"] { background: var(--paper); border: 1px solid var(--line); border-radius: 8px; padding: 1rem 1.1rem; box-shadow: 0 2px 8px rgba(23, 33, 43, .04); }
        [data-testid="stMetricLabel"] { color: var(--muted); }
        [data-testid="stMetricValue"] { color: var(--ink); }
        .stButton > button, .stDownloadButton > button { border-radius: 6px; font-weight: 700; border: 1px solid var(--teal); }
        .stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] { background: var(--teal); color: #ffffff !important; }
        .stDownloadButton > button[kind="primary"] p, .stDownloadButton > button[kind="primary"] span { color: #ffffff !important; opacity: 1; }
        .stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover { background: var(--teal-dark); border-color: var(--teal-dark); }
        [data-testid="stFileUploader"] { background: var(--paper); border: 1px dashed #9db8c3; border-radius: 8px; padding: .35rem; }
        [data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
        [data-testid="stExpander"] { background: var(--paper); border: 1px solid var(--line); border-radius: 8px; }
        .divider { border-top: 1px solid var(--line); margin: 1.5rem 0; }
        @media (max-width: 700px) {
            .block-container { padding: 2.2rem 1rem 3rem; }
            h1 { font-size: 1.8rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown('<div class="app-kicker">ACADEMIC PERFORMANCE TOOL</div>', unsafe_allow_html=True)
    st.markdown("# Student Performance Prediction System")
    st.markdown('<div class="app-subtitle">Simple Average Scoring Method</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-intro">A transparent rule-based system for predicting student performance using previous grade, attendance, and assignment completion.</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


def render_methodology() -> None:
    with st.expander("Methodology and limitations"):
        st.markdown("**Method**")
        st.write("The system uses a simple unweighted average. It is a rule-based method, not a machine learning model.")
        st.code("Score = (Previous Grade + Attendance + Assignment Completion) / 3")
        st.markdown("**Classification**")
        st.write("80-100: High Performer | 60-79.99: Average | 0-59.99: At Risk")
        st.markdown("**Limitations**")
        st.write(
            "All indicators have equal importance; the system does not learn from historical data; "
            "thresholds are fixed; other academic and personal factors are not included; and results "
            "depend on dataset quality. A simple average may not fully represent academic performance."
        )
        st.markdown("**Future enhancements**")
        st.write(
            "Machine learning models, weighted scoring, larger datasets, additional indicators, "
            "database integration, student login, teacher dashboards, historical tracking, and early warnings."
        )


def render_dashboard() -> None:
    st.markdown('<div class="section-label">Workspace</div>', unsafe_allow_html=True)
    st.subheader("Project Overview")
    st.markdown(
        '<div class="welcome-panel"><div class="welcome-title">Ready to evaluate student performance?</div>'
        '<p class="welcome-copy">Choose an individual prediction for a quick check, upload a class CSV for a full analysis, or explore the included sample dataset.</p></div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### Choose a starting point")
    action_columns = st.columns(3)
    action_cards = [
        ("01", "Individual prediction", "Enter three indicators and receive an immediate, explainable result."),
        ("02", "CSV analysis", "Process a full class dataset with validation, charts, and downloadable results."),
        ("03", "Sample dataset", "Explore fictional student records and the actual-versus-predicted evaluation."),
    ]
    for column, (number, title, description) in zip(action_columns, action_cards):
        with column:
            st.markdown(
                f'<div class="info-card"><div class="card-number">{number}</div>'
                f'<h4>{title}</h4><p>{description}</p></div>',
                unsafe_allow_html=True,
            )

    st.markdown("#### The scoring method")
    method_columns = st.columns([1.15, 1])
    with method_columns[0]:
        st.markdown(
            '<div class="info-card"><h4>One transparent formula</h4>'
            '<p>Each indicator contributes equally to the final score. No machine learning or hidden weighting is used.</p>'
            '<div style="background:#eef4f6;border-radius:6px;color:#15546a;font-weight:700;margin-top:1rem;padding:.8rem;text-align:center;">'
            'Score = (Grade + Attendance + Assignment) / 3</div></div>',
            unsafe_allow_html=True,
        )
    with method_columns[1]:
        st.markdown(
            '<div class="threshold-card"><strong>High Performer</strong><span>80 and above</span></div>'
            '<div class="threshold-card"><strong>Average</strong><span>60 to 79.99</span></div>'
            '<div class="threshold-card"><strong>At Risk</strong><span>Below 60</span></div>',
            unsafe_allow_html=True,
        )

    with st.expander("Methodology, limitations, and future enhancements"):
        st.markdown("**Method**")
        st.write("The system uses a simple unweighted average. It is a rule-based method, not a machine learning model.")
        st.markdown("**Limitations**")
        st.write(
            "All indicators have equal importance; the system does not learn from historical data; thresholds are fixed; "
            "other academic and personal factors are not included; and results depend on dataset quality."
        )
        st.markdown("**Future enhancements**")
        st.write("Machine learning, weighted scoring, larger datasets, additional indicators, database integration, and historical tracking.")


def render_metrics(results: pd.DataFrame) -> None:
    counts = results["predicted_category"].value_counts()
    metrics = st.columns(6 if "actual_category" in results.columns else 5)
    metrics[0].metric("Total Students", len(results))
    metrics[1].metric("High Performers", int(counts.get("High Performer", 0)))
    metrics[2].metric("Average", int(counts.get("Average", 0)))
    metrics[3].metric("At Risk", int(counts.get("At Risk", 0)))
    if "actual_category" in results.columns:
        accuracy = calculate_accuracy(results)
        metrics[4].metric("Evaluated", accuracy["total_evaluated"])
        metrics[5].metric("Accuracy", f"{accuracy['accuracy_percentage']:.2f}%")
    else:
        metrics[4].metric("Evaluated", "-")


def render_results(results: pd.DataFrame) -> None:
    st.markdown('<div class="section-label">Analysis</div>', unsafe_allow_html=True)
    st.subheader("Prediction Results")
    render_metrics(results)
    st.dataframe(build_student_summary_table(results), use_container_width=True, hide_index=True)

    chart_data = results["predicted_category"].value_counts().reindex(
        ["High Performer", "Average", "At Risk"], fill_value=0
    )
    st.subheader("Performance Distribution")
    st.bar_chart(chart_data)

    if "actual_category" in results.columns:
        accuracy = calculate_accuracy(results)
        st.subheader("Actual vs Predicted Evaluation")
        evaluation_columns = st.columns(4)
        evaluation_columns[0].metric("Correct Predictions", accuracy["correct_predictions"])
        evaluation_columns[1].metric("Incorrect Predictions", accuracy["incorrect_predictions"])
        evaluation_columns[2].metric("Total Evaluated", accuracy["total_evaluated"])
        evaluation_columns[3].metric("Accuracy", f"{accuracy['accuracy_percentage']:.2f}%")

        confusion = pd.crosstab(
            results["actual_category"], results["predicted_category"], dropna=True
        ).reindex(
            index=["High Performer", "Average", "At Risk"],
            columns=["High Performer", "Average", "At Risk"],
            fill_value=0,
        )
        st.caption("Confusion matrix: rows are actual categories and columns are predicted categories.")
        st.dataframe(confusion, use_container_width=True)

    st.subheader("Student-Level Analysis")
    selected_id = st.selectbox("Select a student", results["student_id"].astype(str).tolist())
    student = results[results["student_id"].astype(str) == selected_id].iloc[0]
    detail_columns = st.columns(4)
    detail_columns[0].metric("Student", str(student["student_name"]))
    detail_columns[1].metric("Prediction Score", f"{student['score']:.2f}")
    detail_columns[2].metric("Predicted Category", student["predicted_category"])
    detail_columns[3].metric("Attendance", f"{student['attendance']:.2f}%")
    st.write(
        f"Previous Grade: {student['previous_grade']:.2f}% | "
        f"Assignment Completion: {student['assignment_completion']:.2f}%"
    )
    if "actual_category" in student.index and pd.notna(student.get("actual_category")):
        st.write(
            f"Final Grade: {student['final_grade']:.2f}% | Actual Category: {student['actual_category']} | "
            f"Prediction: {'Correct' if student['correct_prediction'] else 'Incorrect'}"
        )

    st.download_button(
        "Download Prediction Results",
        data=build_student_summary_table(results).to_csv(index=False),
        file_name="student_prediction_results.csv",
        mime="text/csv",
    )


def process_uploaded_csv(uploaded_file) -> pd.DataFrame | None:
    try:
        source = load_student_dataframe(uploaded_file)
        predictions = prepare_prediction_dataframe(source)
        return compare_predictions(predictions) if "final_grade" in predictions.columns else predictions
    except (ValueError, UnicodeDecodeError) as exc:
        st.error(str(exc))
        return None


def render_csv_upload() -> None:
    st.markdown('<div class="section-label">Data Input</div>', unsafe_allow_html=True)
    st.subheader("Student Data Upload")
    st.write(
        f"Required columns: {REQUIRED_COLUMNS_TEXT}. "
        "Optional columns: Final Grade %, Timestamp."
    )
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=["csv", "xlsx", "xls"],
    )
    if uploaded_file is None:
        st.info("Upload a CSV or Excel file to generate predictions.")
        return
    results = process_uploaded_csv(uploaded_file)
    if results is not None:
        st.success("File processed successfully.")
        render_results(results)


def render_individual_prediction() -> None:
    st.markdown('<div class="section-label">Quick Check</div>', unsafe_allow_html=True)
    st.subheader("Individual Student Prediction")
    with st.form("student_prediction_form"):
        student_id = st.text_input("Student ID")
        student_name = st.text_input("Student Name")
        previous_grade = st.number_input("Previous Grade Average (%)", 0.0, 100.0, 75.0)
        attendance = st.number_input("Attendance Percentage (%)", 0.0, 100.0, 85.0)
        assignment_completion = st.number_input("Assignment Completion (%)", 0.0, 100.0, 90.0)
        submitted = st.form_submit_button("Predict Performance")

    if submitted:
        try:
            score = calculate_score(previous_grade, attendance, assignment_completion)
            category = classify_performance(score)
            st.success(f"Prediction generated: {category}")
            st.metric("Prediction Score", f"{score:.2f}")
            st.write(build_performance_summary(score))
            st.caption(f"Student: {student_name or 'Unnamed'} | ID: {student_id or 'Not provided'}")
        except ValueError as exc:
            st.error(str(exc))


def render_sample_data() -> None:
    st.markdown('<div class="section-label">Demonstration</div>', unsafe_allow_html=True)
    st.subheader("Sample Dataset")
    if not SAMPLE_PATH.exists():
        st.warning("Sample dataset not found.")
        return
    sample_results = compare_predictions(
        prepare_prediction_dataframe(load_student_dataframe(SAMPLE_PATH))
    )
    st.write("The included fictional dataset is ready to upload or inspect below.")
    st.download_button(
        "Download Sample Data (Excel)",
        data=dataframe_to_excel(load_student_dataframe(SAMPLE_PATH)),
        file_name="sample_students.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
    )
    render_results(sample_results)


def main() -> None:
    apply_styles()
    st.sidebar.markdown(
        '<div class="sidebar-brand">Student Performance<br>Prediction</div>'
        '<div class="sidebar-note">Simple Average Scoring Method</div>',
        unsafe_allow_html=True,
    )
    render_header()
    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "Navigation", ["Dashboard", "Individual Prediction", "CSV Upload", "Sample Data"]
    )
    st.sidebar.markdown(
        '<div style="border-top:1px solid #d8e2e7;margin-top:1.5rem;padding-top:1rem;">'
        '<div style="color:#1f6f8b;font-size:.7rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;">Project status</div>'
        '<div style="color:#62727d;font-size:.78rem;line-height:1.5;margin-top:.35rem;">Ready for CSV analysis<br>Rule-based and explainable</div></div>',
        unsafe_allow_html=True,
    )
    if page == "Dashboard":
        render_dashboard()
    elif page == "Individual Prediction":
        render_individual_prediction()
    elif page == "CSV Upload":
        render_csv_upload()
    else:
        render_sample_data()


if __name__ == "__main__":
    main()
