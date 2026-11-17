# Student Performance Prediction Using a Simple Average Scoring Method

## Overview

This undergraduate thesis application predicts student performance with a transparent, rule-based scoring method. It uses previous grade average, attendance percentage, and assignment completion percentage. It does not use machine learning or weighted scoring.

## Features

- Individual student prediction
- CSV upload and validation
- Automatic score calculation and fixed-category classification
- Actual-versus-predicted comparison when `final_grade` is provided
- Accuracy metrics and a simple confusion matrix
- Performance distribution chart
- Student-level result inspection
- Downloadable prediction results
- Fictional sample dataset

## Methodology

The score is always calculated as:

`Score = (Previous Grade + Attendance + Assignment Completion) / 3`

Classification uses the fixed thresholds:

- `score >= 80`: High Performer
- `score >= 60`: Average
- `score < 60`: At Risk

When `final_grade` is available, its category is calculated with the same thresholds for evaluation. Accuracy is `(correct predictions / evaluated students) * 100`.

## Technologies

- Python 3
- Pandas
- Streamlit
- VS Code

## Installation and Local Run

```text
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The application opens at `http://localhost:8501`.

## Dataset Format

Required columns:

```text
student_id,student_name,previous_grade,attendance,assignment_completion
```

Optional column:

```text
final_grade
```

All grade and percentage values must be numeric and between 0 and 100. Student IDs must be unique. Blank final grades are allowed but are excluded from accuracy evaluation. The included sample uses fictional students.

## Testing

Run the standard-library regression tests with:

```text
python -m unittest discover -s tests -v
```

The tests cover the requested score examples, boundaries at 60 and 80, invalid attendance, duplicate IDs, header normalization, and sample accuracy.

## Deployment

This project is suitable for Streamlit Community Cloud or another Streamlit-compatible host:

1. Push the project to a Git repository.
2. Create a new Streamlit deployment.
3. Select `app.py` as the main file.
4. The host installs dependencies from `requirements.txt` and runs `streamlit run app.py`.

The app processes uploaded CSV content in memory and does not store uploaded student data permanently. No local Windows paths are required.

## Limitations

- All three indicators have equal importance.
- The system does not use machine learning or learn from historical data.
- Classification thresholds are fixed.
- Academic performance depends on many factors beyond these three indicators.
- Prediction quality depends on dataset quality.
- A simple average may not fully represent actual academic performance.

## Future Enhancements

Possible future work includes machine learning models, weighted scoring, larger datasets, additional academic indicators, database integration, student login, teacher or administrator dashboards, historical tracking, and early-warning notifications. These are not part of the current methodology.

## Project Structure

```text
app.py
scoring.py
data_processing.py
evaluation.py
requirements.txt
data/sample_students.csv
docs/methodology.md
tests/test_project.py
.streamlit/config.toml
```
"# project" 
