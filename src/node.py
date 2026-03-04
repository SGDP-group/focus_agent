from langchain_core.messages.ai import AIMessage


from langchain_core.messages import HumanMessage, SystemMessage
from src.tools import break_task_to_steps
from src.llm import llm
from src.state import MainState, Route

tools = [break_task_to_steps]
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

TASK_BREAK_DOWN_ASSISTANT_SYSTEM_PROMPT = """You are a helpful AI assistant that helps break down tasks into actionable steps.
When given a high-level task, use the 'break_task_to_steps' tool to decompose it into smaller tasks.
After getting the tool result, respond with EXACTLY the raw tool output without any modification, formatting, or explanation."""

task_break_down_assistant_sys_msg = SystemMessage(content=TASK_BREAK_DOWN_ASSISTANT_SYSTEM_PROMPT)

def task_break_down_assistant(state: MainState) -> dict[str, list[AIMessage]]:
   for m in state.messages:
      m.pretty_print()
   return {"messages": [llm_with_tools.invoke([task_break_down_assistant_sys_msg] + state.messages)]}

router = llm.with_structured_output(Route, method="json_mode")

def llm_call_router(state: MainState):
   """Route the input to the appropriate node"""
   decision = router.invoke(
      [
         SystemMessage(
            content="Route the input to task_break_down or task_navigator based on the user's request."
         ),
         HumanMessage(content=state.messages[-1].content),
      ]
   )
   return {"decision": decision.step}


def route_decision(state: MainState):
   """Conditional edge function to route to the appropriate node"""
   if state.decision == "task_break_down":
      return "task_break_down_assistant"
   elif state.decision == "task_navigator":
      return "task_navigator"

TASK_NAVIGATOR_SYSTEM_PROMPT = """You are a helpful AI assistant that helps to navigate through the tasks."""

task_navigator_sys_msg = SystemMessage(content=TASK_NAVIGATOR_SYSTEM_PROMPT)

def task_navigator(state: MainState) -> dict[str, list[AIMessage]]:
   for m in state.messages:
      m.pretty_print()
   return {"messages": [llm.invoke([task_navigator_sys_msg] + state.messages)]}
