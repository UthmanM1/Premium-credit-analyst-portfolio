"""
Loan Default Prediction Model
==============================
Credit Risk Scoring using Logistic Regression, Decision Tree & Random Forest
Dataset: Lending Club public loan data (simulated for portfolio demonstration)

Author: [Your Name]
Purpose: Credit Analyst Portfolio — Monzo Application
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, roc_curve, ConfusionMatrixDisplay
)
from sklearn.pipeline import Pipeline
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# 1. GENERATE REALISTIC SYNTHETIC LENDING DATA
# ─────────────────────────────────────────────
# In practice: download from https://www.kaggle.com/datasets/wordsforthewise/lending-club
# and replace this section with: df = pd.read_csv('lending_club_loans.csv')

np.random.seed(42)
N = 10_000

def generate_loan_data(n):
    credit_score = np.random.normal(650, 80, n).clip(300, 850).astype(int)
    annual_income = np.random.lognormal(10.8, 0.5, n).clip(15000, 300000)
    loan_amount = np.random.choice([5000, 10000, 15000, 20000, 25000, 30000], n,
                                    p=[0.25, 0.25, 0.20, 0.15, 0.10, 0.05])
    loan_term = np.random.choice([36, 60], n, p=[0.6, 0.4])
    interest_rate = np.where(credit_score > 720, np.random.uniform(5, 10, n),
                    np.where(credit_score > 650, np.random.uniform(10, 18, n),
                             np.random.uniform(18, 30, n)))
    dti = (loan_amount / annual_income * 12).clip(0, 0.8)
    employment_length = np.random.choice(range(0, 15), n,
                                          p=[0.1,0.1,0.08,0.08,0.08,0.07,0.07,
                                             0.07,0.07,0.06,0.05,0.04,0.04,0.04,0.05])
    delinq_2yrs = np.random.choice([0, 1, 2, 3], n, p=[0.75, 0.15, 0.07, 0.03])
    purpose = np.random.choice(
        ['debt_consolidation', 'credit_card', 'home_improvement', 'other', 'medical'],
        n, p=[0.45, 0.25, 0.12, 0.10, 0.08]
    )

    # Default probability influenced by key credit factors
    default_prob = (
        0.05
        + (700 - credit_score) / 700 * 0.25
        + dti * 0.30
        + delinq_2yrs * 0.08
        + (loan_term == 60) * 0.05
        + (interest_rate > 20) * 0.10
    ).clip(0.02, 0.85)

    default = (np.random.uniform(0, 1, n) < default_prob).astype(int)

    return pd.DataFrame({
        'credit_score': credit_score,
        'annual_income': annual_income.astype(int),
        'loan_amount': loan_amount,
        'loan_term_months': loan_term,
        'interest_rate': interest_rate.round(2),
        'dti_ratio': dti.round(4),
        'employment_length_years': employment_length,
        'delinquencies_2yrs': delinq_2yrs,
        'purpose': purpose,
        'default': default
    })

df = generate_loan_data(N)
print("=" * 60)
print("LOAN DEFAULT PREDICTION MODEL")
print("=" * 60)
print(f"\nDataset shape: {df.shape}")
print(f"Default rate:  {df['default'].mean():.1%}\n")
print(df.head())

# ─────────────────────────────
# 2. EXPLORATORY DATA ANALYSIS
# ─────────────────────────────
print("\n--- Descriptive Statistics ---")
print(df.describe().round(2))

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle('Loan Portfolio — Exploratory Data Analysis', fontsize=16, fontweight='bold', color='#1A1A2E')

colors = ['#4CAF50', '#FF6B57']

# Default rate
axes[0,0].bar(['Performing', 'Default'],
               [df['default'].value_counts()[0], df['default'].value_counts()[1]],
               color=colors)
axes[0,0].set_title('Loan Status Distribution')
axes[0,0].set_ylabel('Count')

# Credit score by default
df[df['default']==0]['credit_score'].hist(ax=axes[0,1], bins=40, alpha=0.7, color='#4CAF50', label='Performing')
df[df['default']==1]['credit_score'].hist(ax=axes[0,1], bins=40, alpha=0.7, color='#FF6B57', label='Default')
axes[0,1].set_title('Credit Score Distribution by Outcome')
axes[0,1].set_xlabel('Credit Score')
axes[0,1].legend()

# DTI ratio
df[df['default']==0]['dti_ratio'].hist(ax=axes[0,2], bins=40, alpha=0.7, color='#4CAF50', label='Performing')
df[df['default']==1]['dti_ratio'].hist(ax=axes[0,2], bins=40, alpha=0.7, color='#FF6B57', label='Default')
axes[0,2].set_title('Debt-to-Income Ratio by Outcome')
axes[0,2].set_xlabel('DTI Ratio')
axes[0,2].legend()

# Default rate by purpose
purpose_default = df.groupby('purpose')['default'].mean().sort_values(ascending=False)
axes[1,0].barh(purpose_default.index, purpose_default.values, color='#FF6B57', alpha=0.8)
axes[1,0].set_title('Default Rate by Loan Purpose')
axes[1,0].set_xlabel('Default Rate')

# Default rate by credit score bucket
df['credit_bucket'] = pd.cut(df['credit_score'],
                              bins=[300, 580, 620, 660, 720, 850],
                              labels=['<580', '580-619', '620-659', '660-719', '720+'])
bucket_default = df.groupby('credit_bucket', observed=True)['default'].mean()
axes[1,1].bar(bucket_default.index.astype(str), bucket_default.values, color='#2196F3', alpha=0.8)
axes[1,1].set_title('Default Rate by Credit Score Bucket')
axes[1,1].set_xlabel('Credit Score Range')
axes[1,1].set_ylabel('Default Rate')

# Interest rate vs default
axes[1,2].scatter(df[df['default']==0]['interest_rate'],
                   df[df['default']==0]['credit_score'],
                   alpha=0.1, color='#4CAF50', s=5, label='Performing')
axes[1,2].scatter(df[df['default']==1]['interest_rate'],
                   df[df['default']==1]['credit_score'],
                   alpha=0.2, color='#FF6B57', s=5, label='Default')
axes[1,2].set_title('Interest Rate vs Credit Score')
axes[1,2].set_xlabel('Interest Rate (%)')
axes[1,2].set_ylabel('Credit Score')
axes[1,2].legend()

plt.tight_layout()
plt.savefig('eda_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print("\nSaved: eda_analysis.png")

# ─────────────────────────────
# 3. FEATURE ENGINEERING
# ─────────────────────────────
df['monthly_payment_est'] = (df['loan_amount'] * (df['interest_rate']/100/12)) / \
                             (1 - (1 + df['interest_rate']/100/12) ** -df['loan_term_months'])
df['payment_to_income'] = df['monthly_payment_est'] / (df['annual_income'] / 12)
df['is_high_risk_purpose'] = (df['purpose'].isin(['medical', 'other'])).astype(int)
df['has_delinquency'] = (df['delinquencies_2yrs'] > 0).astype(int)
df['subprime'] = (df['credit_score'] < 620).astype(int)

# Encode purpose
df = pd.get_dummies(df, columns=['purpose'], drop_first=True)
df.drop(columns=['credit_bucket'], inplace=True)

# ─────────────────────────────
# 4. MODEL TRAINING
# ─────────────────────────────
features = [
    'credit_score', 'annual_income', 'loan_amount', 'loan_term_months',
    'interest_rate', 'dti_ratio', 'employment_length_years', 'delinquencies_2yrs',
    'monthly_payment_est', 'payment_to_income', 'is_high_risk_purpose',
    'has_delinquency', 'subprime'
] + [c for c in df.columns if c.startswith('purpose_')]

X = df[features]
y = df['default']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

models = {
    'Logistic Regression': Pipeline([
        ('scaler', StandardScaler()),
        ('model', LogisticRegression(max_iter=1000, random_state=42))
    ]),
    'Decision Tree': Pipeline([
        ('model', DecisionTreeClassifier(max_depth=6, min_samples_leaf=50, random_state=42))
    ]),
    'Random Forest': Pipeline([
        ('model', RandomForestClassifier(n_estimators=100, max_depth=8,
                                          min_samples_leaf=30, random_state=42, n_jobs=-1))
    ])
}

results = {}
print("\n--- Model Performance ---\n")
for name, pipeline in models.items():
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_prob)
    results[name] = {'pipeline': pipeline, 'y_pred': y_pred, 'y_prob': y_prob, 'auc': auc}
    print(f"{'─'*40}")
    print(f"Model: {name}  |  AUC-ROC: {auc:.4f}")
    print(classification_report(y_test, y_pred, target_names=['Performing', 'Default']))

# ─────────────────────────────
# 5. ROC CURVES
# ─────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Model Evaluation', fontsize=14, fontweight='bold', color='#1A1A2E')

roc_colors = ['#2196F3', '#FF6B57', '#4CAF50']
for (name, res), color in zip(results.items(), roc_colors):
    fpr, tpr, _ = roc_curve(y_test, res['y_prob'])
    axes[0].plot(fpr, tpr, label=f"{name} (AUC={res['auc']:.3f})", color=color, lw=2)

axes[0].plot([0,1],[0,1], 'k--', lw=1)
axes[0].set_xlabel('False Positive Rate')
axes[0].set_ylabel('True Positive Rate')
axes[0].set_title('ROC Curves — All Models')
axes[0].legend()
axes[0].grid(alpha=0.3)

# Feature importance (Random Forest)
rf_model = results['Random Forest']['pipeline'].named_steps['model']
importances = pd.Series(rf_model.feature_importances_, index=features).sort_values(ascending=False).head(10)
axes[1].barh(importances.index[::-1], importances.values[::-1], color='#FF6B57', alpha=0.8)
axes[1].set_title('Top 10 Feature Importances (Random Forest)')
axes[1].set_xlabel('Importance Score')

plt.tight_layout()
plt.savefig('model_evaluation.png', dpi=150, bbox_inches='tight')
plt.close()
print("\nSaved: model_evaluation.png")

# ─────────────────────────────
# 6. RISK SCORECARD OUTPUT
# ─────────────────────────────
print("\n--- Risk Scorecard (sample predictions) ---\n")

best_model = results['Random Forest']['pipeline']

test_sample = pd.DataFrame({
    'credit_score':            [750, 620, 550],
    'annual_income':           [65000, 35000, 22000],
    'loan_amount':             [10000, 15000, 20000],
    'loan_term_months':        [36, 60, 60],
    'interest_rate':           [7.5, 16.0, 25.0],
    'dti_ratio':               [0.12, 0.35, 0.55],
    'employment_length_years': [5, 2, 0],
    'delinquencies_2yrs':      [0, 1, 2],
    'monthly_payment_est':     [309, 364, 535],
    'payment_to_income':       [0.057, 0.125, 0.292],
    'is_high_risk_purpose':    [0, 0, 1],
    'has_delinquency':         [0, 1, 1],
    'subprime':                [0, 0, 1],
    'purpose_credit_card':     [0, 1, 0],
    'purpose_home_improvement':[1, 0, 0],
    'purpose_medical':         [0, 0, 0],
    'purpose_other':           [0, 0, 1],
})

# Align columns
for col in features:
    if col not in test_sample.columns:
        test_sample[col] = 0
test_sample = test_sample[features]

probs = best_model.predict_proba(test_sample)[:, 1]
risk_labels = ['LOW RISK', 'MEDIUM RISK', 'HIGH RISK']

scorecard = pd.DataFrame({
    'Applicant':       ['Applicant A', 'Applicant B', 'Applicant C'],
    'Credit Score':    [750, 620, 550],
    'Loan Amount (£)': [10000, 15000, 20000],
    'Default Prob (%)': (probs * 100).round(1),
    'Decision':        risk_labels
})
print(scorecard.to_string(index=False))

print("\n✅ Analysis complete. Output files: eda_analysis.png, model_evaluation.png")
