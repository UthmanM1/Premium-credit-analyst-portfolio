-- ============================================================
-- SQL LENDING PORTFOLIO ANALYSIS DASHBOARD
-- Credit Analyst Portfolio | Author: [Your Name]
-- ============================================================
-- Purpose: Analyse a personal loans portfolio across cohort
-- performance, delinquency, NPV, and pricing dynamics.
-- Compatible with: PostgreSQL / BigQuery / SQLite
-- ============================================================


-- ────────────────────────────────────────────────────────────
-- SECTION 0: SCHEMA & SAMPLE DATA SETUP
-- Run this block first to create and populate tables.
-- In a real environment, replace with your actual data source.
-- ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS loans (
    loan_id           TEXT PRIMARY KEY,
    customer_id       TEXT,
    origination_date  DATE,
    loan_amount       NUMERIC(12,2),
    loan_term_months  INTEGER,
    interest_rate     NUMERIC(5,2),
    credit_score      INTEGER,
    purpose           TEXT,
    employment_years  INTEGER,
    annual_income     NUMERIC(12,2),
    status            TEXT,   -- 'current', 'charged_off', 'paid_off', 'late_30', 'late_60', 'late_90'
    outstanding_balance NUMERIC(12,2),
    total_paid        NUMERIC(12,2),
    months_on_book    INTEGER
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id    TEXT PRIMARY KEY,
    loan_id       TEXT REFERENCES loans(loan_id),
    payment_date  DATE,
    amount_due    NUMERIC(10,2),
    amount_paid   NUMERIC(10,2),
    days_late     INTEGER
);

-- ────────────────────────────────────────────────────────────
-- SECTION 1: PORTFOLIO OVERVIEW
-- High-level summary of the book
-- ────────────────────────────────────────────────────────────

-- 1a. Portfolio snapshot
SELECT
    COUNT(*)                                        AS total_loans,
    SUM(loan_amount)                                AS total_originated_gbp,
    SUM(outstanding_balance)                        AS total_outstanding_gbp,
    AVG(loan_amount)                                AS avg_loan_size_gbp,
    AVG(interest_rate)                              AS avg_interest_rate_pct,
    AVG(credit_score)                               AS avg_credit_score,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'charged_off' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                               AS default_rate_pct,
    ROUND(
        100.0 * SUM(CASE WHEN status IN ('late_30','late_60','late_90') THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                               AS delinquency_rate_pct
FROM loans;


-- 1b. Portfolio breakdown by loan purpose
SELECT
    purpose,
    COUNT(*)                                              AS loan_count,
    ROUND(SUM(loan_amount), 0)                            AS total_originated,
    ROUND(AVG(interest_rate), 2)                          AS avg_rate,
    ROUND(AVG(credit_score), 0)                           AS avg_credit_score,
    ROUND(100.0 * SUM(CASE WHEN status='charged_off' THEN 1 ELSE 0 END) / COUNT(*), 2) AS default_rate_pct
FROM loans
GROUP BY purpose
ORDER BY loan_count DESC;


-- 1c. Portfolio breakdown by credit score band
SELECT
    CASE
        WHEN credit_score >= 720 THEN 'Prime (720+)'
        WHEN credit_score >= 660 THEN 'Near-Prime (660-719)'
        WHEN credit_score >= 620 THEN 'Sub-Prime (620-659)'
        ELSE 'Deep Sub-Prime (<620)'
    END                                                    AS risk_band,
    COUNT(*)                                               AS loan_count,
    ROUND(AVG(interest_rate), 2)                           AS avg_rate_pct,
    ROUND(SUM(loan_amount), 0)                             AS total_originated,
    ROUND(100.0 * SUM(CASE WHEN status='charged_off' THEN 1 ELSE 0 END) / COUNT(*), 2) AS default_rate_pct
FROM loans
GROUP BY risk_band
ORDER BY MIN(credit_score) DESC;


-- ────────────────────────────────────────────────────────────
-- SECTION 2: COHORT PERFORMANCE ANALYSIS
-- Track how loans originated in the same period perform over time
-- This is the core of vintage analysis used in credit teams
-- ────────────────────────────────────────────────────────────

-- 2a. Monthly origination cohorts with cumulative default rates
SELECT
    TO_CHAR(origination_date, 'YYYY-MM')           AS origination_cohort,
    COUNT(*)                                        AS cohort_size,
    SUM(loan_amount)                                AS total_originated,
    AVG(interest_rate)                              AS avg_rate,
    AVG(credit_score)                               AS avg_credit_score,
    SUM(CASE WHEN status = 'charged_off' THEN 1 ELSE 0 END) AS defaults,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'charged_off' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                               AS cumulative_default_rate_pct
FROM loans
GROUP BY TO_CHAR(origination_date, 'YYYY-MM')
ORDER BY origination_cohort;


-- 2b. Vintage curve — default rate by months on book for each quarterly cohort
-- This shows how quickly different cohorts deteriorate
SELECT
    TO_CHAR(DATE_TRUNC('quarter', origination_date), 'YYYY-Q"Q"') AS vintage_quarter,
    months_on_book,
    COUNT(*)                                                        AS loans_in_cohort,
    SUM(CASE WHEN status = 'charged_off' THEN 1 ELSE 0 END)        AS cumulative_defaults,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'charged_off' THEN 1 ELSE 0 END) / COUNT(*), 3
    )                                                               AS cum_default_rate_pct
FROM loans
GROUP BY vintage_quarter, months_on_book
ORDER BY vintage_quarter, months_on_book;


-- ────────────────────────────────────────────────────────────
-- SECTION 3: DELINQUENCY ANALYSIS
-- Understanding payment behaviour and early warning signals
-- ────────────────────────────────────────────────────────────

-- 3a. Delinquency bucket summary
SELECT
    status                                          AS delinquency_status,
    COUNT(*)                                        AS loan_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_portfolio,
    ROUND(SUM(outstanding_balance), 0)              AS total_balance_at_risk,
    ROUND(AVG(credit_score), 0)                     AS avg_credit_score,
    ROUND(AVG(interest_rate), 2)                    AS avg_interest_rate
FROM loans
WHERE status IN ('current', 'late_30', 'late_60', 'late_90', 'charged_off')
GROUP BY status
ORDER BY
    CASE status
        WHEN 'current'     THEN 1
        WHEN 'late_30'     THEN 2
        WHEN 'late_60'     THEN 3
        WHEN 'late_90'     THEN 4
        WHEN 'charged_off' THEN 5
    END;


-- 3b. Roll rate analysis — how accounts move between delinquency buckets
-- (requires payment-level data)
WITH payment_status AS (
    SELECT
        p.loan_id,
        p.payment_date,
        CASE
            WHEN p.days_late = 0  THEN 'Current'
            WHEN p.days_late <= 30 THEN '1-30 DPD'
            WHEN p.days_late <= 60 THEN '31-60 DPD'
            WHEN p.days_late <= 90 THEN '61-90 DPD'
            ELSE '90+ DPD'
        END AS bucket,
        LAG(CASE
            WHEN p.days_late = 0  THEN 'Current'
            WHEN p.days_late <= 30 THEN '1-30 DPD'
            WHEN p.days_late <= 60 THEN '31-60 DPD'
            WHEN p.days_late <= 90 THEN '61-90 DPD'
            ELSE '90+ DPD'
        END) OVER (PARTITION BY p.loan_id ORDER BY p.payment_date) AS prev_bucket
    FROM payments p
)
SELECT
    prev_bucket         AS from_bucket,
    bucket              AS to_bucket,
    COUNT(*)            AS transitions,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY prev_bucket), 2) AS roll_rate_pct
FROM payment_status
WHERE prev_bucket IS NOT NULL
GROUP BY prev_bucket, bucket
ORDER BY prev_bucket, to_bucket;


-- ────────────────────────────────────────────────────────────
-- SECTION 4: NET PRESENT VALUE (NPV) ANALYSIS
-- Assess profitability of lending cohorts
-- ────────────────────────────────────────────────────────────

-- 4a. Estimated NPV per loan cohort
-- NPV = PV of expected interest income - PV of expected losses - cost of funds
WITH cohort_economics AS (
    SELECT
        TO_CHAR(origination_date, 'YYYY-MM')                     AS cohort,
        COUNT(*)                                                   AS loans,
        SUM(loan_amount)                                           AS total_principal,
        AVG(interest_rate) / 100                                   AS avg_rate,
        AVG(loan_term_months)                                      AS avg_term,
        ROUND(
            100.0 * SUM(CASE WHEN status='charged_off' THEN 1 ELSE 0 END) / COUNT(*), 4
        )                                                          AS default_rate,
        SUM(total_paid)                                            AS actual_collections,
        SUM(loan_amount) - SUM(total_paid)                         AS estimated_loss
    FROM loans
    GROUP BY TO_CHAR(origination_date, 'YYYY-MM')
)
SELECT
    cohort,
    loans,
    ROUND(total_principal, 0)                                      AS total_principal,
    ROUND(avg_rate * 100, 2)                                       AS avg_rate_pct,
    default_rate                                                   AS default_rate_pct,
    ROUND(actual_collections, 0)                                   AS actual_collections,
    ROUND(estimated_loss, 0)                                       AS estimated_loss,
    -- Simplified NPV: interest income - losses - assumed 5% cost of funds
    ROUND(
        actual_collections
        - total_principal           -- return of principal
        - estimated_loss            -- credit losses
        - (total_principal * 0.05 * avg_term / 12)  -- cost of funds at 5%
    , 0)                                                           AS estimated_npv
FROM cohort_economics
ORDER BY cohort;


-- ────────────────────────────────────────────────────────────
-- SECTION 5: PRICING DYNAMICS
-- How interest rate pricing relates to risk and volume
-- ────────────────────────────────────────────────────────────

-- 5a. Risk-adjusted yield analysis by credit band
SELECT
    CASE
        WHEN credit_score >= 720 THEN 'Prime'
        WHEN credit_score >= 660 THEN 'Near-Prime'
        WHEN credit_score >= 620 THEN 'Sub-Prime'
        ELSE 'Deep Sub-Prime'
    END                                                            AS risk_tier,
    COUNT(*)                                                       AS loan_count,
    ROUND(AVG(interest_rate), 2)                                   AS avg_gross_rate,
    ROUND(AVG(CASE WHEN status='charged_off' THEN loan_amount ELSE 0 END)
          / NULLIF(AVG(loan_amount), 0) * 100, 2)                  AS avg_loss_rate_pct,
    -- Risk-adjusted yield = gross rate - expected loss rate
    ROUND(AVG(interest_rate) -
          (AVG(CASE WHEN status='charged_off' THEN loan_amount ELSE 0 END)
           / NULLIF(AVG(loan_amount), 0) * 100), 2)                AS risk_adjusted_yield_pct
FROM loans
GROUP BY risk_tier
ORDER BY MIN(credit_score) DESC;


-- 5b. Identify potentially mispriced loans (high risk, low rate)
SELECT
    loan_id,
    credit_score,
    interest_rate,
    loan_amount,
    dti_ratio,
    status,
    CASE
        WHEN credit_score < 620 AND interest_rate < 15  THEN 'UNDERPRICED — High Risk'
        WHEN credit_score > 720 AND interest_rate > 20  THEN 'OVERPRICED — Low Risk'
        ELSE 'Appropriately Priced'
    END                                                            AS pricing_assessment
FROM loans
CROSS JOIN (
    SELECT AVG(loan_amount / annual_income * 12) AS avg_dti FROM loans
) dti_avg
WHERE credit_score < 620 AND interest_rate < 15
   OR credit_score > 720 AND interest_rate > 20
ORDER BY credit_score ASC, interest_rate ASC;


-- ────────────────────────────────────────────────────────────
-- SECTION 6: MONITORING DASHBOARD QUERIES
-- Production-style queries for ongoing portfolio monitoring
-- ────────────────────────────────────────────────────────────

-- 6a. Weekly portfolio health snapshot (parameterise as needed)
SELECT
    CURRENT_DATE                                        AS report_date,
    COUNT(*)                                            AS active_loans,
    ROUND(SUM(outstanding_balance), 0)                  AS total_exposure,
    ROUND(SUM(CASE WHEN status='late_30' THEN outstanding_balance ELSE 0 END), 0) AS bal_30dpd,
    ROUND(SUM(CASE WHEN status='late_60' THEN outstanding_balance ELSE 0 END), 0) AS bal_60dpd,
    ROUND(SUM(CASE WHEN status='late_90' THEN outstanding_balance ELSE 0 END), 0) AS bal_90dpd,
    ROUND(
        100.0 * SUM(CASE WHEN status IN ('late_30','late_60','late_90') THEN outstanding_balance ELSE 0 END)
        / NULLIF(SUM(outstanding_balance), 0), 2
    )                                                   AS delinquency_rate_by_balance_pct,
    ROUND(
        100.0 * SUM(CASE WHEN status='charged_off' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                   AS cumulative_default_rate_pct
FROM loans
WHERE status != 'paid_off';


-- 6b. Top 10 highest-risk active accounts (for collections prioritisation)
SELECT
    loan_id,
    customer_id,
    loan_amount,
    outstanding_balance,
    credit_score,
    interest_rate,
    months_on_book,
    status
FROM loans
WHERE status IN ('late_30', 'late_60', 'late_90')
ORDER BY
    CASE status WHEN 'late_90' THEN 1 WHEN 'late_60' THEN 2 ELSE 3 END,
    outstanding_balance DESC
LIMIT 10;
