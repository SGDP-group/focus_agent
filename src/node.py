from langchain_core.messages import HumanMessage, SystemMessage
from src.tools import break_task_to_steps
from src.llm import llm
from src.state import MainState


tools = [break_task_to_steps]
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

SYSTEM_PROMPT = """You are a helpful AI assistant that helps break down tasks into actionable steps.
When given a high-level task, use the 'break_task_to_steps' tool to decompose it into smaller tasks.
Always respond in a way that helps the user achieve their goals efficiently."""

sys_msg = SystemMessage(content=SYSTEM_PROMPT)

def assistant(state: MainState):
   for m in state.messages:
      m.pretty_print()
   return {"messages": [llm_with_tools.invoke([sys_msg] + state.messages)]}

