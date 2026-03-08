from langgraph.graph import START, StateGraph
from langgraph.graph import END

import os
from src.helper.node import search_web, search_wikipedia, generate_answer
from src.helper.state import HelperState


builder = StateGraph(HelperState)
builder.add_node("search_web", search_web)
builder.add_node("search_wikipedia", search_wikipedia)
builder.add_node("generate_answer", generate_answer)

# Flow
builder.add_edge(START, "search_web")
builder.add_edge(START, "search_wikipedia")
builder.add_edge("search_web", "generate_answer")
builder.add_edge("search_wikipedia", "generate_answer")
builder.add_edge("generate_answer", END)

helper_graph = builder.compile()