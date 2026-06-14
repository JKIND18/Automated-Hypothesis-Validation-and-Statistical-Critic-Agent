import os

from dotenv import load_dotenv
from openai import AzureOpenAI


def _load_pitfalls_knowledge_base() -> str:
    """Load the local pitfalls.md file as critic guidance."""
    pitfalls_path = os.path.join(os.path.dirname(__file__), 'pitfalls.md')
    try:
        with open(pitfalls_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError as exc:
        raise ValueError('Could not find pitfalls.md in the same directory as critic_agent.py.') from exc


def _load_settings():
    """Load Azure OpenAI settings from the local .env file."""
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    api_key = os.getenv('AZURE_OPENAI_KEY')
    deployment_name = os.getenv('AZURE_DEPLOYMENT_NAME')

    if not endpoint or not api_key or not deployment_name:
        raise ValueError(
            'Missing Azure OpenAI configuration. Make sure .env contains '
            'AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, and AZURE_DEPLOYMENT_NAME.'
        )

    return endpoint, api_key, deployment_name


def run_follow_up_agent(question: str, hypothesis: str, backtest_results: str) -> str:
    """Answer a follow-up question about the hypothesis using the current analysis context."""
    if not isinstance(question, str) or not question.strip():
        raise ValueError('Question must be a non-empty string.')
    if not isinstance(hypothesis, str) or not hypothesis.strip():
        raise ValueError('Hypothesis must be a non-empty string.')
    if not isinstance(backtest_results, str) or not backtest_results.strip():
        raise ValueError('Backtest results must be a non-empty string.')

    endpoint, api_key, deployment_name = _load_settings()

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version='2024-10-21',
    )

    prompt = (
        'You are a helpful quant research assistant. Answer the user\'s specific question about the trading signal '
        'clearly and concisely. Use the hypothesis and backtest results as context but directly answer what is asked.\n\n'
        f'QUESTION:\n{question}\n\n'
        f'HYPOTHESIS:\n{hypothesis}\n\n'
        f'BACKTEST_RESULTS:\n{backtest_results}'
    )

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {
                'role': 'system',
                'content': (
                    'You are a helpful quant research assistant. Answer the user\'s specific question '
                    'about the trading signal clearly and concisely. Use the hypothesis and backtest results '
                    'as context but directly answer what is asked.'
                ),
            },
            {
                'role': 'user',
                'content': prompt,
            },
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content
    return content.strip() if isinstance(content, str) else str(content)


def run_critic_agent(hypothesis: str, backtest_results: str) -> str:
    """Critique a trading hypothesis using backtest evidence and return a verdict."""
    if not isinstance(hypothesis, str) or not hypothesis.strip():
        raise ValueError('Hypothesis must be a non-empty string.')
    if not isinstance(backtest_results, str) or not backtest_results.strip():
        raise ValueError('Backtest results must be a non-empty string.')

    endpoint, api_key, deployment_name = _load_settings()
    pitfalls_knowledge_base = _load_pitfalls_knowledge_base()

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version='2024-10-21',
    )

    prompt = (
        'You are a skeptical quant researcher whose job is to find flaws in a trading signal hypothesis. '
        'Evaluate the following hypothesis together with the backtest results. '
        'Focus on p-value, trade count, Sharpe ratio, and any statistical weaknesses. '
        'Provide a structured critique and end with a final verdict in this exact format:\n'
        'SUMMARY: <brief summary>\n'
        'P_VALUE: <assessment>\n'
        'TRADE_COUNT: <assessment>\n'
        'SHARPE_RATIO: <assessment>\n'
        'WEAKNESSES: <bullet list or concise issues>\n'
        'VERDICT: PASS | WEAK | REJECT\n\n'
        'HYPOTHESIS:\n'
        f'{hypothesis}\n\n'
        'BACKTEST_RESULTS:\n'
        f'{backtest_results}'
    )

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {
                'role': 'system',
                'content': (
                    'You are a skeptical quant researcher whose job is to find flaws in trading ideas. '
                    'Use the following knowledge base as the standards for your evaluation. '
                    'Explicitly reference these standards when assessing the hypothesis and backtest results, '
                    'and explain how they influence your final verdict.\n\n'
                    f'KNOWLEDGE BASE:\n{pitfalls_knowledge_base}'
                ),
            },
            {
                'role': 'user',
                'content': prompt,
            },
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content
    return content.strip() if isinstance(content, str) else str(content)


if __name__ == '__main__':
    sample_hypothesis = 'A 20-day moving average breakout above the 50-day average predicts positive next-day returns for AAPL.'
    sample_backtest = 'Total return: 4.2%, Sharpe ratio: 0.65, p-value: 0.08, trade count: 18.'

    print('\nRunning local critic test...\n')
    print(run_critic_agent(sample_hypothesis, sample_backtest))
