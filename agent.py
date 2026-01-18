import os
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.graph import START, StateGraph
from langgraph.checkpoint.memory import MemorySaver


from dotenv import load_dotenv
from src.utils import _set_env
from src.state import PydanticState
from src.node import assistant, tools

load_dotenv()
_set_env("LANGSMITH_API_KEY")
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "langchain-academy"


memory = MemorySaver()

# Build graph
builder = StateGraph(PydanticState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define edges: these determine how the control flow moves
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

graph = builder.compile(checkpointer=memory)






