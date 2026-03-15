from langgraph.graph import START, StateGraph
from langgraph.graph import END
from src.question_generator.state import MainState
from src.question_generator.node import generate_questions

builder = StateGraph(MainState)
builder.add_node("generate_questions", generate_questions)

# Flow
builder.add_edge(START, "generate_questions")
builder.add_edge("generate_questions", END)



question_generator_graph = builder.compile()