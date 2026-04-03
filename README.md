# 📁 Credit Analyst Portfolio

> Data-driven credit risk & lending analytics projects — built to demonstrate skills for a Credit Analyst role in fintech/consumer lending.

**Author:** Uthman Mustapha 
**Target Role:** Credit Analyst — Monzo (Borrowing Team)  
**Skills:** SQL · Python · Excel · Looker/BI · Credit Risk · Lending Economics

---

## Projects

### 1. 🏦 [Loan Default Prediction Model](./1_loan_default_model/)
Build and evaluate three credit scoring models (Logistic Regression, Decision Tree, Random Forest) to predict personal loan defaults. Covers EDA, feature engineering, model evaluation (AUC-ROC), and a risk scorecard output.

**Stack:** Python · scikit-learn · pandas · matplotlib

---

### 2. 📊 [SQL Lending Portfolio Analysis Dashboard](./2_sql_lending_dashboard/)
Production-style SQL queries covering the full portfolio analytics stack: cohort analysis, vintage curves, delinquency roll rates, NPV estimation, and pricing dynamics. Includes a Python runner that generates a Looker-ready dashboard.

**Stack:** SQL (SQLite/PostgreSQL) · Python · Looker Studio

---

### 3. 🇬🇧 [UK Unsecured Lending Market Analysis](./3_uk_lending_market_analysis/)
Macro-level market analysis using Bank of England and UK Finance data. Covers market sizing, pricing compression, the macro impact on defaults, and the rise of challenger banks including Monzo.

**Stack:** Python · pandas · matplotlib · BoE/FCA data

---

### 4. 🔴 [Monzo Lending Strategy Case Study](./4_monzo_case_study/)
Written strategic case study proposing three data-driven improvements to Monzo's lending book: dynamic risk-tiered pricing, a behavioural Early Warning System, and a thin-file customer strategy. Includes a working Python PoC of the EWS model.

**Stack:** Python · scikit-learn · Strategic analysis · FCA regulatory context

---

## Skills Demonstrated

| Skill | Where |
|---|---|
| SQL — cohort analysis, CTEs, window functions | Project 2 |
| Python — ML models, feature engineering, visualisation | Projects 1, 3, 4 |
| Credit risk — PD modelling, scorecards, NPV | Projects 1, 2, 4 |
| Market analysis — macro, pricing dynamics | Project 3 |
| Strategic thinking — proposals with KPIs & testing plans | Project 4 |
| FCA / regulatory awareness — Consumer Duty, responsible lending | Project 4 |
| Data storytelling — charts, dashboards, written insight | All projects |

---

## How to Run Any Project

Each project folder contains a `README.md` with specific instructions. General setup:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn
cd 1_loan_default_model && python loan_default_model.py
cd 2_sql_lending_dashboard && python run_dashboard.py
cd 3_uk_lending_market_analysis && python uk_lending_market_analysis.py
cd 4_monzo_case_study && python ews_model.py
```
