from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

model = 'moonshotai/kimi-k2-instruct-0905'

llm = ChatGroq(
    model=model,
    temperature=0.1,
)


research_llm = ChatGroq(
    model=model,
    temperature=0.1,
)