from pydantic import BaseModel
from langgraph.graph.message import add_messages
from typing import Literal, Annotated, Dict, List, Optional
from langchain_core.messages import AnyMessage
from pydantic import BaseModel, Field


class Task(BaseModel):
    description: str = Field(..., description="Description of the task")
    status: Literal["pending", "in_progress", "completed"] = Field(
        "pending", description="Status of the task"
    )
    subtasks: List["Task"] = Field([], description="List of subtasks")

Task.model_rebuild()

class Route(BaseModel):
    step: Literal["task_break_down", "task_navigator"] = Field(
        None, description="The next step in the routing process: 'task_break_down' to break a task into steps, or 'task_navigator' to navigate through existing tasks."
    )

class MainState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]
    tasks: List["Task"] = Field([], description="List of subtasks")
    decision: Optional[str] = Field(None, description="Routing decision: task_break_down or task_navigator")
