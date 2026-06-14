import os

from dotenv import load_dotenv
from openai import AzureOpenAI


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


def run_hypothesis_agent(ticker: str) -> str:
    """Generate one simple, testable trading signal hypothesis for a ticker."""
    symbol = (ticker or '').strip().upper()
    if not symbol:
        raise ValueError('Ticker must be a non-empty stock symbol.')

    endpoint, api_key, deployment_name = _load_settings()

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version='2024-10-21',
    )

    prompt = (
        f"You are helping validate a quant trading idea for {symbol}. "
        "Propose ONE simple, testable trading signal hypothesis for this ticker. "
        "Keep the idea practical and easy to backtest. "
        "Respond in exactly two lines with these labels:\n"
        "HYPOTHESIS: <one concise hypothesis>\n"
        "RATIONALE: <why this could be a useful testable signal>"
    )

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {
                'role': 'system',
                'content': 'You are a quantitative research assistant.'
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
    test_ticker = input('Enter a ticker to test (for example AAPL): ').strip()
    print('\nGenerating hypothesis...\n')
    print(run_hypothesis_agent(test_ticker))
