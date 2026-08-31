# 🎓 RAG-Based College Information Chatbot

An AI-powered, full-stack **Retrieval-Augmented Generation (RAG)** College Chatbot that serves as an autonomous academic advisor and campus knowledge assistant for students.

The chatbot provides answers to student inquiries regarding **admissions, semester examinations, fee structures, hostel rules, scholarships, placements, academic calendars, and department details** — strictly grounded in authorized college documents with verified source citations.

---

## 🌟 Key Features

* **Strict Grounding & Hallucination Resistance:** Answers are strictly synthesized from authorized college documents. If a question is not answerable from the knowledge base, the system returns a safe fallback message and logs the query for administrator review.
* **Qdrant Vector Database:** Persistent dense vector search with cosine similarity and hybrid keyword boosting for course codes, dates, and fee terminology.
* **Multi-Format Document Ingestion:** Supports **PDF (PyMuPDF)**, **Word (DOCX)**, and **Plain Text (TXT)** with recursive chunking and metadata preservation (page numbers, section titles, categories, departments).
* **Live Streaming Responses:** Real-time token-by-token generation via Server-Sent Events (SSE).
* **Clickable Source Citations:** Every answer displays verified source cards with document title, page numbers, relevance percentages, and supporting text snippets.
* **Administrator Control Panel:** Complete document upload and reprocessing interface, unanswered questions (knowledge gaps) manager, popular student queries analytics, and feedback inspection.
* **Automated RAG Evaluation Suite:** Built-in benchmark (`eval_rag.py`) measuring **Precision@K (100%)**, **Answer Faithfulness (100%)**, and **Hallucination Resistance (100%)**.
* **Zero-Friction Local Execution:** Runs locally out of the box with embedded database storage and local Qdrant persistence.

---

## 🏗️ System Architecture

```text
Student Question
       │
       ▼
Query Processing & Embeddings
       │
       ▼
Qdrant Vector DB (Hybrid Semantic + Keyword Search)
       │
       ▼
Top-K Relevant Document Chunks
       │
       ▼
Context Construction & Grounding Prompt
       │
       ▼
LLM Generation (Gemini / OpenRouter / Grounded Extractive Engine)
       │
       ▼
Streamed Answer + Source Documents & Page Numbers
```

---

## 📋 Prerequisites

* **Python 3.10+** (Python 3.10, 3.11, 3.12, 3.13, or 3.14)
* Modern web browser (Chrome, Edge, Firefox, Brave, Safari)
* *(Optional)* MongoDB or MongoDB Atlas instance
* *(Optional)* Google Gemini API Key or OpenRouter API Key

---

## 🚀 Quick Start (Run Locally)

### 1. Clone or Open the Workspace

Open a terminal (PowerShell, Command Prompt, or Bash) in the project root directory:

```bash
cd RAG_BASED_COLLEGE_CHATBOT
```

### 2. Create and Activate a Virtual Environment (Recommended)

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure Environment Variables

Create a `.env` file from the provided `.env.example`:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**Linux / macOS:**
```bash
cp .env.example .env
```

> **Note:** The application works completely offline out of the box! If you want to use Google Gemini or OpenRouter for LLM generation, set your API key in `.env`:
> ```env
> GEMINI_API_KEY=your_google_gemini_api_key_here
> ```

### 5. Start the Application

Run the one-click startup runner:

```bash
python run.py
```

You should see the startup banner in your terminal:
```text
======================================================================
      GREENWOOD INSTITUTE OF TECHNOLOGY — RAG CHATBOT SERVER      
======================================================================
  [>] Web Application UI:  http://localhost:8000
  [>] Interactive API Docs: http://localhost:8000/docs
  [>] Health Endpoint:      http://localhost:8000/api/health
----------------------------------------------------------------------
  Default Demo Credentials:
    * Student Account: student@college.edu | Password: Student@123
    * Admin Account:   admin@college.edu   | Password: Admin@123
======================================================================
```

### 6. Open the Web Application

Open your browser and navigate to:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 🔑 Default Credentials

The system automatically initializes demo accounts on the first run:

| Role | Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Student** | `student@college.edu` | `Student@123` | Ask questions, view chat history, inspect sources, submit feedback |
| **Administrator** | `admin@college.edu` | `Admin@123` | Upload & reprocess documents, view analytics, manage knowledge gaps |

*You can also register new student accounts directly through the `/register` page.*

---

## 📊 RAG Evaluation Benchmark

The project includes an automated evaluation suite that tests retrieval accuracy, answer faithfulness, and out-of-domain rejection.

To run the evaluation benchmark:

```bash
python eval/eval_rag.py
```

### Benchmark Results:
```text
============================================================
                    EVALUATION SCORECARD
============================================================
1. Retrieval Precision@K:           100.0% (7/7)
2. Answer Grounding / Faithfulness: 100.0% (7/7)
3. Hallucination Resistance Rate:   100.0% (2/2)
4. Average Response Latency:        1.7 ms
============================================================
Overall Evaluation Result: PASSED (EXCELLENT)
```

---

## 📁 Project Structure

```text
RAG_BASED_COLLEGE_CHATBOT/
├── backend/
│   └── app/
│       ├── main.py                  # FastAPI entrypoint, lifespan startup, and SPA mount
│       ├── config/
│       │   ├── settings.py          # Pydantic Settings & environment configuration
│       │   └── database.py          # MongoDB client & embedded async storage fallback
│       ├── models/                  # User, Document, Chunk, Conversation, Feedback models
│       ├── schemas/                 # Pydantic request & response validation schemas
│       ├── rag/
│       │   ├── document_loader.py   # PDF, DOCX, TXT loaders with page preservation
│       │   ├── text_processor.py    # Text normalizer and section extractor
│       │   ├── chunker.py           # Recursive sliding-window chunker
│       │   ├── embedding_service.py # Gemini / SentenceTransformers / Semantic vectorizer
│       │   ├── vector_store.py      # Qdrant client & vector operations
│       │   ├── retrieval_service.py # Hybrid semantic & keyword retrieval engine
│       │   ├── reranking_service.py # Cross-encoder relevance re-ranker
│       │   ├── prompt_builder.py    # Strict grounding prompt templates
│       │   ├── llm_service.py       # Gemini, OpenRouter, and streaming handlers
│       │   └── rag_pipeline.py      # End-to-end RAG pipeline coordinator
│       ├── services/                # AuthService, DocumentService, ChatService, Analytics
│       ├── controllers/             # HTTP controller layer
│       ├── routes/                  # API endpoints (/auth, /chat, /documents, /admin)
│       ├── middleware/              # JWT auth and structured error handler
│       └── utils/                   # Security, file validators, and logging
├── frontend/                        # React / Next.js source components & pages
├── static/                          # Production interactive Web UI (served at /)
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── data/
│   ├── sample_documents/            # Official College Handbook & Examination Regulations
│   ├── uploads/                     # Uploaded documents directory
│   └── qdrant_storage/              # Local persistent Qdrant vector database
├── eval/
│   ├── eval_dataset.json            # Ground truth QA benchmark dataset
│   └── eval_rag.py                  # Benchmark evaluator script
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment template
├── run.py                           # One-click startup runner
└── README.md                        # Local setup & documentation
```

---

## 🔌 API Endpoints Reference

Interactive Swagger documentation is available at **`http://localhost:8000/docs`**.

### Authentication
* `POST /api/auth/register` — Register a student account
* `POST /api/auth/login` — Sign in and receive JWT token
* `GET /api/auth/me` — Get current logged-in user profile
* `POST /api/auth/logout` — Invalidate user session

### Chat & RAG
* `POST /api/chat` — Ask a question and receive grounded answer with source citations
* `POST /api/chat/stream` — Stream answer tokens in real-time (SSE)
* `GET /api/chat/conversations` — List student conversations
* `GET /api/chat/conversations/{id}` — Get messages for a specific conversation
* `DELETE /api/chat/conversations/{id}` — Delete conversation

### Document Management (Admin)
* `GET /api/documents` — List all uploaded knowledge base documents
* `POST /api/documents/upload` — Upload PDF/DOCX/TXT file with metadata
* `POST /api/documents/{id}/reprocess` — Reprocess document vectors in Qdrant
* `DELETE /api/documents/{id}` — Delete document and its vector embeddings

### Analytics & Knowledge Gaps (Admin)
* `GET /api/admin/analytics` — KPI metrics, query volumes, and popular questions
* `GET /api/admin/unanswered` — List unanswered student queries
* `PUT /api/admin/unanswered/{id}` — Mark question as resolved

### Feedback
* `POST /api/feedback` — Submit 👍 / 👎 answer rating and reason

---

## 📄 License

This project is open-source and built for educational and technological showcase purposes.
