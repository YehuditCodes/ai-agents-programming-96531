"""Stage 1 - non-agentic program: preferences -> rule-based selection -> LLM explanations.

Run:  python stage1.py
"""
from pydantic import BaseModel

from config import NO_MATCH_SENTENCE
from utils import (SYSTEM_PROMPT, ask_user_preferences, describe_preferences,
                   describe_stocks, filter_stocks_by_preferences, get_llm,
                   load_stock_profiles)


class StockExplanation(BaseModel):
    ticker: str
    explanation: str


class Explanations(BaseModel):
    items: list[StockExplanation]


def generate_explanations_with_llm(preferences: dict, selected_stocks: dict) -> dict:
    """Ask the LLM for one short explanation per selected stock.
    Returns {ticker: explanation}."""
    if not selected_stocks:
        return {}  # nothing to explain - no need to call the LLM

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"User preferences:\n{describe_preferences(preferences)}\n\n"
        f"Selected stocks:\n{describe_stocks(selected_stocks)}\n\n"
        "Return one explanation for each selected stock."
    )
    llm = get_llm().with_structured_output(Explanations)
    result = llm.invoke(prompt)

    by_ticker = {item.ticker.upper(): item.explanation for item in result.items}
    # Keep only the stocks Python selected, in the same order
    return {t: by_ticker.get(t, "(no explanation was generated)") for t in selected_stocks}


def main():
    profiles = load_stock_profiles()
    prefs = ask_user_preferences()
    selected = filter_stocks_by_preferences(profiles, prefs)
    explanations = generate_explanations_with_llm(prefs, selected)
    print("\n=== Suggested Stocks ===\n")
    if not explanations:
        print(f"{NO_MATCH_SENTENCE}. Try another domain or a higher risk tolerance.")
    for ticker, explanation in explanations.items():
        print(f"- {ticker}:")
        print(f"  {explanation}\n")


if __name__ == "__main__":
    main()
