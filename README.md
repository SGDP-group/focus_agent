# Focus Agent - Task Breakdown Tool

A LangGraph agent that breaks down complex tasks into actionable steps using LLM-powered structured output.

## Features

- Breaks down high-level tasks into structured, actionable subtasks
- Uses LangChain with Pydantic for structured output
- Built with LangGraph for agent orchestration
- Clean, raw task object output
- **Voice interface** powered by [Pipecat](https://github.com/pipecat-ai/pipecat) — speak a task, hear the breakdown

## Prerequisites

- Python 3.11 or higher
- uv (Python package manager)

## Installation

### 1. Install uv

If you don't have uv installed, run one of the following commands:

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

### 2. Clone and Setup the Project

```bash
# Clone the repository
git clone <your-repo-url>
cd focus_agent

# Install dependencies using uv
uv sync

# Create a .env file from the example
cp .env.example .env
```

### 3. Environment Configuration

Add your API keys to the `.env` file:

```env
# Required: Groq API Key (for the LLM)
GROQ_API_KEY=your_groq_api_key_here

# Required for Voice Bot: Deepgram API Key (for STT and TTS)
DEEPGRAM_API_KEY=your_deepgram_api_key_here

# Optional: LangSmith API Key (for tracing)
LANGSMITH_API_KEY=your_langsmith_api_key_here
```

**Getting API Keys:**

- **Groq API Key**: Sign up at [https://console.groq.com/](https://console.groq.com/) and get your API key
- **Deepgram API Key**: Sign up at [https://console.deepgram.com/](https://console.deepgram.com/) — free tier available, one key covers both Speech-to-Text and Text-to-Speech
- **LangSmith API Key**: Optional, for tracing and monitoring at [https://smith.langchain.com/](https://smith.langchain.com/)

## Usage

### Method 1: Voice Bot (Recommended)

Start the voice-enabled Focus Agent:

```bash
uv run python voice_bot.py
```

Then open **http://localhost:7860/client** in your browser (Chrome or Edge recommended).

**How to test:**

1. Click the **Connect** button in the browser UI
2. **Allow microphone access** when prompted
3. **Speak a task** — e.g. "organize a birthday party" or "plan a vacation"
4. **Listen** — the agent will break down your task and speak the response back

The voice pipeline: Browser mic → Deepgram STT → LangGraph Focus Agent → Deepgram TTS → Browser speaker

### Method 2: Direct Python Usage

Run the agent directly from Python:

```bash
uv run python -c "
from src.graph import graph
from langchain_core.messages import HumanMessage

# Test the agent
result = graph.invoke({'messages': [HumanMessage(content='organize a birthday party')]})
print(result['messages'][-1].content)
"
```

### Method 3: Development Server (Text Only)

Start the LangGraph development server (requires separate install of `langgraph-api` and `langgraph-cli`):

```bash
pip install langgraph-api==0.7.9 "langgraph-cli[inmem]>=0.4.11"
uv run langgraph dev
```

This will start a local development server where you can interact with the agent through a web interface or API.

> **Note:** `langgraph-api` has a `protobuf` version conflict with `pipecat-ai`. Install it in a separate virtual environment if needed.

### Method 4: Import in Your Code

```python
from src.graph import graph
from langchain_core.messages import HumanMessage

# Use the agent
def break_down_task(task_description):
    result = graph.invoke({'messages': [HumanMessage(content=task_description)]})
    return result['messages'][-1].content

# Example
task_breakdown = break_down_task("plan a vacation")
print(task_breakdown)
```

## Example Output

When you input "organize a birthday party", the agent returns:

```
description='Organize a birthday party' status='pending' subtasks=[Task(description='Set a budget', status='pending', subtasks=[]), Task(description='Choose a date and time', status='pending', subtasks=[]), Task(description='Create a guest list', status='pending', subtasks=[]), Task(description='Select and book a venue', status='pending', subtasks=[]), Task(description='Send invitations', status='pending', subtasks=[]), Task(description='Plan the menu and order food', status='pending', subtasks=[]), Task(description='Order or bake a birthday cake', status='pending', subtasks=[]), Task(description='Arrange decorations', status='pending', subtasks=[]), Task(description='Organize entertainment or activities', status='pending', subtasks=[]), Task(description='Confirm RSVPs one week before', status='pending', subtasks=[]), Task(description='Purchase party favors', status='pending', subtasks=[]), Task(description='Set up the venue on the day', status='pending', subtasks=[]), Task(description='Clean up after the party', status='pending', subtasks=[])]
```

## Project Structure

```
focus_agent/
├── src/
│   ├── graph.py              # LangGraph setup and configuration
│   ├── llm.py               # LLM configuration (Groq)
│   ├── node.py              # Agent nodes and system prompts
│   ├── state.py             # Pydantic models for state management
│   ├── tools.py             # Task breakdown tool
│   ├── utils.py             # Utility functions
│   └── voice_processor.py   # Custom Pipecat processor wrapping the LangGraph agent
├── voice_bot.py             # Voice bot entry point (Pipecat + WebRTC)
├── pyproject.toml           # Project dependencies and metadata
├── .env.example             # Example environment variables
├── README.md               # This file
└── .env                    # Environment variables (create from .env.example)
```

## Configuration

### LLM Model

The agent uses Groq's `moonshotai/kimi-k2-instruct-0905` model by default. You can change this in `src/llm.py`:

```python
model = 'llama-3.1-70b-versatile'  # or any other Groq model
```

### Available Groq Models

- `llama-3.1-70b-versatile`
- `llama-3.1-8b-instant`
- `mixtral-8x7b-32768`
- `gemma-2-9b-it`

## Troubleshooting

### Common Issues

1. **"Field required" error**: Ensure your `.env` file contains the required API keys
2. **Import errors**: Run `uv sync` to ensure all dependencies are installed
3. **Model not available**: Check if the specified model is available in your Groq account
4. **Port 7860 already in use**: Kill the existing process with `lsof -ti:7860 | xargs -r kill` and restart
5. **No audio response from voice bot**: Check the terminal logs for errors — ensure `DEEPGRAM_API_KEY` is set correctly
6. **Microphone not working**: Make sure you're using Chrome or Edge and have allowed microphone permissions

### Debug Mode

Enable debug logging by setting environment variables:

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_PROJECT="focus-agent-debug"
```

## Development

### Adding New Tools

1. Create your tool function in `src/tools.py`
2. Decorate with `@tool`
3. Add to the tools list in `src/node.py`
4. Update the system prompt as needed

### Testing

Run the test suite:

```bash
uv run python -c "from src.tools import break_task_to_steps; print(break_task_to_steps.invoke({'task': 'test task'}))"
```

## License

Add your license information here.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request