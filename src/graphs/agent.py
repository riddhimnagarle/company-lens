import os
import sys
from typing import TypedDict, List
from dotenv import load_dotenv

# Ensure imports work from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rag_chain import retriever, llm, prompt, format_docs

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END

# 1. State: what the graph passes around
class State(TypedDict):
    question: str
    context: str
    answer: str

# 2. Node 1: Retrieve documents
def retrieve(state: State):
    docs = retriever.invoke(state["question"])
    return {"context": format_docs(docs)}

# 3. Node 2: Generate answer using LLM
def generate(state: State):
    chain = prompt | llm | StrOutputParser()
    res = chain.invoke({"context": state["context"], "question": state["question"]})
    return {"answer": res}

# 4. Connect the graph: START -> retrieve -> generate -> END
workflow = StateGraph(State)
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

agent = workflow.compile()

# Helper function to call it easily
def ask_agent(question: str) -> str:
    result = agent.invoke({"question": question, "context": "", "answer": ""})
    return result["answer"]

# Quick test
if __name__ == "__main__":
    print(ask_agent("What is Ghost and what does it do?"))