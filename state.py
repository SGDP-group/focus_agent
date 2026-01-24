from pydantic import BaseModel
from langgraph.graph.message import add_messages
from typing import Literal, Annotated, Dict, List
from langchain_core.messages import AnyMessage

class PydanticState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]
    servers : List[Dict] | None = None
    