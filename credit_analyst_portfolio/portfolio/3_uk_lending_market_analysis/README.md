# 🇬🇧 UK Unsecured Lending Market Analysis

> Macro-level analysis of the UK personal loans and credit card market — pricing dynamics, default trends, and fintech disruption.

## Overview

This project analyses the UK unsecured consumer credit market using Bank of England and UK Finance data. It covers market sizing, pricing dynamics, the macro impact on defaults, and how challenger banks like Monzo are reshaping the competitive landscape.

## Key Findings

- The UK unsecured credit market stands at **~£232bn outstanding** (2024 estimate)
- Fintech challengers grew from **~2.5% to ~11%** of new personal loan originations between 2020–2024
- **Unemployment** is a stronger predictor of default rates than interest rate changes alone
- The 2022–2023 rate hiking cycle **compressed risk-adjusted yields** as cost of funds rose faster than lending rates
- FCA's overdraft reforms caused a structural decline in overdraft balances, shifting volume toward personal loans

## Chart Output

`uk_lending_market_analysis.png` — 6-panel dashboard covering:
1. Total credit outstanding by product type (£bn stacked)
2. Personal loan rate vs BoE base rate & lending spread
3. Default rate vs unemployment (macro sensitivity)
4. Market share shift 2020→2024 by lender type
5. Consumer credit annual growth by product
6. Gross rate vs risk-adjusted yield over time

## Data Sources

Data has been structured from publicly available sources:
- [Bank of England Statistics](https://www.bankofengland.co.uk/statistics)
- [UK Finance Consumer Finance data](https://www.ukfinance.org.uk/data-and-research)
- [FCA Consumer Credit data](https://www.fca.org.uk/data)

## How to Run

```bash
pip install pandas numpy matplotlib
python uk_lending_market_analysis.py
```

## Skills Demonstrated

- `Python` — pandas, matplotlib, data analysis
- Market analysis — macro factors, pricing dynamics, competitive landscape
- Credit knowledge — risk-adjusted yield, cost of funds, FCA regulatory context
- UK lending — BoE base rate, consumer credit regulation, product economics
