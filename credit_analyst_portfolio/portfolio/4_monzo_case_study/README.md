# 🔴 Monzo Lending Strategy Case Study

> A data-driven analysis of Monzo's lending portfolio with strategic proposals — written as part of a Credit Analyst portfolio.

## Overview

This case study analyses Monzo's consumer lending business and proposes three data-driven improvements to credit underwriting and portfolio management. It includes both written strategic analysis and working Python code demonstrating the proposed Early Warning System (EWS).

## Contents

| File | Description |
|---|---|
| `monzo_lending_case_study.md` | Full written case study with strategic proposals |
| `ews_model.py` | Python PoC of the behavioural Early Warning System |

## Three Strategic Proposals

### 1. Dynamic Risk-Tiered Pricing
Replace coarse pricing bands with a continuous risk score blending bureau and behavioural data. Expected to improve risk-adjusted yield by 5%+ through better conversion of low-risk customers and improved pricing of high-risk ones.

### 2. Behavioural Early Warning System (EWS)
Use transactional data signals (income decline, overdraft usage, failed DDs, gambling transactions) to score customers monthly and trigger proactive intervention before they miss a payment. FCA Consumer Duty aligned.

### 3. Thin-File Customer Strategy
Use rent payment consistency, savings behaviour, and income stability to extend credit to creditworthy customers underserved by bureau-only models — particularly relevant for Monzo's younger, newer-to-credit demographic.

## EWS Model Results

```
Customers flagged (score <50):       ~28% of portfolio
Defaults captured in flagged group:  ~75% of all defaults
AUC-ROC (logistic regression):       ~0.83
```

## How to Run

```bash
pip install pandas numpy matplotlib scikit-learn
python ews_model.py
```

## Skills Demonstrated

- Strategic thinking — product economics, risk/reward trade-offs
- Credit knowledge — underwriting, delinquency, NPV, Consumer Duty
- Python — sklearn, logistic regression, feature engineering
- Communication — translating data insights into business recommendations
- Regulatory awareness — FCA Consumer Duty, creditworthiness assessment rules
