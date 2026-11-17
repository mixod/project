"""Evaluation logic for comparing predicted and actual student outcomes."""

from __future__ import annotations

import pandas as pd

from scoring import classify_performance


def compare_predictions(df: pd.DataFrame) -> pd.DataFrame:
    """Compare the predicted category against the actual category when final_grade exists."""
    result = df.copy()

    if "final_grade" not in result.columns:
        return result

    result["actual_category"] = result["final_grade"].apply(
        lambda grade: None if pd.isna(grade) else classify_performance(grade)
    )
    result["correct_prediction"] = result["predicted_category"].eq(result["actual_category"])
    return result


def calculate_accuracy(df: pd.DataFrame) -> dict:
    """Calculate overall accuracy based on correctly classified students."""
    if "correct_prediction" in df.columns:
        filtered = df[df["actual_category"].notna()].copy()
    else:
        filtered = df[df["actual_category"].notna()] if "actual_category" in df.columns else df
        if "actual_category" not in filtered.columns:
            raise ValueError(
                "This dataset does not contain a final_grade column, so accuracy cannot be calculated."
            )

    total_evaluated = len(filtered)
    if total_evaluated == 0:
        return {
            "total_evaluated": 0,
            "correct_predictions": 0,
            "incorrect_predictions": 0,
            "accuracy_percentage": 0.0,
        }

    correct_predictions = int(filtered["correct_prediction"].sum())
    incorrect_predictions = total_evaluated - correct_predictions
    accuracy = (correct_predictions / total_evaluated) * 100

    return {
        "total_evaluated": total_evaluated,
        "correct_predictions": correct_predictions,
        "incorrect_predictions": incorrect_predictions,
        "accuracy_percentage": round(accuracy, 2),
    }


def get_accuracy_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Create a simple comparison table for thesis demonstration."""
    comparison = compare_predictions(df)
    if "final_grade" not in comparison.columns:
        return comparison

    columns = [
        "student_id",
        "student_name",
        "predicted_category",
        "actual_category",
        "correct_prediction",
    ]
    return comparison[columns].copy()
