from langgraph.graph import START, StateGraph, END
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
import os

from src.state import MainState
from src.node import task_breakdown_assistant, router, helper
from src.node import tools
from src.utils import _set_env

_set_env("LANGSMITH_API_KEY")
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "langchain-academy"

builder = StateGraph(MainState)

builder.add_node("assistant", task_breakdown_assistant)
# builder.add_node("tools", ToolNode(tools))
builder.add_node("router", router)
builder.add_node("helper", helper)

builder.add_edge(START, "router")
builder.add_conditional_edges("router", router, ['assistant', 'helper'])
builder.add_edge("assistant", END)
builder.add_edge("helper", END)
graph = builder.compile()