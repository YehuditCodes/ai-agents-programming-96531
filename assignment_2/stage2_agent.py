"""Stage 2 - the same flow as Stage 1, as a linear LangGraph agent.

    PreferenceCollector -> StockSelector -> LLMExplanation -> END

Run:  python stage2_agent.py
"""
from typing import List, Literal, Optional

from langgraph.graph import END, StateGraph
from pydantic import BaseModel

from config import PLOTS_DIR
from utils import (SYSTEM_PROMPT, ask_user_preferences, describe_preferences,
                   describe_stocks, ensure_no_match_sentence,
                   filter_stocks_by_preferences, get_llm, load_stock_profiles)

RiskLevel = Literal["low", "medium", "high"]

stocks_dict = load_stock_profiles()


class AgentState(BaseModel):
    domain: Optional[str] = None
    risk: Optional[RiskLevel] = None
    horizon: Optional[str] = None  # "short", "medium", "long"
    selected_stocks: List[str] = []
    final_answer: Optional[str] = None


def _prefs(state: AgentState) -> dict:
    return {"domain": state.domain, "risk": state.risk, "horizon": state.horizon}


# ------------------------------------------------------------------ nodes
def preference_collector_node(state: AgentState) -> AgentState:
    print("\n--- NODE: PreferenceCollector ---")
    prefs = ask_user_preferences()  # re-prompts on invalid input
    state.domain = prefs["domain"]
    state.risk = prefs["risk"]
    state.horizon = prefs["horizon"]
    return state


def stock_selector_node(state: AgentState) -> AgentState:
    print("\n--- NODE: StockSelector ---")
    selected = filter_stocks_by_preferences(stocks_dict, _prefs(state))
    state.selected_stocks = list(selected)
    print(f"Selected: {', '.join(state.selected_stocks) or '(none)'}")
    return state


def build_llm_prompt(state: AgentState) -> str:
    selected = {t: stocks_dict[t] for t in state.selected_stocks}
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"User preferences:\n{describe_preferences(_prefs(state))}\n\n"
        f"Selected stocks:\n{describe_stocks(selected)}\n\n"
        "Answer format (when there are selected stocks):\n"
        "1. One short intro sentence that acknowledges the user's preferences.\n"
        "2. One bullet per selected stock, in the given order: "
        "'- TICKER: 2-3 sentences'."
    )


def llm_explanation_node(state: AgentState) -> AgentState:
    print("\n--- NODE: LLMExplanation ---")
    response = get_llm().invoke(build_llm_prompt(state))
    state.final_answer = ensure_no_match_sentence(response.content, state.selected_stocks)
    print("\nAGENT (final suggestions):\n")
    print(state.final_answer)
    return state


# ------------------------------------------------------------------ graph
def build_graph(plot_graph: bool = True):
    builder = StateGraph(AgentState)
    builder.add_node("PreferenceCollector", preference_collector_node)
    builder.add_node("StockSelector", stock_selector_node)
    builder.add_node("LLMExplanation", llm_explanation_node)

    builder.set_entry_point("PreferenceCollector")
    builder.add_edge("PreferenceCollector", "StockSelector")
    builder.add_edge("StockSelector", "LLMExplanation")
    builder.add_edge("LLMExplanation", END)

    agent = builder.compile()

    if plot_graph:
        PLOTS_DIR.mkdir(exist_ok=True)
        try:
            png_bytes = agent.get_graph().draw_mermaid_png()  # uses mermaid.ink (internet)
            with open(PLOTS_DIR / "agent_s2.png", "wb") as f:
                f.write(png_bytes)
        except Exception as e:  # no internet should not stop the agent
            print(f"(Could not draw the graph image: {e})")
    return agent


if __name__ == "__main__":
    graph = build_graph()
    state = AgentState()
    # Single linear run: all interaction happens inside the nodes (via input / print)
    graph.invoke(state)
