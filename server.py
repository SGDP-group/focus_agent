from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional

from src.task_breaker.graph import graph
from src.task_breaker.state import MainState, Task
from src.helper.graph import helper_graph
from src.question_generator.graph import question_generator_graph
from src.question_generator.state import Question as QuestionModel
from langchain_core.messages import HumanMessage
from src.logger import logger

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

class TaskBreakdownRequest(BaseModel):
    """Request model for task breakdown with title, description, and duration"""
    title: str = Field(..., description="Title of the task")
    description: str = Field(..., description="Description of the task")
    duration: int = Field(..., description="Estimated duration in minutes")
    maximum_time_per_task: Optional[int] = Field(None, description="Maximum time allowed per subtask in minutes")
    user_id: Optional[str] = Field(None, description="Optional user ID for tracking")
    session_id: Optional[str] = Field(None, description="Optional session ID for tracking")

class TaskResponse(BaseModel):
    """Response model for tasks"""
    description: str
    status: str
    estimated_time: int = 0
    subtasks: List["TaskResponse"] = []


TaskResponse.model_rebuild()


class QuestionResponse(BaseModel):
    """Response model for questions"""
    question: str = Field(..., description="Generated question")


class QuestionGeneratorRequest(BaseModel):
    """Request model for question generator"""
    task: str = Field(..., description="High-level task to generate questions for")
    user_id: Optional[str] = Field(None, description="Optional user ID for tracking")
    session_id: Optional[str] = Field(None, description="Optional session ID for tracking")


class AgentResponse(BaseModel):
    """Response model for agent output"""
    success: bool
    message: str
    tasks: List[TaskResponse] = []
    questions: List[QuestionResponse] = []
    user_id: Optional[str] = None


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/invoke-task-breakdown", response_model=AgentResponse)
async def invoke_task_breakdown_agent(request: TaskBreakdownRequest):
    """
    Invoke the focus agent with a task breakdown request.
    
    Args:
        request: TaskBreakdownRequest containing title, description, duration, and maximum_time_per_task
        
    Returns:
        AgentResponse with the agent's response and tasks
    """
    try:
        # Create message from title, description, and duration
        message = f"Title: {request.title}\nDescription: {request.description}\nDuration: {request.duration} minutes"
        if request.maximum_time_per_task:
            message += f"\nMaximum time per subtask: {request.maximum_time_per_task} minutes"
        
        # Create initial state with the task information
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "tasks": [],
            "duration": request.duration,
            "maximum_time_per_task": request.maximum_time_per_task
        }
        
        logger.info(f"Processing task breakdown: {request.title} - {request.description} ({request.duration} minutes)")
        if request.maximum_time_per_task:
            logger.info(f"Maximum time per subtask: {request.maximum_time_per_task} minutes")
        
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
        logger.error(f"Error invoking task breakdown agent: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/invoke-helper", response_model=AgentResponse)
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


@app.post("/invoke-question-generator", response_model=AgentResponse)
async def invoke_question_generator(request: QuestionGeneratorRequest):
    """
    Invoke the question generator agent with a task.
    
    Args:
        request: QuestionGeneratorRequest containing the task to generate questions for
        
    Returns:
        AgentResponse with the generated questions
    """
    try:
        # Create initial state with the task
        initial_state = {
            "task": request.task,
            "messages": [],
            "questions": []
        }
        
        user_id = request.user_id
        logger.info(f"Processing question generation for task: {request.task}")
        
        result = question_generator_graph.invoke(initial_state)
        
        # Extract questions from result
        questions_list = result.get("questions", [])
        questions = [
            QuestionResponse(question=q.question) 
            for q in questions_list
        ] if questions_list else []
        
        # Get the last message from the agent
        messages = result.get("messages", [])
        last_message = messages[-1].content if messages else f"Generated {len(questions)} questions"
        
        # If questions are empty but message contains Question objects, try to parse them
        if not questions and last_message:
            import re
            # Try to extract Question objects from the message string
            pattern = r"Question\(question='([^']*)'\)"
            matches = re.findall(pattern, last_message)
            if matches:
                questions = [QuestionResponse(question=q) for q in matches]
        
        return AgentResponse(
            success=True,
            message=str(last_message),
            questions=questions,
            user_id=user_id
        )
        
    except Exception as e:
        logger.error(f"Error invoking question generator: {str(e)}", exc_info=True)
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
        estimated_time=task.estimated_time,
        subtasks=[_task_to_response(st) for st in task.subtasks]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8003,
        reload=True
    )
