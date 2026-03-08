from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from src.task_breaker.state import Task
from src.llm import llm

@tool
def break_task_to_steps(task: str) -> dict:
    """
    Uses an LLM to break a high-level task into actionable steps
    using LangChain structured output.
    Args:
        task (str): The high-level task to be broken down.
    Returns:
        Task: A Task object containing the breakdown of steps.
    """

    # 1) Create output parser based on the Task schema
    parser = PydanticOutputParser(pydantic_object=Task)

    # 2) Build the prompt
    prompt = PromptTemplate.from_template(
        """
        You are an expert task breakdown assistant.
        Your job is to take a high-level task and break it down into clear,
        actionable steps. Each step should be concise and focused on a single action.
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
    parsed = parser.parse(response.content)
    return parsed.model_dump()
