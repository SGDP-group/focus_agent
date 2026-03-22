from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from src.question_generator.state import Question
from typing import List
from src.llm import llm
import json

@tool
def generate_questions(task: str) -> List[Question]:
    """
    Uses an LLM to generate questions for a high-level task
    using LangChain structured output.
    Args:
        task (str): The high-level task to generate questions for.
    Returns:
        List[Question]: A list of generated questions.
    """

    # Create a simple schema for list of questions
    prompt = PromptTemplate.from_template(
        """
        You are an expert question generator.
        Your job is to take a high-level task and generate a list of 5 questions that would help understand the goal, purpose, duration, deadlines and other relevant information.
        Return the output as a JSON object with a "question" key containing a list of question strings.
        Example format: {{"question": ["question 1", "question 2", ...]}}

        Task: {task}
        """
    )

    formatted_prompt = prompt.format(task=task)
    
    response = llm.invoke(formatted_prompt)
    
    # Parse the JSON response
    try:
        data = json.loads(response.content)
        questions_list = data.get('question', [])
        
        # Convert to List[Question]
        if isinstance(questions_list, list):
            return [Question(question=q) for q in questions_list]
    except json.JSONDecodeError:
        pass
    
    return []


tools = [generate_questions]