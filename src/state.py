from pydantic import BaseModel
import operator
from langgraph.graph.message import add_messages
from typing import Literal, Annotated, Dict, List, TYPE_CHECKING
from langchain_core.messages import AnyMessage
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

class Node(TypedDict):
    """A single routing decision: which node to call with what query."""
    source: Literal["task_breakdown", "helper", ]
    query: str

class Task(BaseModel):
    description: str = Field(..., description="Description of the task")
    status: Literal["pending", "in_progress", "completed"] = Field(
        "pending", description="Status of the task"
    )
    subtasks: List["Task"] = Field([], description="List of subtasks")

Task.model_rebuild()

class MainState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]
    tasks: List["Task"] = Field([], description="List of subtasks")
    node_results: Annotated[list["Node"], operator.add]
