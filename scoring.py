"""Core logic for the simple student performance prediction system.

This module contains the transparent, unweighted scoring method required by the
thesis proposal. It intentionally avoids machine learning or complex modeling.
"""

from __future__ import annotations


def calculate_score(previous_grade: float, attendance: float, assignment_completion: float) -> float:
    """Calculate the student performance score using the required simple average formula.

    Formula:
        Score = (Previous Grade + Attendance + Assignment Completion) / 3

    All inputs must be on a 0-100 scale.
    """
    validate_score_input(previous_grade, "Previous Grade")
    validate_score_input(attendance, "Attendance")
    validate_score_input(assignment_completion, "Assignment Completion")

    score = (previous_grade + attendance + assignment_completion) / 3
    return round(score, 2)


def validate_score_input(value: float, field_name: str) -> None:
    """Validate a single score input.

    Rules:
    - must be numeric
    - must be between 0 and 100 inclusive
    - empty values are invalid
    """
    if value is None:
        raise ValueError(f"{field_name} cannot be empty.")

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a number.") from None

    if numeric_value != numeric_value:
        raise ValueError(f"{field_name} cannot be empty.")

    if numeric_value < 0:
        raise ValueError(f"{field_name} cannot be negative.")

    if numeric_value > 100:
        raise ValueError(f"{field_name} cannot be greater than 100.")


def classify_performance(score: float) -> str:
    """Return the category based on the fixed thresholds in the proposal."""
    if score >= 80:
        return "High Performer"
    if score >= 60:
        return "Average"
    return "At Risk"


def build_performance_summary(score: float) -> str:
    """Create a short explanatory sentence for the score result."""
    category = classify_performance(score)
    return (
        f"The student score is {score:.2f}, which places the student in the "
        f"'{category}' category based on the fixed thresholds."
    )
