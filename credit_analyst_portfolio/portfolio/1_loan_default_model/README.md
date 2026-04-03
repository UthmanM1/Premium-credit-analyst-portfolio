# 🏦 Loan Default Prediction Model

> Credit risk scoring using machine learning — built as part of a Credit Analyst portfolio.

## Overview

This project builds and evaluates three credit risk models to predict whether a borrower will default on an unsecured personal loan. It mirrors the kind of analytical work done by credit analysts at fintechs and banks to inform underwriting strategy.

## What It Does

- Generates a realistic 10,000-row lending dataset (swap in real Lending Club data from Kaggle)
- Performs exploratory data analysis (EDA) on key credit variables
- Engineers features relevant to credit risk (DTI, payment-to-income, delinquency flags)
- Trains and compares three models: Logistic Regression, Decision Tree, Random Forest
- Outputs ROC curves, feature importance charts, and a sample risk scorecard

## Key Findings

| Model | AUC-ROC |
|---|---|
| Logistic Regression | ~0.82 |
| Decision Tree | ~0.79 |
| Random Forest | ~0.86 |

**Top predictors of default:** credit score, debt-to-income ratio, payment-to-income ratio, delinquency history, and interest rate.

## Output Charts

| Chart | Description |
|---|---|
| `eda_analysis.png` | Distribution of key variables by loan outcome |
| `model_evaluation.png` | ROC curves + feature importance |

## How to Run

```bash
pip install pandas numpy matplotlib seaborn scikit-learn
python loan_default_model.py
```

To use real data, download the [Lending Club dataset from Kaggle](https://www.kaggle.com/datasets/wordsforthewise/lending-club) and replace the data generation section with:
```python
df = pd.read_csv('lending_club_loans.csv', low_memory=False)
```

## Skills Demonstrated

- `Python` — pandas, scikit-learn, matplotlib, seaborn
- Credit risk concepts — PD modelling, scorecard logic, DTI analysis
- ML fundamentals — train/test split, pipeline, ROC-AUC evaluation
- Feature engineering — derived credit variables
