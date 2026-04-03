# 📊 SQL Lending Portfolio Analysis Dashboard

> End-to-end portfolio monitoring using SQL, Python & Looker Studio — built as part of a Credit Analyst portfolio.

## Overview

A production-style SQL analytics project analysing a personal loans portfolio. Covers the key reporting areas a Credit Analyst works on daily: cohort performance, delinquency tracking, NPV estimation, and pricing dynamics.

## What's Included

| File | Description |
|---|---|
| `lending_portfolio_analysis.sql` | Full suite of 15 portfolio analysis queries |
| `run_dashboard.py` | Generates SQLite database, runs queries, exports CSVs + charts |
| `dashboard_exports/` | Auto-generated CSV exports ready for Looker Studio |

## SQL Query Coverage

**Section 1 — Portfolio Overview**
- Portfolio snapshot (total loans, default rate, delinquency rate)
- Breakdown by loan purpose
- Breakdown by credit score band

**Section 2 — Cohort / Vintage Analysis**
- Monthly origination cohorts with cumulative default rates
- Vintage curve by months-on-book

**Section 3 — Delinquency Analysis**
- Delinquency bucket summary
- Roll rate analysis (30→60→90 DPD)

**Section 4 — NPV Analysis**
- Estimated NPV per origination cohort

**Section 5 — Pricing Dynamics**
- Risk-adjusted yield by credit tier
- Mispriced loan identification

**Section 6 — Monitoring Dashboard**
- Weekly portfolio health snapshot
- Top 10 highest-risk active accounts

## How to Run

```bash
pip install pandas numpy matplotlib
python run_dashboard.py
```

Then upload the CSVs in `dashboard_exports/` to [Looker Studio](https://lookerstudio.google.com) to build interactive charts.

## Skills Demonstrated

- `SQL` — window functions, CTEs, CASE/WHEN, aggregation, self-joins
- `Python` — SQLite, pandas, matplotlib
- Credit analytics — cohort analysis, vintage curves, roll rates, NPV, risk-adjusted yield
- Dashboard thinking — KPI selection, monitoring metrics
