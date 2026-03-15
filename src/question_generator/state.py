from pydantic import BaseModel
from langgraph.graph.message import add_messages
from typing import Literal, Annotated, Dict, List, Optional
from langchain_core.messages import AnyMessage
from pydantic import BaseModel, Field


class Question(BaseModel):
    question: str = Field(..., description="The generated question")

class MainState(BaseModel):
    task: str = Field(..., description="The task to generate questions for")    
    questions: List["Question"] = Field([], description="List of generated questions")
