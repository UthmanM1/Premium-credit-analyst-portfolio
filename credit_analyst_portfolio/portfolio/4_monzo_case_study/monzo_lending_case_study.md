# Monzo Lending Strategy Case Study
## A Data-Driven Analysis & Strategic Proposal

**Author:** [Your Name]  
**Date:** April 2025  
**Purpose:** Credit Analyst Portfolio — Strategic Analysis Exercise

---

## Executive Summary

Monzo has grown from a prepaid card to a full-service bank with over 9 million UK customers. Its lending portfolio — covering personal loans, overdrafts, and credit cards — represents both a significant revenue opportunity and a key risk management challenge.

This case study analyses Monzo's current lending position, identifies strategic opportunities, and proposes a data-driven approach to improving credit underwriting outcomes. The central recommendation is a **risk-tiered dynamic pricing model** combined with an **early intervention framework** that uses behavioural transaction data — a capability uniquely available to Monzo as a primary bank account provider.

---

## 1. Monzo's Lending Context

### 1.1 Product Offering
Monzo currently offers:
- **Personal loans** (up to £25,000, 1–5 years)
- **Overdrafts** (arranged, FCA-compliant pricing)
- **Monzo Flex** (buy now pay later / flexible credit card)
- **Business lending** (via Monzo Business)

### 1.2 Competitive Advantage
Unlike traditional banks, Monzo has access to **real-time transaction data** for customers who use it as their primary account. This creates a richer picture of financial behaviour than a traditional credit bureau check alone — enabling more accurate risk assessment and earlier identification of financial stress.

### 1.3 Key Challenges
| Challenge | Detail |
|---|---|
| Adverse selection | Lower-income / higher-risk customers may skew toward Monzo |
| Limited credit history | Young or thin-file customers common in Monzo's demographic |
| Portfolio seasoning | Relatively young lending book vs established banks |
| Regulatory | FCA Consumer Duty obligations and fair pricing requirements |

---

## 2. Data Analysis: What the Numbers Tell Us

### 2.1 Hypothetical Portfolio Health (illustrative)

Assuming a personal loans book of ~£800m outstanding:

| Metric | Estimated Value | Industry Benchmark |
|---|---|---|
| Average loan size | £7,500 | £8,200 |
| Average interest rate | 14.5% APR | 12.8% APR |
| 90-day delinquency rate | 3.8% | 3.2% |
| Charge-off rate (annualised) | 2.9% | 2.4% |
| Net Interest Margin (est.) | ~9–11% | ~8–10% |

> **Interpretation:** Monzo's rates are slightly above market average, suggesting either a higher-risk book or an opportunity to sharpen pricing for lower-risk customers and improve conversion.

### 2.2 Customer Segmentation (Behavioural)

Using transactional data, Monzo can segment borrowers beyond credit score:

```
Segment A — Stable Earners
  - Regular salary credits, low variance in spend
  - Low overdraft usage, savings pot holders
  - → Lower default risk than credit score alone suggests
  - Opportunity: Offer preferential rates to convert to personal loans

Segment B — Irregular Income
  - Gig economy / freelance patterns
  - Higher spend volatility, periodic overdraft use
  - → Standard credit score may underestimate stability
  - Opportunity: Use 12-month income smoothing to reassess

Segment C — Stress Indicators
  - Increasing % of income going to debt repayments
  - Gambling transactions present
  - Declining end-of-month balances over 3+ months
  - → Early delinquency predictor
  - Action: Proactive outreach, breathing space, hardship tools
```

---

## 3. Strategic Proposals

### Proposal 1: Dynamic Risk-Tiered Pricing

**Problem:** A flat or coarsely banded pricing model leaves margin on the table with low-risk customers and may inadequately price high-risk ones.

**Solution:** Implement a continuous risk score (0–100) blending:
- Bureau data (Experian/Equifax)
- Internal transaction behaviour (income stability, spend patterns)
- Application data (purpose, term preference)

**Expected outcome:**

| Risk Tier | Current Rate | Proposed Rate | Impact |
|---|---|---|---|
| Very Low Risk (score 85-100) | 9.9% APR | 7.9% APR | +15% conversion, lower default |
| Low Risk (70-84) | 12.9% APR | 11.4% APR | +8% conversion |
| Medium Risk (50-69) | 16.9% APR | 16.9% APR | No change |
| Higher Risk (35-49) | 21.9% APR | 23.9% APR | Better risk coverage |
| High Risk (<35) | Decline | Decline/refer | Reduced adverse selection |

**Implementation:**
1. Build logistic regression / gradient boosting model on existing loan performance
2. Shadow run for 3 months alongside existing strategy
3. Champion/challenger A/B test (80/20 split)
4. Monitor AUC-ROC, Gini coefficient, approval rate, and 90-day delinquency by cohort

---

### Proposal 2: Behavioural Early Warning System (EWS)

**Problem:** By the time a customer misses a payment, it's often too late for early intervention.

**Solution:** Build a monthly customer risk score using transaction signals:

```python
# Early Warning Score (EWS) — monthly refresh
# Key signals:

ews_signals = {
    'income_decline_3m':        weight_0.25,  # Salary dropped >15% vs 3m avg
    'dsr_increasing':           weight_0.20,  # Debt service ratio rising
    'end_balance_declining':    weight_0.18,  # Month-end balance trend negative
    'overdraft_days_increasing':weight_0.12,  # More days in overdraft
    'gambling_txns_present':    weight_0.10,  # Any gambling transaction
    'bill_payment_failures':    weight_0.10,  # Rejected direct debits
    'buy_now_pay_later_growth': weight_0.05,  # Increasing BNPL usage
}

# Score threshold → action:
# 70-100: Normal monitoring
# 50-69:  Suppress new credit offers, flag for review
# 30-49:  Proactive wellbeing outreach via app
# <30:    Hardship team contact, breathing space offer
```

**FCA Consumer Duty alignment:** This approach directly supports the Consumer Duty requirement to proactively support customers in financial difficulty — it's a regulatory strength, not just a credit risk tool.

**Expected impact:**
- 15–20% reduction in 90-day delinquency rate through earlier intervention
- Reduced charge-offs by catching customers 2–3 months earlier
- Positive NPS impact from proactive, non-punitive approach

---

### Proposal 3: Thin-File Customer Strategy

**Problem:** A significant portion of Monzo's young or recently immigrated customers have limited credit history, causing them to be automatically declined or offered high rates despite being responsible with money.

**Solution:** Use Monzo's open banking data advantage:
- **Rent payment tracking** — identify consistent rent payments (strong positive signal)
- **Income stability score** — 12-month average vs variance
- **Savings behaviour** — regular transfers to savings pots
- **Bill payment consistency** — utility/subscription reliability

These signals can be combined into an **alternative credit score** for thin-file customers, subject to appropriate model validation and FCA approval.

**Guardrails:**
- Strict loss limits during test & learn phase
- Concentration limits on thin-file cohort
- Enhanced monitoring cadence (monthly vs quarterly for standard cohorts)

---

## 4. Measurement Framework

### KPIs for Proposed Changes

| Proposal | Primary KPI | Secondary KPIs | Review Cadence |
|---|---|---|---|
| Dynamic Pricing | Risk-adjusted yield by tier | Approval rate, NIM | Monthly |
| Early Warning System | 30-day delinquency rate | EWS recall/precision | Monthly |
| Thin-File Strategy | Default rate vs control | Approval volume, AUC | Quarterly |

### Champion/Challenger Testing Protocol

```
Phase 1 (Month 1-3):   Shadow run — score new applicants with new model, 
                        fund with existing model. Compare predicted vs actual.

Phase 2 (Month 4-6):   80/20 split — 80% existing strategy (champion), 
                        20% new strategy (challenger).

Phase 3 (Month 7-9):   Analyse cohort performance. If challenger wins on
                        risk-adjusted yield with no material delinquency 
                        increase → full rollout.

Success criteria:       >5% improvement in risk-adjusted yield OR
                        >10% reduction in 30-day delinquency rate
                        with no statistically significant change in approval rate.
```

---

## 5. Regulatory Considerations

| Area | Requirement | Implication |
|---|---|---|
| FCA Consumer Duty | Avoid foreseeable harm, deliver good outcomes | EWS directly supports this |
| Creditworthiness Assessment | Must assess ability to repay | Behavioural data strengthens this |
| Responsible Lending | Vulnerability identification | EWS flags vulnerable customers |
| Model Risk | Explainability of automated decisions | Prefer interpretable models (logistic regression, scorecards) for customer-facing decisions |
| Data Protection | GDPR / UK GDPR | Transactional data use requires clear consent framework |

---

## 6. Conclusion

Monzo's data advantage — real-time transactional insight into customer financial behaviour — is its most defensible asset in credit risk. The proposals outlined here are designed to convert that advantage into measurably better outcomes: lower defaults, more precise pricing, earlier intervention, and expanded access for creditworthy customers currently underserved by bureau-only models.

The key to success is a disciplined test-and-learn culture: hypothesis → champion/challenger → cohort monitoring → iterate. This is consistent with Monzo's engineering-led, data-first culture and creates a compounding advantage as the lending book seasons.

---

## Appendix: Data Sources & References

- Bank of England: Consumer Credit Statistics — bankofengland.co.uk
- FCA: Consumer Duty Final Rules (PS22/9) — fca.org.uk
- FCA: Credit Card Market Study — fca.org.uk
- UK Finance: Consumer Finance Review 2024 — ukfinance.org.uk
- Monzo Annual Report 2023/24 — monzo.com/legal
- Experian: UK Credit Market Trends — experian.co.uk
