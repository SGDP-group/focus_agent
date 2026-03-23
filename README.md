# focus_agent
The task handling agent for SGDP project

# Focus Agent - Task Breakdown Tool

A FastAPI-based service that provides task breakdown and helper agent functionality using LangGraph and Groq LLM.

## Features

- **Task Breakdown Agent**: Breaks down high-level tasks into structured, actionable subtasks
- **Helper Agent**: Provides general assistance with streaming support
- **LangGraph Integration**: Uses LangGraph for agent orchestration
- **FastAPI Framework**: RESTful API with automatic documentation
- **Groq LLM**: Powered by Groq's fast inference API

## Prerequisites

- **Python 3.11** or higher
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager

## Setup

### 1. Install uv

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Or via pip:**
```bash
pip install uv
```

### 2. Clone the Repository

```bash
git clone <your-repo-url>
cd focus_agent
```

### 3. Install Dependencies

```bash
uv sync
```

This installs all dependencies defined in `pyproject.toml`.

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env   # or create manually
```

Add the following to `.env`:

```env
# Required — Groq API key for the LLM
GROQ_API_KEY=your_groq_api_key_here

# Optional — LangSmith API key for tracing
LANGSMITH_API_KEY=your_langsmith_api_key_here
```

**Where to get API keys:**

- **Groq**: Sign up at [console.groq.com](https://console.groq.com/) and generate an API key
- **LangSmith** *(optional)*: Sign up at [smith.langchain.com](https://smith.langchain.com/) for tracing

## Running the API

### Development Mode

```bash
uv run python server.py
```

Or using uvicorn directly:

```bash
uv run uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### Production Mode

```bash
uv run uvicorn server:app --host 0.0.0.0 --port 8000
```

## API Specification

### Endpoints

#### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

#### POST `/invoke-task-breakdown`
Invoke the task breakdown agent.

**Request Body:**
```json
{
  "message": "Plan the annual office outing",
  "user_id": "optional_user_id",
  "session_id": "optional_session_id"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Task breakdown details...",
  "tasks": [
    {
      "description": "Set budget and obtain approval from finance",
      "status": "pending",
      "subtasks": []
    }
  ],
  "user_id": "optional_user_id"
}
```

#### POST `/invoke_helper`
Invoke the helper agent.

**Request Body:**
```json
{
  "message": "What is the capital of France?",
  "user_id": "optional_user_id",
  "session_id": "optional_session_id"
}
```

**Response:**
```json
{
  "success": true,
  "message": "The capital of France is Paris.",
  "tasks": [],
  "user_id": "optional_user_id"
}
```

#### POST `/stream_helper`
Stream the helper agent response.

**Request Body:**
```json
{
  "message": "Explain quantum computing",
  "user_id": "optional_user_id",
  "session_id": "optional_session_id"
}
```

**Response:** Server-sent events stream.

## Testing the API

### Using the Interactive Documentation

FastAPI provides automatic interactive API documentation.

1. Start the server as described above
2. Open your browser and go to `http://localhost:8000/docs`
3. You'll see the Swagger UI with all endpoints
4. Click on an endpoint to expand it
5. Click "Try it out" to test the endpoint
6. Fill in the request body and click "Execute"

### Example Test Commands

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Task Breakdown
```bash
curl -X POST "http://localhost:8000/invoke-task-breakdown" \
  -H "Content-Type: application/json" \
  -d '{"message": "Plan a birthday party"}'
```

#### Helper Agent
```bash
curl -X POST "http://localhost:8000/invoke_helper" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is machine learning?"}'
```

## Project Structure

```
focus_agent/
├── server.py           # FastAPI application and endpoints
├── state.py            # Pydantic state models
├── src/
│   ├── llm.py          # Groq LLM configuration
│   ├── logger.py       # Logging setup
│   ├── utils.py        # Utility functions
│   ├── helper/
│   │   ├── graph.py    # Helper agent graph
│   │   ├── node.py     # Helper agent nodes
│   │   ├── state.py    # Helper agent state
│   │   └── tools.py    # Helper agent tools
│   └── task_breaker/
│       ├── graph.py    # Task breakdown graph
│       ├── node.py     # Task breakdown nodes
│       ├── state.py    # Task breakdown state
│       └── tools.py    # Task breakdown tools
├── pyproject.toml      # Project dependencies
├── langgraph.json      # LangGraph configuration
├── README.md           # This file
└── .env                # Environment variables
```

## Configuration

### Changing the LLM Model

Edit `src/llm.py` to use a different Groq-supported model:

```python
model = 'llama-3.1-70b-versatile'
```

### LangSmith Tracing

Tracing is configured in the graph files. To disable, remove the environment variable settings.

## Troubleshooting

| Issue | Solution |
|---|---|
| **Missing API key error** | Ensure `.env` contains `GROQ_API_KEY` |
| **Import errors** | Run `uv sync` to install dependencies |
| **Port already in use** | Change the port in the uvicorn command |
| **Model not available** | Verify the model name in your Groq account |

## Development

### Adding New Endpoints

1. Add the endpoint function to `server.py`
2. Define the request/response models using Pydantic
3. Update this README with the new API specification

### Running Tests

```bash
uv run pytest
```

## License

Add your license information here.