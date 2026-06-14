import re

import plotly.graph_objects as go
import streamlit as st

from backtest import download_history, resolve_ticker
from critic_agent import run_critic_agent, run_follow_up_agent
from hypothesis_agent import run_hypothesis_agent
from backtest import run_pipeline as run_backtest


st.set_page_config(
    page_title='Quant Signal Validation Agent',
    page_icon='📈',
    layout='wide',
)

st.markdown(
    """
    <style>
        :root {
            color-scheme: dark;
        }
        .stApp {
            background: linear-gradient(135deg, #0b1220 0%, #111827 45%, #172554 100%);
            color: #e5eefb;
        }
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
        }
        div[data-testid="stExpander"] > div:first-child {
            background: #111827;
            border: 1px solid #1f2937;
            border-radius: 10px;
        }
        div[data-testid="stExpander"] > div:last-child {
            background: #0f172a;
            border: 1px solid #1f2937;
            border-radius: 0 0 10px 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def extract_verdict(critique_text: str) -> str:
    """Extract the final verdict from the critic output."""
    match = re.search(r'\bVERDICT\s*:\s*([A-Z]+)', critique_text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return 'WEAK'


st.title('Quant Signal Validation Agent')
st.caption('Run a multi-agent quant signal validation flow for a ticker and review the results.')

if 'results' not in st.session_state:
    st.session_state.results = None
if 'backtest_results' not in st.session_state:
    st.session_state.backtest_results = ''
if 'hypothesis' not in st.session_state:
    st.session_state.hypothesis = ''
if 'critique' not in st.session_state:
    st.session_state.critique = ''
if 'verdict' not in st.session_state:
    st.session_state.verdict = 'WEAK'
if 'resolved_ticker' not in st.session_state:
    st.session_state.resolved_ticker = ''
if 'follow_up_answers' not in st.session_state:
    st.session_state.follow_up_answers = []
if 'follow_up_counter' not in st.session_state:
    st.session_state.follow_up_counter = 0

with st.sidebar:
    st.header('Inputs')
    ticker = st.text_input('Stock ticker', value='AAPL', placeholder='e.g. AAPL or Microsoft')
    run_button = st.button('Run Analysis', use_container_width=True)

if run_button:
    st.session_state.results = None
    st.session_state.backtest_results = ''
    st.session_state.hypothesis = ''
    st.session_state.critique = ''
    st.session_state.verdict = 'WEAK'
    st.session_state.resolved_ticker = ''
    st.session_state.follow_up_answers = []

    if not ticker.strip():
        st.warning('Please enter a stock ticker or company name.')
        st.session_state.results = None
    else:
        try:
            resolved_ticker = resolve_ticker(ticker)

            with st.status('Running backtest...', expanded=True):
                backtest_results = run_backtest(ticker)

            with st.status('Hypothesis agent thinking...', expanded=True):
                hypothesis = run_hypothesis_agent(resolved_ticker)

            with st.status('Critic agent analysing...', expanded=True):
                critique = run_critic_agent(hypothesis, backtest_results)

            st.session_state.results = {
                'ticker': resolved_ticker,
                'backtest_results': backtest_results,
                'hypothesis': hypothesis,
                'critique': critique,
            }
            st.session_state.backtest_results = backtest_results
            st.session_state.hypothesis = hypothesis
            st.session_state.critique = critique
            st.session_state.verdict = extract_verdict(critique)
            st.session_state.resolved_ticker = resolved_ticker
            st.session_state.follow_up_answers = []
        except Exception as exc:
            st.error(f'Analysis failed: {exc}')
            st.session_state.results = None
            st.stop()

if st.session_state.get('results'):
    results = st.session_state.results
    verdict = st.session_state.verdict
    resolved_ticker = st.session_state.resolved_ticker or results.get('ticker', 'UNKNOWN')

    verdict_colors = {
        'PASS': '#22c55e',
        'WEAK': '#f59e0b',
        'REJECT': '#ef4444',
    }
    verdict_color = verdict_colors.get(verdict, '#f59e0b')

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(15,23,42,0.98), rgba(17,24,39,0.98));
            border: 1px solid {verdict_color};
            border-radius: 14px;
            padding: 16px 18px;
            margin-bottom: 18px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.35);
        ">
            <div style="font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.18em; color: #cbd5e1;">Final Verdict</div>
            <div style="font-size: 2.2rem; font-weight: 800; color: {verdict_color}; margin-top: 6px;">{verdict}</div>
            <div style="font-size: 0.98rem; color: #e5eefb; margin-top: 6px;">Ticker: {resolved_ticker}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        price_data = download_history(resolved_ticker).copy()
        price_data['sma_20'] = price_data['close'].rolling(window=20).mean()
        price_data = price_data.dropna()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=price_data.index, y=price_data['close'], mode='lines', name='Close Price', line=dict(color='#38bdf8')))
        fig.add_trace(go.Scatter(x=price_data.index, y=price_data['sma_20'], mode='lines', name='20-Day SMA', line=dict(color='#f59e0b', width=2)))
        fig.update_layout(
            title=f"{resolved_ticker} - Price vs 20-Day Moving Average",
            template='plotly_dark',
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as chart_exc:
        st.caption(f'Chart unavailable: {chart_exc}')

    with st.expander('Backtest Results', expanded=True):
        st.write(results.get('backtest_results', ''))

    with st.expander('Hypothesis', expanded=True):
        st.write(results.get('hypothesis', ''))

    with st.expander('Critic Analysis', expanded=True):
        st.write(results.get('critique', ''))

    follow_up_question = st.text_input(
        'Follow-up question',
        placeholder='e.g. What would make this signal pass?',
        key=f'follow_up_{st.session_state.follow_up_counter}',
    )
    follow_up_button = st.button('Ask Follow-Up', use_container_width=True)

    if follow_up_button and follow_up_question.strip():
        with st.spinner('Analyzing follow-up...'):
            follow_up_answer = run_follow_up_agent(
                follow_up_question,
                st.session_state.hypothesis,
                st.session_state.backtest_results,
            )

        st.session_state.follow_up_answers.append({
            'question': follow_up_question.strip(),
            'answer': follow_up_answer,
        })
        st.session_state.follow_up_counter += 1

    if st.session_state.follow_up_answers:
        with st.expander('Follow-Up Analysis', expanded=True):
            for index, item in enumerate(st.session_state.follow_up_answers, start=1):
                st.markdown(f'**Q{index}:** {item["question"]}')
                st.write(item['answer'])
                if index < len(st.session_state.follow_up_answers):
                    st.markdown('---')
else:
    st.info('Enter a ticker and click “Run Analysis” to start the validation flow.')
