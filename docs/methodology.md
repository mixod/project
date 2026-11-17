# Methodology

## Introduction

This project develops a simple system for predicting student performance using a basic average-based scoring method. The objective is to evaluate whether a transparent rule-based method can classify students into performance categories using only three indicators: previous grade average, attendance percentage, and assignment completion percentage.

## Problem Statement

Many educational institutions require quick and understandable methods for identifying students who may need support. A simple scoring system can provide early insight without requiring advanced machine learning techniques. This project evaluates the usefulness of a basic average-based model for classifying student performance.

## Objectives

The main objectives of this project are to:

- collect student academic data
- calculate performance using the selected indicators
- classify students into High Performer, Average, or At Risk
- evaluate the system using simple classification accuracy
- present the results in a clear and professional interface

## Data Collection

The system uses a CSV dataset containing student information. The sample dataset in the project includes fictional student records that reflect realistic academic values. The selected variables are:

- previous_grade
- attendance
- assignment_completion
- final_grade (used only for evaluation when available)

No machine learning dataset is required for this project. The system intentionally uses a simple structure that is easy to explain and defend academically.

## Data Preparation

The dataset is checked to ensure that the required columns are present. Student records are validated to confirm that all numeric values are present and fall within the required 0 to 100 range. Invalid inputs are rejected before scoring is calculated.

## Scoring Method

The project uses the formula specified in the thesis proposal:

Score = (Previous Grade + Attendance + Assignment Completion) / 3

This is an unweighted average. Every indicator is treated equally. No additional weight or hidden factor is added.

## Performance Classification

The score is then classified using fixed thresholds:

- Score >= 80 = High Performer
- Score >= 60 and < 80 = Average
- Score < 60 = At Risk

These thresholds are simple, transparent, and easy to present in a thesis defense.

## Evaluation Method

The system compares the predicted category with the actual category when a final_grade is available. The actual category is computed using the same threshold logic applied to the final grade:

- final_grade >= 80 = High Performer
- final_grade >= 60 and < 80 = Average
- final_grade < 60 = At Risk

Accuracy is calculated as:

Accuracy = (Correct Predictions / Total Evaluated Students) \* 100

This gives a straightforward measure of how often the simple scoring method matches the outcome category.

## Expected Results

The expected outcome of this project is not a perfect prediction model. Instead, the system is expected to provide a transparent demonstration of how a basic average-based approach classifies student performance. The system helps to show whether simple academic indicators can provide useful early evaluation for students.

## Limitations

This project has important limitations that should be acknowledged:

- each indicator is given equal importance
- the method does not learn from previous student data
- the thresholds are fixed and may not suit every institution
- the model is limited to only three factors
- final outcomes may be affected by other influences beyond the selected indicators

## Future Improvements

Possible future work may include:

- weighted scoring
- larger datasets
- more academic indicators
- machine learning models
- database integration
- teacher dashboards
- student tracking over time

These are future enhancements and are not part of the current simple undergraduate system.
