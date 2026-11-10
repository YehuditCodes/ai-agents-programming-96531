"""Runs the 3 test scenarios of Stage 2 on the real agent (real LLM calls)
and saves the user-agent interaction of each one to tests_2.docx.

The user's answers are fed in automatically and echoed next to each
question, so the record looks exactly like the terminal session.

Run:  python run_tests.py
"""
import builtins
import contextlib
import io
import re

from docx import Document
from docx.shared import Inches, Pt

from config import BASE_DIR, NO_MATCH_SENTENCE, PLOTS_DIR
from stage2_agent import AgentState, build_graph

SCENARIOS = [
    {
        "title": "Scenario 1 - Happy path (enough matches)",
        "inputs": ["tech", "medium", "long"],
        "expected": "Short intro + 3-5 bullets (tech stocks with risk up to medium), "
                    "2-3 sentences each referencing outlook and key risks.",
    },
    {
        "title": "Scenario 2 - No matches (explicit apology message)",
        "inputs": ["energy", "low", "short"],
        "expected": f'Must include the exact sentence "{NO_MATCH_SENTENCE}". No stock bullets.',
    },
    {
        "title": "Scenario 3 - Input validation loops (invalid domain and risk first)",
        "inputs": ["biotech", "health", "moderate", "high", "medium"],
        "expected": "Re-prompts after 'biotech' and after 'moderate', then intro + up to 5 "
                    "health stock bullets explained for a medium horizon.",
    },
]
FLOW = "PreferenceCollector -> StockSelector -> LLMExplanation -> END"
RISK_NOTE = (
    "The provided stock list contains only 2 tech stocks with risk_level=medium "
    "(NVDA, PLTR), while Scenario 1 expects 3-5 stocks. Therefore the selector treats "
    "the user's risk tolerance as a ceiling: a stock fits if its risk level is at or "
    "below the requested one. Stocks with exactly the requested risk level come first, "
    "then lower-risk stocks (up to 5 in total). A user who accepts medium risk also accepts low risk, "
    "so in Scenario 1 MSFT (low risk) completes the list. Stocks with a higher risk "
    "than requested are never selected."
)


def run_scenario(graph, answers):
    """Run the graph once with scripted answers; return (transcript, final_state)."""
    answers = iter(answers)

    def fake_input(prompt=""):
        answer = next(answers)
        print(f"{prompt}{answer}")  # show the answer like a real terminal
        return answer

    buffer = io.StringIO()
    real_input = builtins.input
    builtins.input = fake_input
    try:
        with contextlib.redirect_stdout(buffer):
            final_state = graph.invoke(AgentState())
    finally:
        builtins.input = real_input
    return buffer.getvalue().strip(), final_state


def check(index, transcript, state):
    """Simple automatic checks against the expected behaviour."""
    answer = state["final_answer"] or ""
    bullets = len(re.findall(r"^- [A-Z]+:", answer, flags=re.MULTILINE))
    nodes = re.findall(r"--- NODE: (\w+) ---", transcript)
    results = [f"Flow: {' -> '.join(nodes)} -> END"]
    if index == 1:
        results.append(f"Stock bullets: {bullets} (expected 3-5) - "
                       f"{'PASS' if 3 <= bullets <= 5 else 'FAIL'}")
    elif index == 2:
        ok = NO_MATCH_SENTENCE in answer and bullets == 0
        results.append(f"Apology sentence present, no bullets - {'PASS' if ok else 'FAIL'}")
    else:
        ok = ("Please choose from" in transcript
              and "Please type 'low', 'medium', or 'high'." in transcript
              and 1 <= bullets <= 5)
        results.append(f"Both re-prompts shown, {bullets} bullets - {'PASS' if ok else 'FAIL'}")
    return results


def add_code_block(doc, text):
    paragraph = doc.add_paragraph()
    run = paragraph.add_run(text)
    run.font.name = "Consolas"
    run.font.size = Pt(9)


def main():
    graph = build_graph(plot_graph=True)
    doc = Document()
    doc.add_heading("Tests - Assignment 2 (LangGraph linear agent)", level=0)
    doc.add_paragraph(f"Expected flow in all scenarios: {FLOW}")
    image = PLOTS_DIR / "agent_s2.png"
    if image.exists():
        doc.add_picture(str(image), width=Inches(1.8))
    doc.add_heading("Note on stock selection (risk level)", level=1)
    doc.add_paragraph(RISK_NOTE)

    for i, scenario in enumerate(SCENARIOS, start=1):
        print(f"Running {scenario['title']} ...")
        transcript, state = run_scenario(graph, scenario["inputs"])
        results = check(i, transcript, state)
        print("   " + " | ".join(results))

        doc.add_heading(scenario["title"], level=1)
        doc.add_paragraph(f"User input: {' -> '.join(scenario['inputs'])}")
        doc.add_paragraph(f"Expected: {scenario['expected']}")
        doc.add_heading("User-agent interaction", level=2)
        add_code_block(doc, transcript)
        doc.add_heading("Result", level=2)
        for line in results:
            doc.add_paragraph(line, style="List Bullet")

    out = BASE_DIR / "tests_2.docx"
    doc.save(out)
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
