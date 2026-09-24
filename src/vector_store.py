import os
import glob
import time
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# 1. Load Gemini API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env! Please check your .env file.")

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=api_key
)

CHROMA_PERSIST_DIR = "data/vector_db"

def load_documents_from_folder(folder_path: str = "data/raw_scraped") -> list[Document]:
    """
    Reads text files, extracts metadata header, and trims oversized files
    (like 5-year changelogs) to recent history to respect free-tier quotas.
    """
    documents = []
    txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
    
    if not txt_files:
        print(f"[NOTICE] No files in '{folder_path}'. Using fallback: 'data/fallback'")
        folder_path = "data/fallback"
        txt_files = glob.glob(os.path.join(folder_path, "*.txt"))

    print(f"[LOADER] Found {len(txt_files)} text files in '{folder_path}'.")

    for file_path in txt_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.splitlines()
        metadata = {
            "source_url": "unknown",
            "page_type": "general",
            "scrape_date": "unknown",
            "title": os.path.basename(file_path)
        }
        
        body_start_index = 0
        for i, line in enumerate(lines[:10]):
            if line.startswith("SOURCE_URL:"):
                metadata["source_url"] = line.replace("SOURCE_URL:", "").strip()
            elif line.startswith("PAGE_TYPE:"):
                metadata["page_type"] = line.replace("PAGE_TYPE:", "").strip()
            elif line.startswith("SCRAPE_DATE:"):
                metadata["scrape_date"] = line.replace("SCRAPE_DATE:", "").strip()
            elif line.startswith("TITLE:"):
                metadata["title"] = line.replace("TITLE:", "").strip()
            elif line.startswith("==="):
                body_start_index = i + 1
                break

        body_text = "\n".join(lines[body_start_index:]).strip()
        
        # SMART FIX: If a file is massive (like changelog), keep the most recent 25,000 chars!
        if len(body_text) > 25000:
            print(f" [TRIM] {metadata['title']} was huge ({len(body_text)} chars). Keeping most recent 25,000 chars.")
            body_text = body_text[:25000]
            
        doc = Document(page_content=body_text, metadata=metadata)
        documents.append(doc)
        print(f" - Loaded: {metadata['title']} ({len(body_text)} chars) -> Type: {metadata['page_type']}")

    return documents


def build_vector_store(folder_path: str = "data/raw_scraped") -> Chroma:
    """
    Splits into 800-char chunks and embeds them in safe batches of 20 with pauses.
    """
    raw_docs = load_documents_from_folder(folder_path)
    
    # 800 chars chunk / 150 overlap
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = text_splitter.split_documents(raw_docs)
    total_chunks = len(chunks)
    print(f"\n[CHUNKING] Prepared {total_chunks} total searchable chunks.")

    # Initialize empty Chroma vector store
    vector_store = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings
    )

    # Safe batching: Add 20 chunks at a time with a 2-second polite pause
    batch_size = 20
    print(f"[VECTOR_DB] Embedding chunks safely in batches of {batch_size}...")
    
    for i in range(0, total_chunks, batch_size):
        batch = chunks[i:i + batch_size]
        print(f" -> Embedding chunks {i+1} to {min(i+batch_size, total_chunks)} of {total_chunks}...")
        vector_store.add_documents(batch)
        if i + batch_size < total_chunks:
            time.sleep(2.0)  # Stay safely below the 100/min rate limit

    print(f"[VECTOR_DB] SUCCESS! All chunks safely embedded and saved to '{CHROMA_PERSIST_DIR}'.")
    return vector_store


def test_retrieval(query: str, k: int = 3):
    """
    Searches the Vector DB and prints results with citations!
    """
    print(f"\n=======================================================")
    print(f"TEST QUERY: '{query}'")
    print(f"=======================================================")
    
    vector_store = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings
    )
    
    results = vector_store.similarity_search(query, k=k)
    
    for i, doc in enumerate(results, 1):
        print(f"\n[Result #{i}]")
        print(f"Source URL : {doc.metadata.get('source_url')}")
        print(f"Page Type  : {doc.metadata.get('page_type')}")
        print(f"Snippet    : {doc.page_content[:200]}...")


if __name__ == "__main__":
    # Build and embed the vector store
    store = build_vector_store()
    
    # Run retrieval test (Official Day 2 Checkpoint!)
    test_retrieval("What is the core product that PostHog offers?")
    test_retrieval("What roles and engineers are they hiring?")