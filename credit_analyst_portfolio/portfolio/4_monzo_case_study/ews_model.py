"""
Monzo Early Warning System (EWS) — Proof of Concept
=====================================================
Demonstrates the behavioural early warning model proposed
in the case study using simulated transactional data.

Author: [Your Name]
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)
N = 3000

# ─────────────────────────────────────────────
# 1. SIMULATE BEHAVIOURAL FEATURES
# ─────────────────────────────────────────────

def simulate_customer_data(n):
    # Will go delinquent in next 90 days?
    will_default = np.random.binomial(1, 0.12, n)

    # Signals — correlated with default outcome
    income_decline     = np.where(will_default, np.random.uniform(0.1, 0.5, n), np.random.uniform(-0.1, 0.15, n))
    dsr_ratio          = np.where(will_default, np.random.uniform(0.35, 0.85, n), np.random.uniform(0.05, 0.40, n))
    end_bal_trend      = np.where(will_default, np.random.uniform(-500, -50, n), np.random.uniform(-100, 400, n))
    overdraft_days     = np.where(will_default, np.random.randint(8, 28, n), np.random.randint(0, 10, n))
    gambling_flag      = np.where(will_default, np.random.binomial(1, 0.35, n), np.random.binomial(1, 0.08, n))
    failed_dds         = np.where(will_default, np.random.randint(1, 5, n), np.random.randint(0, 2, n))
    bnpl_growth        = np.where(will_default, np.random.uniform(0.1, 0.8, n), np.random.uniform(-0.1, 0.3, n))
    months_as_customer = np.random.randint(3, 48, n)
    credit_score       = np.where(will_default,
                                   np.random.normal(610, 60, n),
                                   np.random.normal(680, 55, n)).clip(300, 850).astype(int)

    return pd.DataFrame({
        'will_default_90d':         will_default,
        'income_decline_3m':        income_decline.round(3),
        'debt_service_ratio':       dsr_ratio.round(3),
        'end_balance_trend_gbp':    end_bal_trend.round(2),
        'overdraft_days_last_month':overdraft_days,
        'gambling_transactions':    gambling_flag,
        'failed_direct_debits':     failed_dds,
        'bnpl_spend_growth':        bnpl_growth.round(3),
        'months_as_customer':       months_as_customer,
        'credit_score':             credit_score,
    })

df = simulate_customer_data(N)

print("=" * 60)
print("MONZO EARLY WARNING SYSTEM — PROOF OF CONCEPT")
print("=" * 60)
print(f"\nDataset: {len(df):,} customers | Base delinquency rate: {df['will_default_90d'].mean():.1%}\n")

# ─────────────────────────────────────────────
# 2. RULE-BASED EWS SCORE (interpretable)
# ─────────────────────────────────────────────

def calculate_ews_score(row):
    score = 100
    if row['income_decline_3m'] > 0.15:        score -= 25
    elif row['income_decline_3m'] > 0.05:       score -= 10
    if row['debt_service_ratio'] > 0.50:        score -= 20
    elif row['debt_service_ratio'] > 0.35:      score -= 10
    if row['end_balance_trend_gbp'] < -200:     score -= 18
    elif row['end_balance_trend_gbp'] < 0:      score -= 8
    if row['overdraft_days_last_month'] > 15:   score -= 12
    elif row['overdraft_days_last_month'] > 7:  score -= 6
    if row['gambling_transactions'] == 1:        score -= 10
    if row['failed_direct_debits'] >= 2:        score -= 10
    elif row['failed_direct_debits'] == 1:      score -= 5
    if row['bnpl_spend_growth'] > 0.4:          score -= 5
    return max(0, score)

df['ews_score'] = df.apply(calculate_ews_score, axis=1)

def ews_action(score):
    if score >= 70:   return 'Green — Normal'
    elif score >= 50: return 'Amber — Suppress Offers'
    elif score >= 30: return 'Orange — App Outreach'
    else:             return 'Red — Hardship Contact'

df['ews_action'] = df['ews_score'].apply(ews_action)

print("--- EWS Score Distribution by Action Band ---")
action_summary = df.groupby('ews_action').agg(
    customers=('ews_score','count'),
    avg_score=('ews_score','mean'),
    default_rate=('will_default_90d','mean')
).round(3)
print(action_summary.to_string())

# ─────────────────────────────────────────────
# 3. ML-BASED EWS (logistic regression)
# ─────────────────────────────────────────────

features = ['income_decline_3m','debt_service_ratio','end_balance_trend_gbp',
            'overdraft_days_last_month','gambling_transactions','failed_direct_debits',
            'bnpl_spend_growth','credit_score']

from sklearn.model_selection import train_test_split
X = df[features]
y = df['will_default_90d']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

scaler = StandardScaler()
model  = LogisticRegression(max_iter=500, random_state=42)
model.fit(scaler.fit_transform(X_train), y_train)

y_prob = model.predict_proba(scaler.transform(X_test))[:,1]
auc = roc_auc_score(y_test, y_prob)
print(f"\n--- Logistic Regression EWS Model ---")
print(f"AUC-ROC: {auc:.4f}")
print(classification_report(y_test, model.predict(scaler.transform(X_test)),
                             target_names=['No Default','Default']))

# ─────────────────────────────────────────────
# 4. IMPACT SIMULATION
# ─────────────────────────────────────────────

# How much delinquency is caught in the Red/Orange bands?
red_orange = df[df['ews_score'] < 50]
pct_defaults_caught = red_orange['will_default_90d'].sum() / df['will_default_90d'].sum()
pct_portfolio_flagged = len(red_orange) / len(df)

print(f"\n--- EWS Impact Simulation ---")
print(f"Customers flagged (score <50):       {pct_portfolio_flagged:.1%} of portfolio")
print(f"Defaults captured in flagged group:  {pct_defaults_caught:.1%} of all defaults")
print(f"Expected delinquency reduction*:     ~15-20% with early intervention")
print(f"* Assuming 20% of flagged customers respond positively to intervention")

# ─────────────────────────────────────────────
# 5. VISUALISATION
# ─────────────────────────────────────────────

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('Monzo Early Warning System — PoC Results', fontsize=14, fontweight='bold', color='#1A1A2E')

CORAL, BLUE, GREEN, AMBER = '#FF6B57', '#1565C0', '#2E7D32', '#F57F17'

# 1. EWS score distribution
axes[0].hist(df[df['will_default_90d']==0]['ews_score'], bins=25, alpha=0.7, color=GREEN, label='No Default')
axes[0].hist(df[df['will_default_90d']==1]['ews_score'], bins=25, alpha=0.7, color=CORAL, label='Default')
axes[0].axvline(50, color='orange', lw=2, linestyle='--', label='Action threshold (50)')
axes[0].set_title('EWS Score Distribution')
axes[0].set_xlabel('EWS Score')
axes[0].legend(fontsize=8)
axes[0].grid(alpha=0.3)

# 2. Default rate by action band
action_order = ['Red — Hardship Contact','Orange — App Outreach','Amber — Suppress Offers','Green — Normal']
action_colors = [CORAL, '#FF9800', AMBER, GREEN]
band_defaults = []
for band in action_order:
    subset = df[df['ews_action'] == band]
    if len(subset) > 0:
        band_defaults.append((band.split('—')[0].strip(), subset['will_default_90d'].mean(), len(subset)))

labels  = [b[0] for b in band_defaults]
rates   = [b[1] for b in band_defaults]
counts  = [b[2] for b in band_defaults]
bars = axes[1].bar(labels, rates, color=action_colors[:len(labels)], alpha=0.85)
for bar, count in zip(bars, counts):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.003,
                  f'n={count}', ha='center', fontsize=8)
axes[1].set_title('Default Rate by EWS Band')
axes[1].set_ylabel('90-day Default Rate')
axes[1].grid(axis='y', alpha=0.3)

# 3. Feature importance (logistic regression coefficients)
coefs = pd.Series(np.abs(model.coef_[0]), index=features).sort_values(ascending=True)
axes[2].barh(coefs.index, coefs.values, color=BLUE, alpha=0.8)
axes[2].set_title('Feature Importance (|Coef|)')
axes[2].set_xlabel('Absolute Coefficient')
axes[2].grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('ews_results.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n✅ Saved: ews_results.png")
