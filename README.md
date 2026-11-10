# AI Agents Programming (96531.1.1) - Investment Assistant

Course assignment, Semester A. An investment assistant that asks the user for
investment preferences, selects matching stocks from a predefined list, and uses
an LLM (OpenAI `gpt-4o-mini`) to write short educational explanations for each stock.

- **Stage 1** - simple, non-agentic program (`stage1.py`).
- **Stage 2** - the same flow as a linear LangGraph agent (`stage2_agent.py`):
  `PreferenceCollector -> StockSelector -> LLMExplanation -> END`

## Files

| File | Purpose |
|------|---------|
| `config.py` | Shared settings (model, valid answers, counts, apology sentence) |
| `md_to_json.py` | Helper: converts `stocks_profiles.md` into `stocks_profiles.json` |
| `utils.py` | Shared functions: load profiles, ask preferences, filter stocks, LLM explanations |
| `stage1.py` | Stage 1 program |
| `stage2_agent.py` | Stage 2 LangGraph agent (state, 3 nodes, graph) |
| `run_tests.py` | Runs the 3 test scenarios and writes `tests_2.docx` |
| `tests_2.docx` | Test results: user-agent interaction for each scenario |
| `agents_plots/agent_s2.png` | Diagram of the Stage 2 graph |

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file next to the code (not included in the repository):

```
OPENAI_API_KEY=your-key-here
```

## Run

```bash
python md_to_json.py      # only if stocks_profiles.json needs to be rebuilt
python stage1.py          # Stage 1
python stage2_agent.py    # Stage 2 agent
python run_tests.py       # run the 3 scenarios and create tests_2.docx
```

## Note on stock selection

The user's risk tolerance is treated as a ceiling: a stock fits if its risk level is
at or below the requested one (exact matches first, at most 5 stocks). See the note
at the top of `tests_2.docx` for the reason.
