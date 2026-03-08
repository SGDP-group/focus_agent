from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

from src.task_breaker.graph import graph
from src.task_breaker.state import MainState, Task
from src.helper.graph import helper_graph
from langchain_core.messages import HumanMessage
from state import PydanticState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Focus Agent API",
    description="API for the LangGraph Focus Agent",
    version="1.0.0"
)


# Request/Response models
class AgentRequest(BaseModel):
    """Request model for agent invocation"""
    message: str = Field(..., description="User message to process")
    user_id: Optional[str] = Field(None, description="Optional user ID for tracking")
    session_id: Optional[str] = Field(None, description="Optional session ID for tracking")

class TaskResponse(BaseModel):
    """Response model for tasks"""
    description: str
    status: str
    subtasks: List["TaskResponse"] = []


TaskResponse.model_rebuild()


class AgentResponse(BaseModel):
    """Response model for agent output"""
    success: bool
    message: str
    tasks: List[TaskResponse] = []
    user_id: Optional[str] = None


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/invoke-task-breakdown", response_model=AgentResponse)
async def invoke_agent(request: AgentRequest):
    """
    Invoke the focus agent with a user message.
    
    Args:
        request: AgentRequest containing the message to process
        
    Returns:
        AgentResponse with the agent's response and tasks
    """
    try:
        # Create initial state with the user message
        initial_state = {
            "messages": [HumanMessage(content=request.message)],
            "tasks": []
        }
        
        logger.info(f"Processing message: {request.message}")
        
        # Invoke the graph
        result = graph.invoke(initial_state)
        
        # Extract tasks from result
        tasks = [_task_to_response(task) for task in result.get("tasks", [])]
        
        # Get the last message from the agent
        messages = result.get("messages", [])
        last_message = messages[-1].content if messages else "No response"
        
        return AgentResponse(
            success=True,
            message=str(last_message),
            tasks=tasks,
            user_id=request.user_id
        )
        
    except Exception as e:
        logger.error(f"Error invoking agent: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/invoke_helper", response_model=AgentResponse)
async def invoke_helper(request: AgentRequest):
    """
    Invoke the helper agent with a user question.
    
    Args:
        request: AgentRequest containing the question to process
        
    Returns:
        AgentResponse with the agent's answer
    """
    try:
        # Create initial state with the user question
        initial_state = {"messages": [HumanMessage(content=request.message)],}
        
        user_id = request.user_id
        session_id = request.session_id
        logger.info(f"Processing question: {request.message}")
        config = {"configurable": {"thread_id": session_id}, "user_id": user_id}
   
        result = helper_graph.invoke(initial_state, config=config)
        
        # Get the last message from the agent
        messages = result.get("messages", [])
        last_message = messages[-1].content if messages else "No response"
        
        return AgentResponse(
            success=True,
            message=str(last_message),
            tasks=[],  # No tasks for helper
            user_id=user_id
        )
        
    except Exception as e:
        logger.error(f"Error invoking helper: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stream_helper")
async def stream_helper(request: AgentRequest):
    """
    Stream the helper agent response with intermediate steps.
    
    Args:
        request: AgentRequest containing the question to process
        
    Returns:
        Streaming response with intermediate states
    """
    try:
        from fastapi.responses import StreamingResponse
        import json
        
        # Create initial state with the user question
        initial_state = {"messages": [HumanMessage(content=request.message)]}
        
        logger.info(f"Streaming question: {request.message}")
        user_id = request.user_id
        session_id = request.session_id
        config = {"configurable": {"thread_id": session_id}, "user_id": user_id}
   
        
        async def event_generator():
            # Stream events from the graph
            for event in helper_graph.stream(initial_state, config):
                # Format event as JSON and send
                yield f"data: {json.dumps(event, default=str)}\n\n"
        
        return StreamingResponse(event_generator(), media_type="text/event-stream")
        
    except Exception as e:
        logger.error(f"Error streaming helper: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


def _task_to_response(task: Task) -> TaskResponse:
    """Convert Task model to TaskResponse"""
    return TaskResponse(
        description=task.description,
        status=task.status,
        subtasks=[_task_to_response(st) for st in task.subtasks]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
