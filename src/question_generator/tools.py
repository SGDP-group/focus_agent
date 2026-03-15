from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from src.question_generator.state import Question
from src.llm import llm

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

    # 1) Create output parser based on the Task schema
    parser = PydanticOutputParser(pydantic_object=Question)

    # 2) Build the prompt
    prompt = PromptTemplate.from_template(
        """
        You are an expert question generator.
        Your job is to take a high-level task and generate a list of questions that would help understand the goal, purpose, duration, deadlines and other relevant information.
        Provide the output following this schema exactly:

        {format_instructions}

        Task: {task}
        """
    )

    # 3) Combine system/user prompt with format instructions
    formatted_prompt = prompt.format(
        task=task,
        format_instructions=parser.get_format_instructions()
    )

    response = llm.invoke(formatted_prompt)

    # 5) Parse the structured response
    return parser.parse(response.content)
