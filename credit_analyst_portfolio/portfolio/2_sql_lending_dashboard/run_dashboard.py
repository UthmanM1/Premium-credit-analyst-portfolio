"""
SQL Lending Dashboard — Data Generator & Query Runner
=======================================================
Generates a synthetic lending database, runs all portfolio
analysis queries, and exports results as CSVs ready for
Looker Studio / Power BI visualisation.

Author: [Your Name]
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from datetime import date, timedelta
import random
import os

random.seed(42)
np.random.seed(42)

DB_PATH = "lending_portfolio.db"
EXPORT_DIR = "dashboard_exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# 1. GENERATE SYNTHETIC DATABASE
# ─────────────────────────────────────────────

def random_date(start_year=2022, end_year=2024):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def generate_database(n=5000):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS payments")
    cur.execute("DROP TABLE IF EXISTS loans")

    cur.execute("""
        CREATE TABLE loans (
            loan_id TEXT PRIMARY KEY, customer_id TEXT,
            origination_date TEXT, loan_amount REAL, loan_term_months INTEGER,
            interest_rate REAL, credit_score INTEGER, purpose TEXT,
            employment_years INTEGER, annual_income REAL, status TEXT,
            outstanding_balance REAL, total_paid REAL, months_on_book INTEGER
        )
    """)

    purposes = ['debt_consolidation','credit_card','home_improvement','other','medical']
    purpose_weights = [0.45, 0.25, 0.12, 0.10, 0.08]
    statuses = ['current','late_30','late_60','late_90','charged_off','paid_off']

    loans = []
    for i in range(n):
        cs = int(np.random.normal(650, 80))
        cs = max(300, min(850, cs))
        inc = float(np.random.lognormal(10.8, 0.5))
        inc = max(15000, min(300000, inc))
        amt = float(random.choice([5000,10000,15000,20000,25000,30000]))
        term = random.choice([36, 60])
        rate = (max(5, min(30, np.random.normal(7 if cs>720 else 15 if cs>650 else 22, 3))))
        orig_date = random_date()
        mob = min(term, (date.today() - orig_date).days // 30)

        default_prob = min(0.8, max(0.02,
            0.05 + (700 - cs) / 700 * 0.25
            + (amt / inc * 12) * 0.3
            + (term == 60) * 0.05
        ))

        rand = random.random()
        if mob >= term:
            status = 'paid_off'
        elif rand < default_prob * 0.6:
            status = 'charged_off'
        elif rand < default_prob * 0.7:
            status = 'late_90'
        elif rand < default_prob * 0.8:
            status = 'late_60'
        elif rand < default_prob * 0.9:
            status = 'late_30'
        else:
            status = 'current'

        monthly = amt * (rate/100/12) / (1 - (1 + rate/100/12)**-term)
        total_paid = monthly * mob * (0.0 if status == 'charged_off' else 1.0)
        balance = max(0, amt - (total_paid - monthly * mob * rate/100/12 * 0.3))

        loans.append((
            f"L{i:05d}", f"C{random.randint(1,4000):05d}",
            str(orig_date), round(amt,2), term, round(rate,2),
            cs, random.choices(purposes, purpose_weights)[0],
            random.randint(0,14), round(inc,2), status,
            round(balance,2), round(total_paid,2), mob
        ))

    cur.executemany("INSERT INTO loans VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", loans)

    # Payments table
    cur.execute("""
        CREATE TABLE payments (
            payment_id TEXT PRIMARY KEY, loan_id TEXT,
            payment_date TEXT, amount_due REAL, amount_paid REAL, days_late INTEGER
        )
    """)
    payments = []
    pid = 0
    for loan in loans[:1000]:  # payments for first 1000 loans
        loan_id, _, orig_str, amt, term, rate, *_ = loan
        orig = date.fromisoformat(orig_str)
        monthly = amt * (rate/100/12) / (1 - (1 + rate/100/12)**-term)
        for m in range(min(12, (date.today() - orig).days // 30)):
            pdate = orig + timedelta(days=30 * (m+1))
            if pdate > date.today():
                break
            late = max(0, int(np.random.exponential(3)) if random.random() < 0.15 else 0)
            paid = monthly if late < 90 else 0
            payments.append((f"P{pid:06d}", loan_id, str(pdate), round(monthly,2), round(paid,2), late))
            pid += 1

    cur.executemany("INSERT INTO payments VALUES (?,?,?,?,?,?)", payments)
    conn.commit()
    conn.close()
    print(f"Database created: {DB_PATH} ({n} loans, {len(payments)} payments)")

# ─────────────────────────────────────────────
# 2. RUN ANALYSIS QUERIES & EXPORT
# ─────────────────────────────────────────────

def run_and_export(conn, query, filename, title):
    df = pd.read_sql_query(query, conn)
    path = f"{EXPORT_DIR}/{filename}.csv"
    df.to_csv(path, index=False)
    print(f"  ✓ {title} → {path} ({len(df)} rows)")
    return df

def run_all_queries():
    conn = sqlite3.connect(DB_PATH)

    print("\n--- Running Portfolio Queries ---\n")

    overview = run_and_export(conn, """
        SELECT
            COUNT(*) AS total_loans,
            ROUND(SUM(loan_amount),0) AS total_originated,
            ROUND(SUM(outstanding_balance),0) AS total_outstanding,
            ROUND(AVG(loan_amount),0) AS avg_loan_size,
            ROUND(AVG(interest_rate),2) AS avg_interest_rate,
            ROUND(AVG(credit_score),0) AS avg_credit_score,
            ROUND(100.0*SUM(CASE WHEN status='charged_off' THEN 1 ELSE 0 END)/COUNT(*),2) AS default_rate_pct,
            ROUND(100.0*SUM(CASE WHEN status IN ('late_30','late_60','late_90') THEN 1 ELSE 0 END)/COUNT(*),2) AS delinquency_rate_pct
        FROM loans
    """, "01_portfolio_overview", "Portfolio Overview")

    by_purpose = run_and_export(conn, """
        SELECT purpose,
            COUNT(*) AS loan_count,
            ROUND(SUM(loan_amount),0) AS total_originated,
            ROUND(AVG(interest_rate),2) AS avg_rate,
            ROUND(AVG(credit_score),0) AS avg_credit_score,
            ROUND(100.0*SUM(CASE WHEN status='charged_off' THEN 1 ELSE 0 END)/COUNT(*),2) AS default_rate_pct
        FROM loans GROUP BY purpose ORDER BY loan_count DESC
    """, "02_breakdown_by_purpose", "Breakdown by Purpose")

    by_band = run_and_export(conn, """
        SELECT
            CASE WHEN credit_score>=720 THEN '1_Prime (720+)'
                 WHEN credit_score>=660 THEN '2_Near-Prime (660-719)'
                 WHEN credit_score>=620 THEN '3_Sub-Prime (620-659)'
                 ELSE '4_Deep Sub-Prime (<620)' END AS risk_band,
            COUNT(*) AS loan_count,
            ROUND(AVG(interest_rate),2) AS avg_rate,
            ROUND(SUM(loan_amount),0) AS total_originated,
            ROUND(100.0*SUM(CASE WHEN status='charged_off' THEN 1 ELSE 0 END)/COUNT(*),2) AS default_rate_pct
        FROM loans GROUP BY risk_band ORDER BY risk_band
    """, "03_breakdown_by_risk_band", "Breakdown by Risk Band")

    cohorts = run_and_export(conn, """
        SELECT
            SUBSTR(origination_date,1,7) AS cohort,
            COUNT(*) AS cohort_size,
            ROUND(SUM(loan_amount),0) AS total_originated,
            ROUND(AVG(interest_rate),2) AS avg_rate,
            ROUND(100.0*SUM(CASE WHEN status='charged_off' THEN 1 ELSE 0 END)/COUNT(*),2) AS default_rate_pct
        FROM loans GROUP BY cohort ORDER BY cohort
    """, "04_cohort_performance", "Cohort Performance")

    delinquency = run_and_export(conn, """
        SELECT status,
            COUNT(*) AS loan_count,
            ROUND(100.0*COUNT(*)/CAST((SELECT COUNT(*) FROM loans) AS FLOAT),2) AS pct_of_portfolio,
            ROUND(SUM(outstanding_balance),0) AS total_balance
        FROM loans
        WHERE status IN ('current','late_30','late_60','late_90','charged_off')
        GROUP BY status
    """, "05_delinquency_buckets", "Delinquency Buckets")

    conn.close()
    return overview, by_purpose, by_band, cohorts, delinquency

# ─────────────────────────────────────────────
# 3. GENERATE DASHBOARD CHART
# ─────────────────────────────────────────────

def generate_dashboard(by_purpose, by_band, cohorts, delinquency):
    fig = plt.figure(figsize=(18, 12))
    fig.patch.set_facecolor('#F8F9FA')
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

    CORAL = '#FF6B57'
    BLUE  = '#2196F3'
    GREEN = '#4CAF50'
    DARK  = '#1A1A2E'

    fig.suptitle('Lending Portfolio Dashboard', fontsize=18, fontweight='bold',
                 color=DARK, y=0.98)

    # 1. Default rate by purpose
    ax1 = fig.add_subplot(gs[0, 0])
    bp = by_purpose.sort_values('default_rate_pct', ascending=True)
    ax1.barh(bp['purpose'], bp['default_rate_pct'], color=CORAL, alpha=0.85)
    ax1.set_title('Default Rate by Purpose (%)', fontweight='bold', color=DARK)
    ax1.set_xlabel('Default Rate (%)')
    ax1.grid(axis='x', alpha=0.3)

    # 2. Default rate by risk band
    ax2 = fig.add_subplot(gs[0, 1])
    bb = by_band.copy()
    bb['label'] = bb['risk_band'].str.replace(r'^\d_', '', regex=True)
    ax2.bar(bb['label'], bb['default_rate_pct'], color=BLUE, alpha=0.85)
    ax2.set_title('Default Rate by Credit Band (%)', fontweight='bold', color=DARK)
    ax2.set_ylabel('Default Rate (%)')
    ax2.tick_params(axis='x', rotation=15)
    ax2.grid(axis='y', alpha=0.3)

    # 3. Portfolio volume by purpose
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.pie(by_purpose['loan_count'], labels=by_purpose['purpose'],
            autopct='%1.0f%%', colors=[CORAL, BLUE, GREEN, '#FFC107', '#9C27B0'],
            startangle=90)
    ax3.set_title('Portfolio Mix by Purpose', fontweight='bold', color=DARK)

    # 4. Cohort origination volume over time
    ax4 = fig.add_subplot(gs[1, 0:2])
    cohorts_recent = cohorts.tail(18)
    bars = ax4.bar(cohorts_recent['cohort'], cohorts_recent['total_originated'] / 1e6,
                   color=BLUE, alpha=0.7)
    ax4.plot(range(len(cohorts_recent)), cohorts_recent['default_rate_pct'],
             color=CORAL, marker='o', linewidth=2, markersize=4, label='Default Rate (%)')
    ax4.set_title('Monthly Originations & Cumulative Default Rate', fontweight='bold', color=DARK)
    ax4.set_ylabel('Originations (£M)')
    ax4.tick_params(axis='x', rotation=45)
    ax4_r = ax4.twinx()
    ax4_r.set_ylabel('Default Rate (%)', color=CORAL)
    ax4.legend(loc='upper left')
    ax4.grid(axis='y', alpha=0.3)

    # 5. Delinquency waterfall
    ax5 = fig.add_subplot(gs[1, 2])
    delinq_plot = delinquency[delinquency['status'] != 'paid_off'].copy()
    status_order = ['current','late_30','late_60','late_90','charged_off']
    status_labels = ['Current','30 DPD','60 DPD','90 DPD','Charged Off']
    status_colors = [GREEN, '#FFC107', '#FF9800', '#F44336', DARK]
    delinq_plot = delinq_plot.set_index('status').reindex(status_order).dropna()
    ax5.bar(status_labels[:len(delinq_plot)],
            delinq_plot['pct_of_portfolio'].values,
            color=status_colors[:len(delinq_plot)], alpha=0.85)
    ax5.set_title('Portfolio by Delinquency Status (%)', fontweight='bold', color=DARK)
    ax5.set_ylabel('% of Portfolio')
    ax5.tick_params(axis='x', rotation=15)
    ax5.grid(axis='y', alpha=0.3)

    plt.savefig(f'{EXPORT_DIR}/portfolio_dashboard.png', dpi=150, bbox_inches='tight',
                facecolor='#F8F9FA')
    plt.close()
    print(f"\n  ✓ Dashboard chart → {EXPORT_DIR}/portfolio_dashboard.png")

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("SQL LENDING PORTFOLIO DASHBOARD")
    print("=" * 60)

    generate_database(5000)
    overview, by_purpose, by_band, cohorts, delinquency = run_all_queries()

    print("\n--- Portfolio Snapshot ---")
    print(overview.to_string(index=False))

    generate_dashboard(by_purpose, by_band, cohorts, delinquency)

    print(f"\n✅ All exports saved to: ./{EXPORT_DIR}/")
    print("   Upload CSVs to Looker Studio at: https://lookerstudio.google.com")
