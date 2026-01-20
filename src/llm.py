from langchain_groq import ChatGroq

model = ' "qwen/qwen3-32b"'

llm = ChatGroq(
    model=model,
    temperature=0.1,
)
