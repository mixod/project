from io import BytesIO, StringIO
import unittest

import pandas as pd

from data_processing import (
    dataframe_to_excel,
    load_student_dataframe,
    prepare_prediction_dataframe,
)
from evaluation import calculate_accuracy, compare_predictions
from scoring import calculate_score, classify_performance


class ScoringTests(unittest.TestCase):
    def test_required_examples_and_boundaries(self) -> None:
        cases = [
            ((90, 90, 90), 90.0, "High Performer"),
            ((70, 70, 70), 70.0, "Average"),
            ((40, 50, 45), 45.0, "At Risk"),
            ((60, 60, 60), 60.0, "Average"),
            ((80, 80, 80), 80.0, "High Performer"),
        ]
        for inputs, expected_score, expected_category in cases:
            score = calculate_score(*inputs)
            self.assertEqual(score, expected_score)
            self.assertEqual(classify_performance(score), expected_category)


class DataValidationTests(unittest.TestCase):
    def test_spreadsheet_headers_are_accepted(self) -> None:
        csv = StringIO(
            "Timestamp,Student ID,Student Name,Previous Grade %,Attendance %,Assignment %,Final Grade %\n"
            "10/8/2026 11:33:46,10,Sangram thapa,50,50,50,40\n"
        )

        loaded = load_student_dataframe(csv)
        predictions = prepare_prediction_dataframe(loaded)

        self.assertEqual(predictions.iloc[0]["student_id"], "10")
        self.assertEqual(predictions.iloc[0]["student_name"], "Sangram thapa")
        self.assertEqual(predictions.iloc[0]["score"], 50)
        self.assertEqual(predictions.iloc[0]["final_grade"], 40)

    def test_excel_upload_is_accepted(self) -> None:
        excel_data = BytesIO()
        pd.DataFrame(
            {
                "Student ID": [10],
                "Student Name": ["Sangram thapa"],
                "Previous Grade %": [50],
                "Attendance %": [50],
                "Assignment %": [50],
                "Final Grade %": [40],
            }
        ).to_excel(excel_data, index=False)
        excel_data.seek(0)
        excel_data.name = "student_data.xlsx"

        loaded = load_student_dataframe(excel_data)

        self.assertEqual(loaded.iloc[0]["student_name"], "Sangram thapa")
        self.assertEqual(loaded.iloc[0]["final_grade"], 40)

    def test_excel_upload_without_filename_is_detected_from_file_content(self) -> None:
        excel_data = BytesIO()
        pd.DataFrame(
            {
                "Student ID": [10],
                "Student Name": ["Sangram thapa"],
                "Previous Grade %": [50],
                "Attendance %": [50],
                "Assignment %": [50],
            }
        ).to_excel(excel_data, index=False)
        excel_data.seek(0)

        loaded = load_student_dataframe(excel_data)

        self.assertEqual(loaded.iloc[0]["student_id"], "10")

    def test_out_of_range_attendance_is_rejected(self) -> None:
        csv = StringIO(
            "student_id,student_name,previous_grade,attendance,assignment_completion\n"
            "1,A,80,120,80\n"
        )
        with self.assertRaisesRegex(ValueError, "Attendance cannot be greater than 100"):
            prepare_prediction_dataframe(load_student_dataframe(csv))

    def test_headers_are_normalized_and_duplicate_ids_are_rejected(self) -> None:
        csv = StringIO(
            " Student_ID , student_name,previous_grade,attendance,assignment_completion\n"
            "1,A,80,80,80\n1,B,70,70,70\n"
        )
        with self.assertRaisesRegex(ValueError, "Student ID values must be unique"):
            prepare_prediction_dataframe(load_student_dataframe(csv))


class SampleEvaluationTests(unittest.TestCase):
    def test_sample_data_can_be_downloaded_as_excel(self) -> None:
        from pathlib import Path

        sample_path = Path(__file__).parents[1] / "data" / "sample_students.csv"
        sample_data = load_student_dataframe(sample_path)
        excel_data = dataframe_to_excel(sample_data)

        self.assertTrue(excel_data.startswith(b"PK"))
        loaded_excel = pd.read_excel(BytesIO(excel_data))
        self.assertEqual(list(loaded_excel.columns), list(sample_data.columns))
        self.assertEqual(len(loaded_excel), len(sample_data))

    def test_sample_dataset_accuracy_and_evaluation_columns(self) -> None:
        from pathlib import Path

        sample_path = Path(__file__).parents[1] / "data" / "sample_students.csv"
        predictions = prepare_prediction_dataframe(load_student_dataframe(sample_path))
        evaluated = compare_predictions(predictions)
        metrics = calculate_accuracy(evaluated)
        self.assertEqual(metrics["total_evaluated"], 20)
        self.assertEqual(metrics["correct_predictions"], 19)
        self.assertIn("actual_category", evaluated.columns)
        self.assertIn("correct_prediction", evaluated.columns)


if __name__ == "__main__":
    unittest.main()