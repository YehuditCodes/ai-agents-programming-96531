# Assignment 1 - Stage 1: Investment Assistant (non-agentic)

A simple investment assistant. It asks the user for investment preferences,
selects matching stocks from a predefined list with rule-based logic, and uses
an LLM (OpenAI `gpt-4o-mini`) to write a short educational explanation for each
selected stock.

## Files

| File | Purpose |
|------|---------|
| `config.py` | Settings (model, valid answers, counts, apology sentence) |
| `md_to_json.py` | Helper: converts `stocks_profiles.md` into `stocks_profiles.json` |
| `utils.py` | `load_stock_profiles`, `ask_user_preferences`, `filter_stocks_by_preferences`, LLM helpers |
| `stage1.py` | `generate_explanations_with_llm` and `main()` |
| `stocks_profiles.md` / `.json` | The predefined stock profiles |

## Run

```bash
pip install -r requirements.txt
python md_to_json.py   # only if stocks_profiles.json needs to be rebuilt
python stage1.py
```

The OpenAI key is read from a `.env` file (`OPENAI_API_KEY=...`) in this folder
or in the repository root.

## Note on stock selection

The user's risk tolerance is treated as a ceiling: a stock fits if its risk level is
at or below the requested one (exact matches first, at most 5 stocks).
