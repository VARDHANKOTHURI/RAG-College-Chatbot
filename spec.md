# RAG-Based College Chatbot — Development Specification

## 1. Project Overview & Tech Stack

### Project Overview

Build a full-stack AI-powered **RAG-Based College Chatbot** that acts as a centralized information assistant for students.

The system allows students to ask natural-language questions about college-related information such as:

* Admissions
* Departments
* Courses
* Fees
* Examinations
* Academic calendar
* Hostel
* Library
* Clubs and events
* Scholarships
* Placements
* College policies
* Notices and announcements
* Rules and regulations
* Frequently asked questions

Instead of relying only on an LLM's general knowledge, the chatbot must retrieve relevant information from an authorized college knowledge base before generating an answer.

The system must implement the complete RAG pipeline:

**College Documents → Text Extraction → Cleaning → Chunking → Embeddings → Vector Database → Similarity Search → Relevant Context → LLM → Answer + Sources**

The chatbot should clearly indicate when the requested information is not available in the uploaded knowledge base rather than generating unsupported information.

### Tech Stack

* **Frontend:** React.js / Next.js, Tailwind CSS, Axios, React Context or Zustand
* **Backend:** Python, FastAPI, Pydantic
* **Database:** MongoDB with MongoDB Atlas
* **Vector Database:** Qdrant
* **RAG Framework:** LangChain
* **Embeddings:** Hugging Face Sentence Transformers or configurable embedding API
* **LLM:** Google Gemini / OpenRouter
* **Authentication:** JWT-based authentication with bcrypt password hashing
* **Document Processing:** PyMuPDF, python-docx
* **OCR:** Tesseract / configurable OCR service for scanned documents
* **Real-Time Responses:** Server-Sent Events or streaming API
* **Deployment:** Vercel for frontend and Render/Railway for backend
* **Version Control:** Git and GitHub

---

# 2. Authentication & User Management

## Authentication

The authentication system must support:

* Student registration
* Student login
* Admin login
* JWT-based authentication
* Protected routes
* Password hashing
* Persistent login state
* Logout
* Current-user profile endpoint
* Role-based authorization

### User Roles

#### Student

Students can:

* Ask questions
* View answers
* View sources
* View chat history
* Create conversations
* Delete conversations
* Submit answer feedback

#### Admin

Admins can:

* Upload documents
* View documents
* Update documents
* Delete documents
* Manage document collections
* View document processing status
* View chatbot analytics
* Manage users
* Review unanswered questions

---

# 3. Document Management System

## Document Upload

Administrators must be able to upload college documents through the admin dashboard.

Supported formats:

* PDF
* DOCX
* TXT

Optional support:

* Scanned PDFs
* Images through OCR

Each uploaded document should contain metadata such as:

* Document ID
* File name
* Title
* Description
* Category
* Department
* Academic year
* Version
* Upload date
* Uploaded by
* Processing status
* Number of pages
* Number of chunks

### Document Categories

The system should support categories such as:

* Admissions
* Academics
* Exams
* Fees
* Hostel
* Library
* Placements
* Scholarships
* Departments
* Clubs
* Events
* Policies
* Notices
* General FAQ

---

# 4. Document Processing Pipeline

When an administrator uploads a document, the backend must process it through the following pipeline:

**Upload → Validate → Extract Text → Clean Text → Split into Chunks → Generate Embeddings → Store Vectors → Store Metadata**

## Text Extraction

For PDF documents:

* Extract text page by page using PyMuPDF.
* Preserve page numbers.
* Preserve document metadata.

For DOCX:

* Extract paragraphs and tables.

For scanned documents:

* Detect whether meaningful text is available.
* Run OCR when required.

## Text Cleaning

The processing service should:

* Remove unnecessary whitespace
* Remove repeated headers where possible
* Remove irrelevant formatting characters
* Normalize extracted text
* Preserve meaningful headings
* Preserve page references

## Chunking

Documents must be divided into smaller chunks before embedding.

Each chunk should store:

* chunk_id
* document_id
* text
* page_number
* section
* category
* department
* academic_year
* embedding_id

The chunking strategy should use configurable:

* Chunk size
* Chunk overlap
* Separators

---

# 5. Embedding Generation

Each processed document chunk must be converted into a numerical vector representation.

### Embedding Flow

**Text Chunk → Embedding Model → Vector → Vector Database**

The embedding service should:

* Generate embeddings for document chunks
* Store embeddings in Qdrant
* Associate each vector with document metadata
* Support batch embedding
* Handle embedding failures gracefully

The embedding model should be configurable so that it can be replaced without redesigning the complete application.

---

# 6. Vector Database & Semantic Search

## Vector Database

Qdrant will be used as the vector database.

The system must store:

* Document vectors
* Chunk text
* Document ID
* Page number
* Category
* Department
* Academic year
* Document version

## Similarity Search

When a student asks a question:

**Question → Query Embedding → Qdrant Search → Top-K Relevant Chunks**

The retrieval service should support configurable:

* Top-K results
* Similarity threshold
* Metadata filtering

### Metadata Filtering

The system should optionally filter results based on:

* Department
* Category
* Academic year
* Document collection
* Document version

---

# 7. RAG Pipeline

The RAG pipeline is the core component of the application.

### Required Pipeline

**User Question**

↓

**Query Processing**

↓

**Question Embedding**

↓

**Vector Similarity Search**

↓

**Retrieve Top-K Chunks**

↓

**Optional Re-ranking**

↓

**Build Context**

↓

**Prompt LLM**

↓

**Generate Answer**

↓

**Attach Sources**

↓

**Return Response**

## Retrieval

The retriever must search the vector database for semantically relevant chunks.

The system should not send the entire college knowledge base to the LLM.

Only the most relevant retrieved context should be provided.

## Context Construction

The backend should construct an LLM prompt containing:

* User question
* Retrieved document chunks
* Source information
* Instructions to answer only from the supplied context

### Grounding Rule

The LLM must be instructed:

> Answer using the provided college knowledge base. If the information is not available in the retrieved context, clearly state that the information could not be found in the available college documents.

The system should avoid presenting unsupported information as factual.

---

# 8. Unknown Question Handling

Unknown-question handling is mandatory.

If retrieval does not find sufficiently relevant information, the chatbot should not hallucinate an answer.

Example response:

> "I couldn't find this information in the available college documents. Please contact the concerned department or administrator for accurate information."

The system should store these unanswered questions so administrators can identify knowledge gaps.

---

# 9. Answer & Source System

Every successful RAG response should contain:

* Generated answer
* Relevant source documents
* Document title
* Page number where available
* Relevant text snippet
* Relevance score where available

### Example

**Answer:**

The examination fee must be paid before the deadline specified in the academic examination notice.

**Sources:**

* Examination Guidelines 2026 — Page 4
* Academic Fee Notice — Page 2

Students should be able to click or expand a source to inspect the supporting information.

---

# 10. Chat Interface

The student-facing chatbot should provide a modern conversational interface.

### Features

* New conversation
* Chat input
* Send message
* Streaming response
* Loading state
* Markdown responses
* Source cards
* Suggested questions
* Conversation history
* Delete conversation
* Feedback buttons
* Error handling

### Suggested Questions

The interface may display questions such as:

* "What are the admission requirements?"
* "When are the semester exams?"
* "What are the hostel fees?"
* "What scholarships are available?"
* "Tell me about the CSE department."
* "What documents are required for admission?"

---

# 11. Conversation & Chat History

The system must maintain conversation history for authenticated students.

Each conversation should contain:

* Conversation ID
* User ID
* Title
* Created date
* Updated date
* Messages

Each message should contain:

* Role
* Content
* Timestamp
* Retrieved sources
* Retrieval metadata
* Feedback

The chatbot may use recent conversation messages as context when resolving follow-up questions.

Example:

**Student:** What is the hostel fee?

**Bot:** The annual hostel fee is ...

**Student:** What about first-year students?

The system should understand that the second question refers to the hostel-fee discussion when sufficient conversation context exists.

---

# 12. Admin Dashboard

The admin dashboard should provide centralized control over the college knowledge base.

### Dashboard Metrics

Display:

* Total documents
* Processed documents
* Failed documents
* Total document chunks
* Total chatbot questions
* Answered questions
* Unanswered questions
* Active users
* Most frequently asked questions

### Document Management

Admins should be able to:

* Upload documents
* Search documents
* Filter documents
* View document details
* Reprocess documents
* Replace document versions
* Delete documents
* View processing status

---

# 13. Document Version Management

The system should support document versions.

Example:

**Academic Calendar 2025 → Version 1**

**Academic Calendar 2026 → Version 2**

When a new version is uploaded, the system should:

1. Process the new document
2. Create new chunks
3. Generate embeddings
4. Store the new vectors
5. Mark the new version as active
6. Optionally archive the previous version

The chatbot should prioritize the currently active document version.

---

# 14. Multiple Knowledge Collections

The system should support multiple document collections.

Example:

* General College Knowledge
* CSE Department
* ECE Department
* MBA Department
* Admissions
* Examination Cell
* Placement Cell

A user query can be searched across all permitted collections or restricted to a selected collection.

---

# 15. Hybrid Search

As a bonus enhancement, the retrieval system should support hybrid retrieval.

### Hybrid Pipeline

**User Question**

↓

**Semantic Search**

*

**Keyword Search**

↓

**Combine Results**

↓

**Re-rank**

↓

**Top Relevant Chunks**

This can improve retrieval for queries containing:

* Course codes
* Regulation numbers
* Notice numbers
* Specific dates
* Faculty names
* Exact policy terminology

---

# 16. Re-Ranking

An optional re-ranking layer can improve retrieval accuracy.

### Pipeline

**Vector Search → Candidate Chunks → Re-ranker → Best Chunks → LLM**

The re-ranker should evaluate the relevance of retrieved chunks against the user's question.

Only the highest-quality chunks should be passed to the LLM.

---

# 17. Multilingual Support

The chatbot may support multiple languages.

Initial target:

* English
* Telugu
* Hindi

The system should detect or accept the user's language and generate the response in the requested language while still retrieving information from the same knowledge base.

---

# 18. Feedback System

Students should be able to provide feedback on generated answers.

### Feedback

* 👍 Helpful
* 👎 Not helpful

Optional feedback fields:

* Incorrect information
* Missing information
* Irrelevant source
* Answer not clear
* Other

Administrators can use feedback to identify poor retrieval or knowledge-base gaps.

---

# 19. AI-Generated FAQs

The system may analyze frequently asked questions and generate FAQ suggestions.

Pipeline:

**Chat History → Frequently Asked Questions → Group Similar Questions → Generate FAQ → Admin Review → Publish**

Only administrator-approved FAQs should become official knowledge-base content.

---

# 20. Database Architecture

## MongoDB Collections

### Users

Stores:

* _id
* name
* email
* passwordHash
* role
* createdAt
* lastLogin

### Documents

Stores:

* _id
* title
* fileName
* description
* category
* department
* academicYear
* version
* status
* uploadedBy
* fileUrl
* totalPages
* totalChunks
* createdAt
* updatedAt

### DocumentChunks

Stores:

* _id
* documentId
* chunkIndex
* text
* pageNumber
* section
* metadata
* vectorId

### Conversations

Stores:

* _id
* userId
* title
* createdAt
* updatedAt

### Messages

Stores:

* _id
* conversationId
* role
* content
* sources
* retrievalMetadata
* feedback
* createdAt

### Feedback

Stores:

* _id
* userId
* messageId
* rating
* reason
* comment
* createdAt

### Collections

Stores:

* _id
* name
* description
* department
* accessRules
* createdAt

### UnansweredQuestions

Stores:

* _id
* userId
* question
* conversationId
* retrievalScore
* status
* adminNotes
* createdAt

---

# 21. Backend Architecture

The backend should follow a layered architecture.

### Routes

Responsible for:

* HTTP endpoints
* Request routing
* Authentication middleware
* Validation

### Controllers

Responsible for:

* Request parsing
* Calling services
* Response formatting

Controllers should not contain core business logic.

### Services

Responsible for:

* Authentication
* Document management
* Document processing
* Embedding generation
* Retrieval
* RAG orchestration
* Chat management
* Analytics

### RAG Layer

Contains:

* Document loader
* Text splitter
* Embedding service
* Vector store
* Retriever
* Re-ranker
* Prompt builder
* LLM service
* RAG pipeline

### Database Layer

Responsible for:

* MongoDB connections
* Models
* Queries
* Persistence

---

# 22. RAG Service Architecture

The RAG module should be separated into independent services.

### documentLoader

Loads:

* PDF
* DOCX
* TXT

### textProcessor

Responsible for:

* Cleaning
* Normalization
* Chunking

### embeddingService

Responsible for:

* Generating embeddings
* Batch processing
* Embedding model configuration

### vectorStoreService

Responsible for:

* Creating collections
* Upserting vectors
* Searching vectors
* Deleting vectors
* Filtering metadata

### retrievalService

Responsible for:

* Query embedding
* Similarity search
* Threshold filtering
* Top-K selection

### rerankingService

Optional service responsible for:

* Re-ranking retrieved chunks
* Selecting highest-quality context

### ragService

Coordinates:

**Question → Retrieval → Context → Prompt → LLM → Sources**

---

# 23. API Endpoints

## Health

* `GET /api/health` — System health check

## Authentication

* `POST /api/auth/register` — Register user
* `POST /api/auth/login` — Login user
* `GET /api/auth/me` — Get current user
* `POST /api/auth/logout` — Logout

## Chat

* `POST /api/chat` — Ask a question
* `POST /api/chat/stream` — Stream RAG response
* `GET /api/chat/conversations` — List conversations
* `GET /api/chat/conversations/:id` — Get conversation
* `DELETE /api/chat/conversations/:id` — Delete conversation

## Sources

* `GET /api/chat/messages/:id/sources` — Get sources used for an answer

## Documents

* `GET /api/documents` — List documents
* `GET /api/documents/:id` — Get document
* `POST /api/documents/upload` — Upload document
* `POST /api/documents/:id/reprocess` — Reprocess document
* `PUT /api/documents/:id` — Update document metadata
* `DELETE /api/documents/:id` — Delete document

## Collections

* `GET /api/collections` — List collections
* `POST /api/collections` — Create collection
* `PUT /api/collections/:id` — Update collection
* `DELETE /api/collections/:id` — Delete collection

## Feedback

* `POST /api/feedback` — Submit answer feedback
* `GET /api/feedback` — Admin feedback list

## Analytics

* `GET /api/admin/analytics` — Dashboard statistics
* `GET /api/admin/unanswered` — Unanswered questions
* `GET /api/admin/popular-questions` — Frequently asked questions

---

# 24. Frontend Pages

The frontend should contain the following pages.

### `/`

Landing page containing:

* College chatbot introduction
* RAG explanation
* Feature highlights
* Login/register buttons
* Responsive design

### `/login`

Contains:

* Email
* Password
* Login button
* Validation
* Error messages

### `/register`

Contains:

* Name
* Email
* Password
* Confirm password
* Registration validation

### `/chat`

Main student chatbot interface containing:

* Conversation sidebar
* Chat messages
* Input box
* Send button
* Streaming response
* Source cards
* Suggested questions
* Feedback buttons

### `/chat/:conversationId`

Individual conversation page.

### `/documents`

Admin document-management page containing:

* Upload interface
* Document table
* Search
* Filters
* Processing status
* Reprocess
* Delete

### `/admin`

Admin dashboard containing:

* Metrics
* Document statistics
* Question statistics
* User statistics
* Knowledge gaps

### `/settings`

User settings containing:

* Profile
* Password
* Preferences
* Logout

---

# 25. Frontend Components

Recommended components:

```text
components/
├── layout/
│   ├── Navbar.jsx
│   ├── Sidebar.jsx
│   └── ProtectedRoute.jsx
│
├── chat/
│   ├── ChatWindow.jsx
│   ├── ChatMessage.jsx
│   ├── ChatInput.jsx
│   ├── SourceCard.jsx
│   ├── SuggestedQuestions.jsx
│   ├── ConversationList.jsx
│   └── FeedbackButtons.jsx
│
├── documents/
│   ├── DocumentUpload.jsx
│   ├── DocumentTable.jsx
│   ├── DocumentCard.jsx
│   ├── DocumentFilters.jsx
│   └── ProcessingStatus.jsx
│
├── admin/
│   ├── AdminDashboard.jsx
│   ├── MetricsCard.jsx
│   ├── QuestionAnalytics.jsx
│   └── UnansweredQuestions.jsx
│
└── common/
    ├── Button.jsx
    ├── Modal.jsx
    ├── Loader.jsx
    └── ErrorMessage.jsx
```

---

# 26. Backend Folder Structure

```text
backend/
└── app/
    ├── main.py
    │
    ├── config/
    │   ├── settings.py
    │   └── database.py
    │
    ├── routes/
    │   ├── auth.py
    │   ├── chat.py
    │   ├── documents.py
    │   ├── collections.py
    │   ├── feedback.py
    │   └── admin.py
    │
    ├── controllers/
    │   ├── auth_controller.py
    │   ├── chat_controller.py
    │   ├── document_controller.py
    │   └── admin_controller.py
    │
    ├── services/
    │   ├── auth_service.py
    │   ├── document_service.py
    │   ├── chat_service.py
    │   └── analytics_service.py
    │
    ├── rag/
    │   ├── document_loader.py
    │   ├── text_processor.py
    │   ├── chunker.py
    │   ├── embedding_service.py
    │   ├── vector_store.py
    │   ├── retrieval_service.py
    │   ├── reranking_service.py
    │   ├── prompt_builder.py
    │   ├── llm_service.py
    │   └── rag_pipeline.py
    │
    ├── models/
    │   ├── user.py
    │   ├── document.py
    │   ├── chunk.py
    │   ├── conversation.py
    │   ├── message.py
    │   ├── feedback.py
    │   └── collection.py
    │
    ├── schemas/
    │   ├── auth.py
    │   ├── chat.py
    │   ├── document.py
    │   └── feedback.py
    │
    ├── middleware/
    │   ├── auth.py
    │   └── error_handler.py
    │
    └── utils/
        ├── security.py
        ├── file_utils.py
        └── logger.py
```

---

# 27. Frontend Folder Structure

```text
frontend/
└── src/
    ├── components/
    │   ├── layout/
    │   ├── chat/
    │   ├── documents/
    │   ├── admin/
    │   └── common/
    │
    ├── pages/
    │   ├── index.jsx
    │   ├── login.jsx
    │   ├── register.jsx
    │   ├── chat/
    │   │   ├── index.jsx
    │   │   └── [conversationId].jsx
    │   ├── documents.jsx
    │   ├── admin.jsx
    │   └── settings.jsx
    │
    ├── services/
    │   ├── api.js
    │   └── chatService.js
    │
    ├── store/
    │   ├── authStore.js
    │   └── chatStore.js
    │
    └── utils/
        └── formatters.js
```

---

# 28. Environment Configuration

The application should use environment variables for sensitive configuration.

Example:

```text
MONGODB_URI=
JWT_SECRET=

QDRANT_URL=
QDRANT_API_KEY=

GEMINI_API_KEY=
OPENROUTER_API_KEY=

EMBEDDING_MODEL=

UPLOAD_DIR=
FRONTEND_URL=
```

API keys, database credentials, JWT secrets, and other sensitive values must never be committed to GitHub.

---

# 29. Security Requirements

The application should implement:

* Password hashing
* JWT authentication
* Protected API routes
* Role-based authorization
* File-type validation
* File-size validation
* Secure file handling
* Input validation
* CORS configuration
* Rate limiting
* Environment-based secrets
* Secure error handling

Admin-only document operations must be protected through role-based middleware.

---

# 30. Error Handling

The backend must return structured errors.

Examples:

```text
AUTH_REQUIRED
INVALID_CREDENTIALS
FORBIDDEN
INVALID_FILE_TYPE
FILE_TOO_LARGE
DOCUMENT_PROCESSING_FAILED
EMBEDDING_FAILED
VECTOR_SEARCH_FAILED
LLM_ERROR
NO_RELEVANT_CONTEXT
CONVERSATION_NOT_FOUND
DOCUMENT_NOT_FOUND
```

The frontend should display user-friendly messages instead of exposing internal stack traces.

---

# 31. RAG Evaluation

The project should include basic evaluation of retrieval and answer quality.

### Retrieval Metrics

Evaluate:

* Precision@K
* Recall@K
* Context relevance
* Retrieval similarity

### Answer Metrics

Evaluate:

* Faithfulness
* Answer relevance
* Context utilization
* Hallucination rate

A small evaluation dataset should contain:

* Question
* Expected answer
* Expected source document
* Expected page/chunk

This makes the project stronger as an AI/ML portfolio project.

---

# 32. Logging & Monitoring

The backend should log:

* Authentication events
* Document uploads
* Document processing
* Embedding generation
* Retrieval operations
* LLM requests
* Errors
* Chat requests

Sensitive information such as passwords and API keys must never be logged.

---

# 33. Bonus Features

The following features can be added after the core RAG system is stable:

### Multiple Collections

Department-wise and topic-wise knowledge bases.

### OCR

Process scanned college notices and PDFs.

### Hybrid Search

Combine keyword and semantic retrieval.

### Re-Ranking

Improve retrieval precision using a re-ranking model.

### Multilingual Chatbot

Support English, Telugu, and Hindi.

### Voice Input

Convert student speech into text.

### Voice Response

Convert chatbot answers into speech.

### Conversation Export

Export conversations as:

* PDF
* TXT
* Markdown

### Source Highlighting

Highlight the exact passage used to generate an answer.

### Confidence Score

Display retrieval confidence or relevance information.

### AI FAQ Generation

Automatically identify common student questions.

### Admin Analytics

Show:

* Most asked questions
* Most searched topics
* Unanswered questions
* Retrieval failures
* User activity

### Streaming Responses

Display LLM output progressively instead of waiting for the complete response.

---

# 34. Development Phases

## Phase 1 — Project Setup

Set up:

* React/Next.js frontend
* FastAPI backend
* MongoDB
* Qdrant
* Git/GitHub
* Environment configuration
* Basic project structure

Deliverable:

**Frontend + Backend + Database running successfully**

---

## Phase 2 — Authentication

Implement:

* Registration
* Login
* JWT
* Password hashing
* Protected routes
* Student/admin roles
* Logout

Deliverable:

**Working authentication system**

---

## Phase 3 — Document Management

Implement:

* Admin dashboard
* PDF/DOCX/TXT upload
* Document metadata
* Document listing
* Document deletion
* Processing status

Deliverable:

**Admin can upload and manage college documents**

---

## Phase 4 — Document Processing

Implement:

* PDF extraction
* DOCX extraction
* Text cleaning
* Chunking
* Metadata generation

Deliverable:

**Uploaded documents converted into searchable chunks**

---

## Phase 5 — Embeddings & Vector Database

Implement:

* Embedding service
* Qdrant collection
* Vector insertion
* Metadata storage
* Vector deletion
* Similarity search

Deliverable:

**Working semantic search system**

---

## Phase 6 — RAG Pipeline

Implement:

* Query embedding
* Similarity retrieval
* Context construction
* Prompt generation
* LLM integration
* Answer generation
* Source extraction

Deliverable:

**End-to-end working RAG chatbot**

---

## Phase 7 — Chat Interface

Implement:

* Chat UI
* Conversations
* Message history
* Source cards
* Suggested questions
* Loading states
* Error handling

Deliverable:

**Complete student-facing chatbot**

---

## Phase 8 — Unknown Question Handling

Implement:

* Similarity threshold
* No-context detection
* Unknown-question response
* Unanswered question storage

Deliverable:

**Hallucination-resistant knowledge-base behavior**

---

## Phase 9 — Admin Dashboard

Implement:

* Document analytics
* Question analytics
* Unanswered questions
* User statistics
* Document processing status

Deliverable:

**Complete admin control panel**

---

## Phase 10 — Advanced Retrieval

Implement optional:

* Hybrid search
* Metadata filtering
* Re-ranking
* Collection-specific retrieval

Deliverable:

**Improved retrieval accuracy**

---

## Phase 11 — Feedback & Evaluation

Implement:

* 👍 / 👎 feedback
* Evaluation dataset
* Retrieval evaluation
* Answer evaluation
* Knowledge-gap analysis

Deliverable:

**Measurable RAG performance**

---

## Phase 12 — Deployment

Deploy:

* Frontend
* Backend
* MongoDB Atlas
* Qdrant
* Environment variables
* Production API
* Production authentication

Perform:

* End-to-end testing
* Security testing
* RAG evaluation
* Performance testing

Deliverable:

**Fully deployed working college chatbot**

---

# 35. Final System Architecture

```text
                    ┌─────────────────────┐
                    │      Student        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   React / Next.js   │
                    │    Chat Interface   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI API     │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │     RAG Pipeline    │
                    │                     │
                    │ Query Processing    │
                    │ Query Embedding     │
                    │ Retrieval           │
                    │ Re-ranking          │
                    │ Context Building    │
                    │ Prompt Generation   │
                    └──────┬───────┬──────┘
                           │       │
                ┌──────────▼───┐ ┌─▼────────────┐
                │   Qdrant     │ │     LLM      │
                │Vector Search │ │Gemini/OpenRtr│
                └──────────────┘ └──────┬───────┘
                                        │
                                        ▼
                              ┌──────────────────┐
                              │ Answer + Sources │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │    Student UI    │
                              └──────────────────┘


             ADMIN DOCUMENT INGESTION PIPELINE

┌──────────────┐
│ College PDF  │
│ DOCX / TXT   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│Text Extraction│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Text Cleaning│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Chunking   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Embeddings  │
└──────┬───────┘
       │
       ▼
┌────────────────────┐
│ Qdrant Vector DB   │
│ + Chunk Metadata   │
└────────────────────┘
```

# 36. Core MVP Definition

The project should **not** be considered complete until the following workflow works end-to-end:

```text
Admin Login
    ↓
Upload College PDF
    ↓
Extract Text
    ↓
Chunk Text
    ↓
Generate Embeddings
    ↓
Store in Qdrant
    ↓
Student Login
    ↓
Ask Question
    ↓
Generate Query Embedding
    ↓
Semantic Search
    ↓
Retrieve Relevant Chunks
    ↓
Send Context + Question to LLM
    ↓
Generate Grounded Answer
    ↓
Display Answer
    ↓
Display Source Document + Page
```

The most important requirement is that the chatbot's answer must actually depend on the **retrieved college documents**. A normal LLM chatbot without document retrieval, embeddings, vector search, and source references does **not** satisfy the project requirements.