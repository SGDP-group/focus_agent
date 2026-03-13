import operator
from pydantic import BaseModel, Field
from typing import Annotated, List
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class Analyst(BaseModel):
    affiliation: str = Field(
        description="Primary affiliation of the analyst.",
    )
    name: str = Field(
        description="Name of the analyst."
    )
    role: str = Field(
        description="Role of the analyst in the context of the topic.",
    )
    description: str = Field(
        description="Description of the analyst focus, concerns, and motives.",
    )
    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nAffiliation: {self.affiliation}\nDescription: {self.description}\n"

class Perspectives(BaseModel):
    analysts: List[Analyst] = Field(
        description="Comprehensive list of analysts with their roles and affiliations.",
    )

class GenerateAnalystsState(TypedDict):
    topic: str # Research topic
    max_analysts: int # Number of analysts
    human_analyst_feedback: str # Human feedback
    analysts: List[Analyst] # Analyst asking questions

class HelperState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]
    context: Annotated[list, operator.add] = Field(default_factory=list)  # Source docs
    needs_wikipedia: bool = Field(default=False)  # Whether to search Wikipedia

class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Search query for retrieval.")
