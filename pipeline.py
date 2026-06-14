from backtest import run_pipeline as run_backtest
from hypothesis_agent import run_hypothesis_agent
from critic_agent import run_critic_agent


def run_full_pipeline(stock_input: str) -> dict:
    """Run the quant signal validation pipeline end to end and return its outputs."""
    try:
        print('Running backtest...')
        backtest_results = run_backtest(stock_input)

        print('Hypothesis agent thinking...')
        hypothesis = run_hypothesis_agent(stock_input)

        print('Critic agent analysing...')
        critique = run_critic_agent(hypothesis, backtest_results)

        return {
            'ticker': stock_input.strip().upper(),
            'backtest_results': backtest_results,
            'hypothesis': hypothesis,
            'critique': critique,
        }
    except Exception as exc:
        raise RuntimeError(f'Pipeline error: {exc}') from exc


def print_results(results: dict) -> None:
    """Print the pipeline outputs with clear section headers."""
    print('\n=== BACKTEST ===')
    print(results['backtest_results'])

    print('\n=== HYPOTHESIS ===')
    print(results['hypothesis'])

    print('\n=== CRITIC ===')
    print(results['critique'])


if __name__ == '__main__':
    print('Quant Signal Validation Pipeline. Type "quit" at any prompt to exit.')

    while True:
        try:
            ticker = input('\nEnter a stock ticker to validate (or type "quit"): ').strip()
            if ticker.lower() == 'quit':
                print('Exiting pipeline. Goodbye!')
                break

            if not ticker:
                ticker = 'AAPL'

            print('\nRunning full quant signal validation pipeline...\n')
            results = run_full_pipeline(ticker)
            print_results(results)

            while True:
                follow_up = input('\nAsk a follow-up question about this signal? (type "quit" to exit, or press Enter to continue to a new stock): ').strip()
                if follow_up.lower() == 'quit':
                    print('Exiting pipeline. Goodbye!')
                    raise SystemExit(0)

                if not follow_up:
                    break

                print('\nFollow-up analysis...')
                follow_up_prompt = (
                    f"{results['hypothesis']}\n\n"
                    f"FOLLOW-UP QUESTION: {follow_up}\n"
                    'Please answer this question using the current hypothesis and backtest evidence.'
                )
                follow_up_answer = run_critic_agent(follow_up_prompt, results['backtest_results'])
                print('\n=== FOLLOW-UP ===')
                print(follow_up_answer)

            continue_prompt = input('\nAnalyse another stock? (Press Enter to continue, or type "quit" to exit): ').strip()
            if continue_prompt.lower() == 'quit':
                print('Exiting pipeline. Goodbye!')
                break

        except KeyboardInterrupt:
            print('\nExiting pipeline. Goodbye!')
            break
        except Exception as exc:
            print(f'Error: {exc}')
            retry = input('Press Enter to try again or type "quit" to exit: ').strip()
            if retry.lower() == 'quit':
                print('Exiting pipeline. Goodbye!')
                break
