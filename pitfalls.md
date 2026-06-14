# Quantitative Research Pitfalls & Statistical Standards

## 1. Statistical Significance and P-Values
In quantitative finance, any trading signal must prove that its returns are not the result of random chance. A p-value greater than 0.05 indicates that the null hypothesis (that the strategy returns are equal to zero or purely random noise) cannot be rejected. Researchers must flag high p-values as an immediate failure of the trading signal's validity.

## 2. Sample Size and Trade Count
A backtest must have a sufficient sample size to be considered reliable. Any strategy that generates fewer than 35 distinct trades over a 24-month horizon suffers from small sample bias. A low trade count means a few lucky or unlucky days completely skew the data, making the calculated Sharpe ratio statistically irrelevant.

## 3. Regime Overfitting
Strategies backtested purely over a short horizon (such as 2 years) often overfit to a specific market environment. If an asset is in a heavy growth or highly cyclical regime, simple trend-following indicators like Moving Averages will trigger whipsaws (buying at the top, selling at the bottom), leading to negative returns and high drawdown.