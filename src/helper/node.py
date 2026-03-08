from src.helper.state import HelperState
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import WikipediaLoader
from src.llm import research_llm

def search_web(state: HelperState):
    
    """ Retrieve docs from web search """

    # Search
    tavily_search = TavilySearchResults(max_results=3)

    # Use the user question as search query
    search_query = state.messages[0].content
    
    # Search
    search_docs = tavily_search.invoke(search_query)

     # Format
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]} 

def search_wikipedia(state: HelperState):
    
    """ Retrieve docs from wikipedia """

    # Use the user question as search query
    search_query = state.messages[0].content
    
    # Search
    search_docs = WikipediaLoader(query=search_query, 
                                  load_max_docs=2).load()

     # Format
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]} 

# Generate final answer
answer_instructions = """You are an AI assistant tasked with answering a user's question based on the provided context.

The user's question is: {question}

Use the following context to answer the question:

{context}

Guidelines:
1. Use only the information provided in the context.
2. Do not introduce external information or make assumptions beyond what is explicitly stated in the context.
3. The context contains sources at the beginning of each document.
4. Include these sources in your answer next to any relevant statements. For example, for source #1 use [1].
5. List your sources in order at the bottom of your answer. [1] Source 1, [2] Source 2, etc.
6. If the source is: <Document source="..." page="..."/> then list: [1] source, page ...
7. Provide a clear, concise, and accurate answer."""

def generate_answer(state: HelperState):
    
    """ Node to generate the final answer """

    # Get state
    messages = state.messages
    context = state.context

    # The question is the first message
    question = messages[0].content

    # Answer question
    system_message = answer_instructions.format(question=question, context=context)
    answer = research_llm.invoke([SystemMessage(content=system_message)])
            
    # Append it to state
    return {"messages": [answer]}
