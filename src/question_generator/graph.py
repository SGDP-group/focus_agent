from langgraph.graph import START, StateGraph
from langgraph.graph import END
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
import os

from src.question_generator.state import MainState
from src.question_generator.node import assistant
from src.question_generator.node import tools
from src.utils import _set_env

_set_env("LANGSMITH_API_KEY")
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "langchain-academy"

builder = StateGraph(MainState)

builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition,
)
builder.add_edge("tools", "assistant")
builder.add_edge("assistant", END)

question_generator_graph = builder.compile()