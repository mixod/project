"""Functions for loading, validating, and preparing student data."""

from __future__ import annotations

from pathlib import Path
import re
from io import BytesIO
from typing import BinaryIO

import pandas as pd

from scoring import calculate_score, classify_performance

REQUIRED_COLUMNS = {
    "student_id",
    "student_name",
    "previous_grade",
    "attendance",
    "assignment_completion",
}

OPTIONAL_COLUMNS = {"final_grade"}
HEADER_ALIASES = {
    "student_id": "student_id",
    "student_name": "student_name",
    "previous_grade": "previous_grade",
    "previous_grade_percent": "previous_grade",
    "attendance": "attendance",
    "attendance_percent": "attendance",
    "assignment": "assignment_completion",
    "assignment_percent": "assignment_completion",
    "assignment_completion": "assignment_completion",
    "assignment_completion_percent": "assignment_completion",
    "final_grade": "final_grade",
    "final_grade_percent": "final_grade",
    "timestamp": "timestamp",
}


def load_student_csv(file_path: str | Path) -> pd.DataFrame:
    """Load a CSV file and validate the required structure."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    return load_student_dataframe(path)


def load_student_dataframe(source: str | Path | BinaryIO | BytesIO) -> pd.DataFrame:
    """Read and validate CSV or Excel data from a path or uploaded file."""
    try:
        source_name = str(getattr(source, "name", source)).lower()
        if hasattr(source, "seek"):
            source.seek(0)
        file_signature = source.read(4) if hasattr(source, "read") else b""
        if hasattr(source, "seek"):
            source.seek(0)

        is_excel = source_name.endswith((".xlsx", ".xls")) or (
            isinstance(file_signature, bytes) and file_signature.startswith(b"PK")
        )
        if is_excel:
            df = pd.read_excel(source)
        else:
            df = pd.read_csv(source)
    except (
        OSError,
        ImportError,
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        UnicodeDecodeError,
        ValueError,
    ) as exc:
        raise ValueError("The uploaded file is not a readable CSV or Excel file.") from exc

    if df.empty:
        raise ValueError("The uploaded file does not contain any student records.")

    cleaned = clean_student_dataframe(df)
    validate_required_columns(cleaned)
    return cleaned


def dataframe_to_excel(df: pd.DataFrame, sheet_name: str = "Student Data") -> bytes:
    """Serialize a dataframe to an Excel workbook for download."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()


def validate_required_columns(df: pd.DataFrame) -> None:
    """Check that all required columns are present in the CSV."""
    missing_columns = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing_columns:
        raise ValueError(
            "The uploaded CSV is missing required columns: "
            + ", ".join(missing_columns)
        )


def clean_student_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names and validate numeric fields without losing errors."""
    cleaned = df.copy()
    normalized_columns = []
    for column in cleaned.columns:
        normalized = re.sub(
            r"_+",
            "_",
            re.sub(r"[^a-z0-9]+", "_", str(column).strip().lower().replace("%", " percent")),
        ).strip("_")
        normalized_columns.append(HEADER_ALIASES.get(normalized, normalized))
    cleaned.columns = normalized_columns

    if len(cleaned.columns) != len(set(cleaned.columns)):
        raise ValueError("The CSV contains duplicate column names.")

    if cleaned.empty:
        raise ValueError("The CSV file does not contain any student records.")

    empty_rows = cleaned.dropna(how="all").copy()
    if len(empty_rows) != len(cleaned):
        raise ValueError("The CSV contains empty rows. Remove them and try again.")

    numeric_columns = ["previous_grade", "attendance", "assignment_completion"]
    if "final_grade" in cleaned.columns:
        numeric_columns.append("final_grade")

    for column in numeric_columns:
        if column in cleaned.columns:
            values = cleaned[column]
            numeric_values = pd.to_numeric(values, errors="coerce")
            invalid_values = values.notna() & numeric_values.isna()
            if invalid_values.any():
                row_number = int(invalid_values[invalid_values].index[0]) + 2
                raise ValueError(f"{column} contains a non-numeric value on CSV row {row_number}.")
            cleaned[column] = numeric_values

    if "student_id" in cleaned.columns:
        cleaned["student_id"] = cleaned["student_id"].astype(str)

    if "student_name" in cleaned.columns:
        cleaned["student_name"] = cleaned["student_name"].astype(str)

    if "student_name" in cleaned.columns:
        cleaned["student_name"] = cleaned["student_name"].replace({"nan": "", "None": ""})
    if "student_id" in cleaned.columns:
        cleaned["student_id"] = cleaned["student_id"].replace({"nan": "", "None": ""})

    return cleaned


def validate_student_row(row: pd.Series) -> None:
    """Validate a single student record before scoring."""
    required_fields = [
        ("student_id", "Student ID"),
        ("student_name", "Student Name"),
        ("previous_grade", "Previous Grade"),
        ("attendance", "Attendance"),
        ("assignment_completion", "Assignment Completion"),
    ]

    for column_name, label in required_fields:
        if pd.isna(row.get(column_name)) or str(row.get(column_name)).strip() == "":
            raise ValueError(f"{label} is missing for a student entry.")

    if pd.isna(row.get("student_name")) or str(row.get("student_name")).strip() == "":
        raise ValueError("Student Name cannot be empty.")

    for column_name, label in [
        ("previous_grade", "Previous Grade"),
        ("attendance", "Attendance"),
        ("assignment_completion", "Assignment Completion"),
    ]:
        value = row.get(column_name)
        if pd.isna(value):
            raise ValueError(f"{label} cannot be empty.")
        numeric_value = float(value)
        if numeric_value < 0:
            raise ValueError(f"{label} cannot be negative.")
        if numeric_value > 100:
            raise ValueError(f"{label} cannot be greater than 100.")

    if "final_grade" in row and not pd.isna(row["final_grade"]):
        final_grade = float(row["final_grade"])
        if final_grade < 0 or final_grade > 100:
            raise ValueError("Final Grade must be between 0 and 100.")


def prepare_prediction_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare a dataframe for prediction by validating each row and adding score fields."""
    working = df.copy()

    validate_required_columns(working)
    if working["student_id"].duplicated().any():
        raise ValueError("Student ID values must be unique.")

    for index, row in working.iterrows():
        try:
            validate_student_row(row)
        except ValueError as exc:
            raise ValueError(f"Invalid data on student row {index + 2}: {exc}") from exc

    working["score"] = working.apply(
        lambda row: calculate_score(
            row["previous_grade"], row["attendance"], row["assignment_completion"]
        ),
        axis=1,
    )
    working["predicted_category"] = working["score"].apply(lambda value: classify_performance(value))

    return working


def build_student_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    """Create a display-friendly summary of student prediction results."""
    summary = df.copy()
    if "score" not in summary.columns:
        summary = prepare_prediction_dataframe(summary)

    columns = [
        "student_id",
        "student_name",
        "previous_grade",
        "attendance",
        "assignment_completion",
        "score",
        "predicted_category",
    ]
    if "final_grade" in summary.columns:
        columns.append("final_grade")
    if "actual_category" in summary.columns:
        columns.append("actual_category")
    if "correct_prediction" in summary.columns:
        columns.append("correct_prediction")
    return summary[columns].copy()


def ensure_results_directory(base_dir: str | Path) -> Path:
    """Create the results directory if it does not exist."""
    result_dir = Path(base_dir) / "results"
    result_dir.mkdir(parents=True, exist_ok=True)
    return result_dir


def get_available_actual_category(final_grade: float) -> str | None:
    """Map final grade to a category using the same fixed thresholds for comparison.

    This is only used for evaluation when an uploaded CSV contains a final_grade.
    Missing final grades are treated as unavailable, not incorrect predictions.
    """
    if pd.isna(final_grade):
        return None
    if final_grade >= 80:
        return "High Performer"
    if final_grade >= 60:
        return "Average"
    return "At Risk"
