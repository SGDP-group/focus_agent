# Focus Agent - Task Breakdown Tool

A LangGraph agent that breaks down complex tasks into actionable steps using LLM-powered structured output.

## Features

- Breaks down high-level tasks into structured, actionable subtasks with recursive `Task` models
- Uses LangChain with Pydantic for structured output parsing
- Built with LangGraph for agent orchestration
- Powered by Groq LLM (`moonshotai/kimi-k2-instruct-0905` by default)
- Optional LangSmith tracing for debugging and monitoring

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

This installs all dependencies defined in `pyproject.toml`, including `langchain`, `langchain-groq`, `langgraph`, `trustcall`, and others.

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
- **LangSmith** *(optional)*: Sign up at [smith.langchain.com](https://smith.langchain.com/) for tracing and monitoring

> **Note:** If `LANGSMITH_API_KEY` is not set in `.env`, you will be prompted to enter it at runtime.

## Running the Agent

### Option 1: LangGraph Development Server

```bash
uv run langgraph dev
```

This starts a local dev server with a web UI and API powered by the graph defined in `langgraph.json` (`src/graph.py:graph`). You can interact with the agent through the LangGraph Studio interface.

### Option 2: Direct Python Invocation

```bash
uv run python -c "
from src.graph import graph
from langchain_core.messages import HumanMessage

result = graph.invoke({'messages': [HumanMessage(content='organize a birthday party')]})
print(result['messages'][-1].content)
"
```

### Option 3: Import in Your Own Code

```python
from src.graph import graph
from langchain_core.messages import HumanMessage

def break_down_task(task_description: str) -> str:
    result = graph.invoke({'messages': [HumanMessage(content=task_description)]})
    return result['messages'][-1].content

print(break_down_task("plan a vacation"))
```

## Project Structure

```
focus_agent/
├── src/
│   ├── graph.py        # LangGraph graph definition (entry point for langgraph dev)
│   ├── llm.py          # Groq LLM configuration
│   ├── node.py         # Assistant node, system prompt, and tool binding
│   ├── state.py        # Pydantic models: Task (recursive) and MainState
│   ├── tools.py        # break_task_to_steps tool using structured output
│   └── utils.py        # Helper to load env vars with fallback prompt
├── agent.py            # Alternate graph build with in-memory checkpointer
├── state.py            # Alternate PydanticState (with servers field)
├── logger.py           # Basic logging setup
├── langgraph.json      # LangGraph CLI/dev server configuration
├── pyproject.toml      # Project metadata and dependencies
├── .env                # Environment variables (not committed — listed in .gitignore)
└── README.md
```

## Configuration

### Changing the LLM Model

Edit `src/llm.py` to use a different Groq-supported model:

```python
model = 'llama-3.1-70b-versatile'  # or any other Groq model
```

### LangSmith Tracing

Tracing is enabled by default in `src/graph.py`. To disable it, remove or comment out:

```python
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "langchain-academy"
```

## Troubleshooting

| Issue | Solution |
|---|---|
| **Missing API key error** | Ensure `.env` contains `GROQ_API_KEY` |
| **Import errors** | Run `uv sync` to install all dependencies |
| **Model not available** | Verify the model name is valid in your Groq account |
| **Prompted for LANGSMITH_API_KEY** | Either add it to `.env` or press Enter to skip |

## Development

### Adding New Tools

1. Define your tool function in `src/tools.py` using the `@tool` decorator
2. Add it to the `tools` list in `src/node.py`
3. Update the system prompt in `src/node.py` if needed

### Quick Tool Test

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