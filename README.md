# 🔍 CompanyLens — AI-Powered Company Intelligence Agent

CompanyLens is an autonomous Retrieval-Augmented Generation (RAG) agent that performs automated research and question-answering on companies using their public web footprint (About, Careers, Blogs, and Changelogs).

---

## 🌟 Key Features

- **Robots-Compliant Web Scraping**: Scrapes target company pages while strictly respecting `robots.txt`, crawl delays, and rate limits.
- **Semantic Vector Store**: Splits text into 800-character chunks with 150-char overlap and embeds them using Google Gemini into ChromaDB.
- **Agentic LangGraph Architecture**: Stateful workflow that coordinates retrieval, synthesis, and grounding nodes.
- **Lightning-Fast Inference**: Integrated with Groq (`qwen/qwen3.8-27b`) for ultra-low latency response generation.
- **Grounded Citations**: Every answer includes explicit `[Source: URL]` attributions pointing to the scraped public data.
- **Interactive Web Interface**: Custom Gradio chat application with modern typography and public link sharing.

---

## 🏗️ Architecture

```
[Target Company Website]
          │
          ▼
   src/scraper.py (Polite crawl & clean HTML)
          │
          ▼
   data/raw_scraped/ (.txt files with metadata headers)
          │
          ▼
   src/vector_store.py (Recursive text chunking & embedding)
          │
          ▼
   [ChromaDB Vector Store] (Google Gemini Embeddings)
          │
          ▼
   src/graphs/agent.py (LangGraph StateGraph Workflow)
       ┌──────────────────────────────┐
       │      [Retrieve Node]         │
       │             │                │
       │      [Generate Node]         │
       └─────────────┬────────────────┘
                     ▼
                 app.py (Gradio Chat Interface)
```

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **Agent Framework** | LangGraph & LangChain |
| **LLM Inference** | Groq (`qwen/qwen3.8-27b`) |
| **Embeddings** | Google Generative AI (`models/gemini-embedding-001`) |
| **Vector Database** | ChromaDB (`langchain-chroma`) |
| **Scraper** | BeautifulSoup4 & Requests |
| **UI** | Gradio |

---

## 📁 Project Structure

```
CompanyLens/
├── app.py                     # Gradio Web Interface
├── requirements.txt           # Project Dependencies
├── .env.example               # Environment template
├── data/
│   ├── raw_scraped/           # Scraped raw company text files
│   └── vector_db/             # Local ChromaDB persistent storage
└── src/
    ├── scraper.py             # Multi-page company web scraper
    ├── vector_store.py        # Chunking & vector embedding pipeline
    ├── rag_chain.py           # Core RAG retrieval chain
    └── graphs/
        └── agent.py           # LangGraph state machine & agent workflow
```

---

## 🚀 Quickstart Guide

### 1. Clone the repository
```bash
git clone https://github.com/riddhimnagarle/company-lens.git
cd company-lens
```

### 2. Set up virtual environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the web application
```bash
python app.py
```
Open your browser at `http://127.0.0.1:7860` or access the generated public share link.

---

## 💡 Example Queries

- *"What is Ghost and what does it do?"*
- *"Who founded Ghost and what is their founding story?"*
- *"What is Ghost's business model as an open-source non-profit?"*
- *"What engineering roles and technologies is the team looking for?"*
