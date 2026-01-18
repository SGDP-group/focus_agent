
from langchain_groq import ChatGroq
from langchain_openai import AzureChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage

from langchain_openai import ChatOpenAI


from src.state import PydanticState
from src.tools import ping, rag_tool, load_servers, scan

import os
from dotenv import load_dotenv

load_dotenv()

assistant_model = os.getenv("ASSISTANT_MODEL")

ip_range = os.getenv("IP_RANGE")


tools = [ping, rag_tool, scan]

# llm = ChatGoogleGenerativeAI(
#     model= "gemini-2.5-flash",
#     temperature=1.0,
#     max_retries=2,
# )


# if "AZURE_OPENAI_API_KEY" not in os.environ:
#     os.environ["AZURE_OPENAI_API_KEY"] = getpass.getpass(
#         "Enter your AzureOpenAI API key: "
#     )
# os.environ["AZURE_OPENAI_ENDPOINT"] = "https://wmschatagent.cognitiveservices.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview"

llm = AzureChatOpenAI(
    azure_deployment="gpt-4o",  # or your deployment
    api_version="2025-01-01-preview",  # or your api version
    temperature=0.6,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

# llm = ChatOpenAI(
#     model="moonshotai/kimi-k2:free", # Specify a model available on OpenRouter
#     api_key=os.environ.get("OPENROUTER_API_KEY"),
#     base_url="https://openrouter.ai/api/v1",
# )

# llm = ChatGroq(
#     model= "openai/gpt-oss-120b",
#     temperature=0.4,
#     max_retries=2,
# )

# llm = ChatGroq(
#     model= "moonshotai/kimi-k2-instruct-0905",
#     temperature=0.4,
#     max_retries=2,
# )


llm_with_tools = llm.bind_tools(tools)

servers = [
    {
        "name": "single board computer 01",
        "ip": "10.101.16.180"
    },
    {
        "name": "single board computer 02",
        "ip": "10.101.16.181"
    },
    {
        "name": "single board computer 03",
        "ip": "10.101.16.182"
    },
    {
        "name": "single board computer 04",
        "ip": "10.101.16.183"
    },
    {
        "name": "single board computer 05",
        "ip": "10.101.16.184"
    },
    {
        "name": "single board computer 06",
        "ip": "10.101.16.185"
    },
    {
        "name": "single board computer 07",
        "ip": "10.101.16.186"
    },
    {
        "name": "single board computer 08",
        "ip": "10.101.16.187"
    },
    {
        "name": "single board computer 09",
        "ip": "10.101.16.188"
    }
]

SYSTEM_PROMPT :str = """
    You are network assistant. Help the user with networking monitoring and troubleshooting. Use the tools provided to you to perform network operations. 
    If you get an notification simply notify the user. 
    Assume that the user is a non-technical person and try to explain the tasks in a simple way. And don't send any ip addresses when refering to servers.
    Exclusively refere to the RAG tool output for the troubleshooting instructions.
    If the user asks about a specific server, use the ping tool to get the current status of the server. 
    If the user asks about a range of servers, use the scan tool to get the current status of the servers. 
    This is the ip range of your network: {ip_range} (You should give this to the scan tool)
    Your interacting with the user via WhatsApp Business API. So don't add any markdown syntaxes to the response.
    """

def assistant(state: PydanticState):
    sys_msg = SystemMessage(content=SYSTEM_PROMPT.format(servers=servers, ip_range=ip_range))
    return {"messages": [llm_with_tools.invoke([sys_msg] + state.messages)]}

