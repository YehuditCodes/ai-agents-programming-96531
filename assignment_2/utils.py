"""Functions shared by all stages: loading data, asking the user,
rule-based stock selection, and the LLM call.

Design rule (controlled generation): Python DECIDES which stocks fit;
the LLM only EXPLAINS that decision, using the profile text it is given.
"""
import json
import os

from dotenv import load_dotenv

from config import (DOMAINS, HORIZONS, MAX_COUNT, MIN_COUNT, MODEL,
                    NO_MATCH_SENTENCE, RISK_LEVELS, STOCKS_JSON, TEMPERATURE)

RISK_ORDER = {level: i for i, level in enumerate(RISK_LEVELS)}  # low=0 ... high=2


# ---------------------------------------------------------------- 1. load
def load_stock_profiles(path=STOCKS_JSON) -> dict:
    """Load the stock profiles JSON (created by md_to_json.py) into a dict."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- 2. ask
def _ask(question: str, normalize, error_message: str):
    """Ask until normalize(answer) returns a valid value (not None)."""
    while True:
        answer = input(question).strip().lower()
        value = normalize(answer)
        if value is not None:
            return value
        print(error_message)


def _normalize_domain(answer: str):
    answer = answer.replace(" ", "_").replace("-", "_")
    return answer if answer in DOMAINS else None


def _normalize_risk(answer: str):
    return answer if answer in RISK_LEVELS else None


def _normalize_horizon(answer: str):
    # accepts "long", "long (5+ years)", "1"/"2"/"3"
    options = list(HORIZONS)
    if answer in {"1", "2", "3"}:
        return options[int(answer) - 1]
    first_word = answer.split(" ")[0] if answer else ""
    return first_word if first_word in HORIZONS else None


def ask_user_preferences() -> dict:
    """Ask for domain, risk tolerance and horizon. Re-asks on invalid input."""
    print("Hi! I'll suggest a few stocks that fit your preferences.\n")
    domain = _ask(
        f"Preferred investment domain ({', '.join(DOMAINS)}): ",
        _normalize_domain,
        f"Unknown domain. Please choose from {', '.join(DOMAINS)}.",
    )
    risk = _ask(
        "Risk tolerance (low / medium / high): ",
        _normalize_risk,
        "Please type 'low', 'medium', or 'high'.",
    )
    horizon = _ask(
        "Investment horizon (short = 0-2 years, medium = 2-5 years, long = 5+ years): ",
        _normalize_horizon,
        "Please type 'short', 'medium', or 'long'.",
    )
    return {"domain": domain, "risk": risk, "horizon": horizon}


# ---------------------------------------------------------------- 3. filter
def filter_stocks_by_preferences(
    profiles: dict,
    prefs: dict,
    min_count: int = MIN_COUNT,
    max_count: int = MAX_COUNT,
) -> dict:
    """Rule-based selection.

    Rules:
      1. Same domain as the user asked for.
      2. Risk tolerance is a ceiling: a stock fits if its risk level is
         at or below the user's tolerance (a 'medium' investor can hold
         low-risk stocks, but a 'low' investor never gets medium/high).
      3. Exact risk matches come first, then the next lower level.
      4. At most max_count stocks. If fewer than min_count fit, return
         only those - never pad with stocks that break rules 1-2.
    """
    user_risk = RISK_ORDER[prefs["risk"]]
    candidates = [
        (ticker, p) for ticker, p in profiles.items()
        if p["domain"] == prefs["domain"] and RISK_ORDER[p["risk_level"]] <= user_risk
    ]
    # closest to the user's tolerance first; keep file order inside a level
    candidates.sort(key=lambda item: user_risk - RISK_ORDER[item[1]["risk_level"]])
    selected = dict(candidates[:max_count])

    if 0 < len(selected) < min_count:
        print(f"(Note: only {len(selected)} stock(s) fit these preferences.)")
    return selected


# ---------------------------------------------------------------- 4. LLM
SYSTEM_PROMPT = f"""You are an educational investment assistant.
The stocks were ALREADY selected by a rule-based program. Your job is only to
EXPLAIN why each selected stock fits the user's preferences.

Rules:
- Use only the profile information you are given (domain, risk level, outlook,
  key risks). Do not add facts, prices, numbers or news.
- Do not add, remove or rank stocks, and do not tell the user to buy or sell.
- Mention the stock's outlook AND at least one key risk, and relate them to
  the user's risk tolerance and investment horizon.
- If a stock's risk level is lower than the user's tolerance, say so briefly.
- Plain, friendly English. 2-3 sentences per stock.
- If the list of selected stocks is empty, reply with exactly this sentence:
  "{NO_MATCH_SENTENCE}" and then one short suggestion such as trying another
  domain or a higher risk tolerance. Nothing else."""


def get_llm():
    """ChatOpenAI client. The key comes from .env (the course key),
    which overrides any key already set in the system environment."""
    from langchain_openai import ChatOpenAI

    load_dotenv(override=True)
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not found. Put it in a .env file next to the code.")
    return ChatOpenAI(model=MODEL, temperature=TEMPERATURE)


def describe_preferences(prefs: dict) -> str:
    return (f"- Domain: {prefs['domain']}\n"
            f"- Risk tolerance: {prefs['risk']}\n"
            f"- Investment horizon: {HORIZONS[prefs['horizon']]}")


def describe_stocks(selected: dict) -> str:
    if not selected:
        return "(none - no stock matches the user's criteria)"
    lines = []
    for ticker, p in selected.items():
        lines.append(f"{ticker}: domain={p['domain']}, risk_level={p['risk_level']}\n"
                     f"  outlook: {p['outlook']}\n"
                     f"  key risks: {'; '.join(p['key_risks'])}")
    return "\n".join(lines)


def ensure_no_match_sentence(answer: str, selected: dict) -> str:
    """Python guard: the apology sentence must appear exactly when nothing matched,
    even if the model paraphrased it."""
    if not selected and NO_MATCH_SENTENCE not in answer:
        return f"{NO_MATCH_SENTENCE}.\n{answer}"
    return answer
