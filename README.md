# Automated Hypothesis Validation and Statistical Critic Agent

> A multi-agent AI pipeline that proposes, backtests, and statistically critiques trading signals — powered by Azure OpenAI and Microsoft Foundry.

---

## Overview

This project is a multi-agent quantitative research pipeline that mimics the workflow of a real quant research desk. You type in a stock ticker, and three AI agents work in sequence to propose a trading signal, validate it mathematically, and then ruthlessly critique it for statistical flaws.

The system is designed to catch what most naive backtests miss — data snooping, small sample bias, regime overfitting, and false statistical significance.

---

## Architecture

```
[User inputs a ticker]
        │
        ▼
1. HYPOTHESIS AGENT  ──► Proposes a testable trading signal hypothesis
        │
        ▼
2. VALIDATION ENGINE ──► Runs a backtest and computes Sharpe ratio, 
                          p-value, trade count, and total return
        │
        ▼
3. CRITIC AGENT      ──► Audits the results against a curated knowledge 
                          base of quantitative research standards and 
                          returns a verdict: PASS | WEAK | REJECT
```

### The Three Agents

**Hypothesis Agent** — given a stock ticker, uses GPT-4.1-mini to propose a simple, testable trading signal hypothesis with a rationale grounded in financial theory.

**Validation Engine** — pure Python/maths (no LLM). Downloads 2 years of daily price data via yfinance, runs a backtest, and computes:
- Total strategy return
- Annualised Sharpe ratio
- p-value (t-test against zero mean returns)
- Trade count

**Critic Agent** — the most sophisticated component. Reads a curated knowledge base (`pitfalls.md`) of quantitative research standards and uses it to ground its critique. Explicitly checks for:
- Statistical significance (p-value threshold)
- Small sample bias (minimum trade count)
- Regime overfitting over short horizons
- Poor risk-adjusted returns (Sharpe ratio)

Returns a structured verdict with cited reasoning.

---

## Microsoft IQ Integration

The Critic Agent implements the **Foundry IQ** grounding principle — its verdicts are not based on LLM intuition alone, but are explicitly grounded in a curated knowledge document (`pitfalls.md`) containing quantitative research standards and statistical thresholds. This reduces hallucination and ensures the agent's critiques are consistent, cited, and auditable — the same principle behind Microsoft Foundry IQ's agentic knowledge retrieval.

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Azure OpenAI GPT-4.1-mini |
| Agent orchestration | Python + Azure AI Projects SDK |
| AI Platform | Microsoft Azure Foundry |
| Web interface | Streamlit |
| Market data | yfinance |
| Charts | Plotly |
| Statistical analysis | NumPy, SciPy, Pandas |

---

## How to Run

**1. Clone the repository**
```bash
git clone https://github.com/JKIND18/Automated-Hypothesis-Validation-and-Statistical-Critic-Agent.git
cd Automated-Hypothesis-Validation-and-Statistical-Critic-Agent
```

**2. Create a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

**3. Install dependencies**
```bash
pip install streamlit plotly yfinance pandas numpy scipy openai python-dotenv azure-ai-projects azure-ai-inference azure-identity
```

**4. Create a `.env` file** in the project folder:
```
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_KEY=your_api_key_here
AZURE_DEPLOYMENT_NAME=gpt-4.1-mini
```

**5. Run the app**
```bash
streamlit run app.py
```

---

## Example Output

Running the pipeline on `AAPL` produces:

- **Hypothesis**: "Buy AAPL when its 5-day moving average crosses above the 20-day moving average"
- **Backtest**: Total return 11.43%, Sharpe 0.40, p-value 0.57, 21 trades
- **Critic verdict**: `REJECT` — p-value well above 0.05 threshold, trade count below minimum 35, short horizon risks regime overfitting

The web interface displays a live price chart with the 20-day SMA overlay, structured agent outputs, and supports follow-up questions about the analysis.

---

## Built For

**Microsoft Agents League Hackathon 2026** — Reasoning Agents track, with Foundry IQ integration.

---

## Important Note

Never commit your `.env` file. It is excluded via `.gitignore`. You will need your own Azure OpenAI deployment to run this project.