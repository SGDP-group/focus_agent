from langchain_core.messages.ai import AIMessage
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field
from typing import Literal
from src.tools import break_task_to_steps
from src.llm import llm
from src.state import MainState, Node
from langgraph.types import Send

tools = [break_task_to_steps]
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

SYSTEM_PROMPT = """You are a helpful AI assistant that helps break down tasks into actionable steps.
When given a high-level task, use the 'break_task_to_steps' tool to decompose it into smaller tasks.
After getting the tool result, respond with EXACTLY the raw tool output without any modification, formatting, or explanation."""

sys_msg = SystemMessage(content=SYSTEM_PROMPT)

def task_breakdown_assistant(state: MainState) -> dict[str, list[AIMessage]]:
   return {"messages": [llm_with_tools.invoke([sys_msg] + state.messages)]}


class NodeResult(BaseModel):
    """Result of classifying a user query into agent-specific sub-questions."""
    nodes: list[Node] = Field(
        description="List of Nodes to route to depending on the user query.",
    )

structured_llm = llm.with_structured_output(NodeResult)  

ROUTER_SYSTEM_PROMPT = """You are a router that decides which node to call based on the user's query. You have the following nodes available:
- task_breakdown: A node that breaks down a high-level task into smaller, actionable steps
- helper: A node that provides assistance with specific questions or issues related to the task

When given a user query, determine which node(s) should be called to best assist the user. For each node, provide a query that should be sent to that node. 
The output should be a JSON object with a list of nodes and their corresponding queries.
Only include nodes that are relevant to the user's query. If the user's query is about breaking down a task, route to the 'task_breakdown' node. 
If the user's query is about getting help with a specific question, route to the 'helper' node. If the user's query is about both, route to both nodes with appropriate queries. Always provide a query for each node you route to, even if it's just the original user query. Do not include any nodes that are not relevant to the user's query.

Here are some examples of user queries and the corresponding routing decisions:
User query: "I have a project to complete, but I'm not sure where to start. Can you help me break it down?
Routing decision: {"nodes": [{"source": "task_breakdown", "query": "I have a project to complete, but I'm not sure where to start. Can you help me break it down?"}]}
User query: "I'm having trouble understanding a specific part of my project. Can you help me with that?"
Routing decision: {"nodes": [{"source": "helper", "query": "I'm having trouble understanding a specific part of my project. Can you help me with that?"}]}
User query: "I have a project to complete, but I'm not sure where to start. Also, I'm having trouble understanding a specific part of my project. Can you help me with both?"
Routing decision: {"nodes": [{"source": "task_breakdown", "query": "I have a project to complete, but I'm not sure where to start. Can you help me break it down?"}, {"source": "helper", "query": "I'm having trouble understanding a specific part of my project. Can you help me with that?"}]}
"""

def router(state: MainState) -> list[Send]:
    result = structured_llm.invoke(state.messages)
    return [Send(node["source"], {"messages": state.messages}) for node in result.nodes]


HELPER_SYSTEM_PROMPT = """You are a helpful assistant that provides assistance with specific questions or issues related to a task. When given a user query, provide helpful information, guidance, or resources to assist the user with their question or issue.
 Your response should be relevant to the user's query and should aim to help them better understand or resolve their question or issue. Always provide a clear and concise response that directly addresses the user's query."""

def helper(state: MainState) -> dict[str, list[AIMessage]]:
    sys_msg = SystemMessage(content=HELPER_SYSTEM_PROMPT)
    return {"messages": [llm.invoke([sys_msg] + state.messages)]}