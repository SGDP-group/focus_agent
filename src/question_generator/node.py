from langchain_core.messages.ai import AIMessage
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from src.question_generator.tools import generate_questions
from src.llm import llm
from src.question_generator.state import MainState, Question, dict_to_question
from src.logger import logger
import json

tools = [generate_questions]
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

SYSTEM_PROMPT = """You are an expert question generator.
Your job is to take a high-level task and generate a list of 5 questions that would help understand the goal, purpose, duration, deadlines and other relevant information.
When given a task, use the 'generate_questions' tool to create the questions.
After getting the tool result, respond with EXACTLY the raw tool output without any modification, formatting, or explanation."""

sys_msg = SystemMessage(content=SYSTEM_PROMPT)

def dict_to_question_obj(d: dict) -> Question:
    return Question(question=d['question'])

def assistant(state: MainState) -> dict:
    logger.info(f"Generating questions for task: {state.task}")
    
    # Build messages list
    messages = [sys_msg]
    
    # If we have existing messages, use them (we're in a loop)
    if state.messages:
        messages.extend(state.messages)
    else:
        # First invocation
        messages.append(HumanMessage(content=f"Task: {state.task}"))
    
    result = llm_with_tools.invoke(messages)
    logger.info("Generated response for questions")
    
    # Check if result contains tool calls (means we need to use the tool)
    if hasattr(result, 'tool_calls') and result.tool_calls:
        # Tool will be called by ToolNode, just return the message
        return {"messages": [result]}
    
    # Check if result.content is a string representation of Question objects
    content = result.content if hasattr(result, 'content') else str(result)
    
    # Try to parse the questions from the response
    questions = []
    
    # First try JSON parsing
    try:
        questions_list = json.loads(content)
        if isinstance(questions_list, list):
            questions = [Question(question=q if isinstance(q, str) else q.get('question', '')) for q in questions_list]
            return {"messages": [result], "questions": questions}
    except json.JSONDecodeError:
        pass
    
    # If JSON parsing failed, try regex to extract Question objects from string representation
    import re
    pattern = r"Question\(question='([^']*)'\)"
    matches = re.findall(pattern, content)
    if matches:
        questions = [Question(question=q) for q in matches]
        return {"messages": [result], "questions": questions}
    
    return {"messages": [result]}
