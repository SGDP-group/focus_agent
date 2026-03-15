from pydantic import BaseModel
from langgraph.graph.message import add_messages
from typing import Literal, Annotated, Dict, List
from langchain_core.messages import AnyMessage
from pydantic import BaseModel, Field


class Task(BaseModel):
    description: str = Field(..., description="Description of the task")
    status: Literal["pending", "in_progress", "completed"] = Field(
        "pending", description="Status of the task"
    )
    subtasks: List["Task"] = Field([], description="List of subtasks")
    estimated_time: int = Field(0, description="Estimated time to complete the task in minutes")

Task.model_rebuild()

class MainState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]
    tasks: List["Task"] = Field([], description="List of subtasks")
