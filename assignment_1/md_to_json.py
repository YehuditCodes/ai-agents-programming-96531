"""Helper program: converts stocks_profiles.md into stocks_profiles.json.

Input format (per stock):
    ## XOM
    - **Domain:** Energy
    - **Risk level:** medium
    - **Outlook:** ...
    - **Key risks:** risk 1; risk 2; risk 3

Output format:
    {"XOM": {"domain": "energy", "risk_level": "medium",
             "outlook": "...", "key_risks": ["risk 1", "risk 2", "risk 3"]}, ...}

Usage:  python md_to_json.py [input.md] [output.json]
"""
import json
import re
import sys

from config import STOCKS_JSON, STOCKS_MD

FIELD_RE = re.compile(r"^-\s*\*\*(.+?):\*\*\s*(.+)$")
FIELD_NAMES = {
    "domain": "domain",
    "risk level": "risk_level",
    "outlook": "outlook",
    "key risks": "key_risks",
}


def normalize_domain(text: str) -> str:
    """'Consumer Goods' -> 'consumer_goods'."""
    return text.strip().lower().replace(" ", "_")


def parse_markdown(text: str) -> dict:
    profiles = {}
    ticker = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("## "):
            ticker = line[3:].strip().upper()
            profiles[ticker] = {}
            continue
        match = FIELD_RE.match(line)
        if not (ticker and match):
            continue
        key = FIELD_NAMES.get(match.group(1).strip().lower())
        if key is None:
            continue
        value = match.group(2).strip()
        if key == "domain":
            value = normalize_domain(value)
        elif key == "risk_level":
            value = value.lower()
        elif key == "key_risks":
            value = [r.strip() for r in value.split(";") if r.strip()]
        profiles[ticker][key] = value

    # Every stock must have all four fields
    for t, profile in profiles.items():
        missing = set(FIELD_NAMES.values()) - profile.keys()
        if missing:
            raise ValueError(f"{t} is missing fields: {sorted(missing)}")
    return profiles


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else STOCKS_MD
    dst = sys.argv[2] if len(sys.argv) > 2 else STOCKS_JSON
    with open(src, encoding="utf-8") as f:
        profiles = parse_markdown(f.read())
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)
    print(f"Converted {len(profiles)} stocks: {src} -> {dst}")


if __name__ == "__main__":
    main()
