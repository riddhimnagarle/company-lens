import os
import time
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=api_key
)

vector_store = Chroma(
    persist_directory="data/vector_db",
    embedding_function=embeddings
)

retriever = vector_store.as_retriever(search_kwargs={"k": 6})

llm = ChatGroq(
  model="qwen/qwen3.8-27b",
  api_key=groq_key,
  temperature=0.2
)

prompt = ChatPromptTemplate.from_template("""
You are CompanyLens, an AI analyst that answers questions about companies using only the provided context.
Always cite your sources at the end.

Context:
{context}

Question: {question}

Answer:
""")

def format_docs(docs):
    output = []
    for doc in docs:
        source = doc.metadata.get("source_url", "unknown")
        output.append(f"{doc.page_content}\n[Source: {source}]")
    return "\n\n".join(output)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

def ask(question: str) -> str:
    return rag_chain.invoke(question)

if __name__ == "__main__":
    questions = [
        "What is Ghost and what does it do?",
        "What kind of engineers is Ghost hiring?",
        "What is Ghost's business model?"
    ]
    for q in questions:
        print(f"\nQ: {q}")
        print(f"A: {ask(q)}")
        print("-" * 60)
        time.sleep(15)