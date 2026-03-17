from pydantic import BaseModel
from typing import List
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from typing import Annotated
from langchain_core.messages import AnyMessage


class Question(BaseModel):
    question: str = Field(..., description="The generated question")

Question.model_rebuild()

def dict_to_question(d: dict) -> List["Question"]:
    """Convert a dict into a list of Question models.

    Handles both single question strings and lists of questions.
    """
    questions = []
    if isinstance(d.get("question"), list):
        # Multiple questions in a list
        questions = [Question(question=q) for q in d["question"]]
    elif isinstance(d.get("question"), str):
        # Single question string
        questions = [Question(question=d["question"])]
    return questions


class MainState(BaseModel):
    task: str = Field(..., description="The task to generate questions for")
    messages: Annotated[list[AnyMessage], add_messages]
    questions: List["Question"] = Field([], description="List of generated questions")
