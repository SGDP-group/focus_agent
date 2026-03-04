from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
import os

from src.state import MainState
from src.node import llm_call_router, route_decision, task_break_down_assistant, task_navigator, tools
from src.utils import _set_env

_set_env("LANGSMITH_API_KEY")
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "langchain-academy"

builder = StateGraph(MainState)

# Add nodes
builder.add_node("llm_call_router", llm_call_router)
builder.add_node("task_break_down_assistant", task_break_down_assistant)
builder.add_node("task_navigator", task_navigator)
builder.add_node("tools", ToolNode(tools))

# Router entry point
builder.add_edge(START, "llm_call_router")

# Conditional routing based on decision
builder.add_conditional_edges(
    "llm_call_router",
    route_decision,
    {
        "task_break_down_assistant": "task_break_down_assistant",
        "task_navigator": "task_navigator",
    },
)

# Task breakdown assistant can call tools
builder.add_conditional_edges(
    "task_break_down_assistant",
    tools_condition,
)
builder.add_edge("tools", "task_break_down_assistant")

# Task navigator goes to END
builder.add_edge("task_navigator", END)

graph = builder.compile()