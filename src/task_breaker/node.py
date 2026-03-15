from langchain_core.messages.ai import AIMessage
from langchain_core.messages import HumanMessage, SystemMessage
from src.task_breaker.tools import break_task_to_steps
from src.llm import llm
from src.task_breaker.state import MainState, Task
from src.logger import logger
import json

tools = [break_task_to_steps]
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

SYSTEM_PROMPT = """You are a helpful AI assistant that helps break down tasks into actionable steps.
When given a high-level task, use the 'break_task_to_steps' tool to decompose it into smaller tasks.
You will receive the task title, description and the total duration in minutes.
Each step should have a estimated time to complete in minutes. Always use the tool for task breakdown and respond with the tool output.
The total estimated time for the main task should be the sum of the estimated times of the subtasks.
After getting the tool result, respond with EXACTLY the raw tool output without any modification, formatting, or explanation."""

sys_msg = SystemMessage(content=SYSTEM_PROMPT)

def dict_to_task(d: dict) -> Task:
    subtasks = [dict_to_task(sub) for sub in d.get('subtasks', [])]
    return Task(description=d['description'], status=d['status'], subtasks=subtasks, estimated_time=d.get('estimated_time', 60))

def assistant(state: MainState) -> dict[str, list[AIMessage]]:
   logger.info(f"Processing task with {len(state.messages)} messages")
   result = llm_with_tools.invoke([sys_msg] + state.messages)
   logger.info("Generated response for task")
   
   # Try to parse the task from the response
   try:
       task_dict = json.loads(result.content)
       parsed_task = dict_to_task(task_dict)
       return {"messages": [result], "tasks": [parsed_task]}
   except (json.JSONDecodeError, TypeError, ValueError):
       pass
   
   return {"messages": [result]}

