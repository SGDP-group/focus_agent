from langgraph.graph import START, StateGraph
from langgraph.graph import END

import os
from src.helper.node import decide_search, search_web, search_wikipedia, generate_answer
from src.helper.state import HelperState


builder = StateGraph(HelperState)
builder.add_node("decide_search", decide_search)
builder.add_node("search_web", search_web)
builder.add_node("search_wikipedia", search_wikipedia)
builder.add_node("generate_answer", generate_answer)

# Flow
builder.add_edge(START, "decide_search")
builder.add_edge("decide_search", "search_web")
builder.add_conditional_edges(
    "decide_search",
    lambda state: "search_wikipedia" if state.needs_wikipedia else "generate_answer",
    {"search_wikipedia": "search_wikipedia", "generate_answer": "generate_answer"}
)
builder.add_edge("search_web", "generate_answer")
builder.add_edge("search_wikipedia", "generate_answer")
builder.add_edge("generate_answer", END)

helper_graph = builder.compile()