from src.question_generator.state import MainState
from src.llm import question_generator_llm
from src.question_generator.tools import generate_questions

SYSTEM_PROMPT = """
You are an expert question generator.
Your job is to take a high-level task and generate a list of questions that would help understand the goal, purpose, duration, deadlines and other relevant information.
"""
question_generator = question_generator_llm.bind_tools([generate_questions])

def generate_questions(state: MainState):
    """Generate questions based on the task"""
    response = question_generator.invoke([SYSTEM_PROMPT, state["task"]])
    return {"questions": response}
