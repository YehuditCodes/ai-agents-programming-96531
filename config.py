"""Shared settings for all stages of the investment assistant."""
from pathlib import Path

BASE_DIR = Path(__file__).parent
STOCKS_MD = BASE_DIR / "stocks_profiles.md"
STOCKS_JSON = BASE_DIR / "stocks_profiles.json"
PLOTS_DIR = BASE_DIR / "agents_plots"

# LLM. gpt-4o-mini is covered by the course's free (data-sharing) token allowance.
MODEL = "gpt-4o-mini"
TEMPERATURE = 0.3

# Valid user answers
DOMAINS = ["tech", "health", "finance", "energy", "consumer_goods"]
RISK_LEVELS = ["low", "medium", "high"]
HORIZONS = {
    "short": "short (0-2 years)",
    "medium": "medium (2-5 years)",
    "long": "long (5+ years)",
}

# How many stocks to show
MIN_COUNT = 3
MAX_COUNT = 5

# Exact sentence required when nothing matches (Scenario 2)
NO_MATCH_SENTENCE = "Sorry, none of the provided stocks matches your criteria"
