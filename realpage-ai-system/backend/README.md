# RealPage AI Resolution System - Backend

## Tech Stack

| Component | Technology | Reason |
|-----------|------------|--------|
| **API Framework** | FastAPI (Python) | Async support, auto-docs, type hints |
| **Database** | SQLite | Simple setup, sufficient for MVP, no server needed |
| **ORM** | SQLAlchemy | Pythonic database operations, migration support |
| **Authentication** | JWT (python-jose) | Stateless, secure token-based auth |
| **Password Hashing** | bcrypt (passlib) | Industry standard password security |
| **RAG Integration** | LangChain + OpenAI | For knowledge base search and resolution generation |

---

## Database Schema

### ERD Overview

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   realpage_user │       │  support_agent  │       │     ticket      │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ username        │       │ username        │       │ ticket_number   │
│ email           │       │ email           │       │ conversation_id │
│ password_hash   │       │ password_hash   │       │ channel         │
│ role            │       │ agent_id        │       │ customer_role   │
│ created_at      │       │ tier            │       │ product         │
└────────┬────────┘       │ created_at      │       │ transcript      │
         │                └────────┬────────┘       │ status          │
         │                         │                │ created_by (FK) │◄── realpage_user
         │                         │                │ assigned_to (FK)│◄── support_agent
         │                         │                │ original_resolution │
         │                         │                │ edited_resolution   │
         │                         │                │ relevancy_score │
         │                         │                │ reference_articles │
         │                         │                │ created_at      │
         │                         │                │ updated_at      │
         │                         │                └─────────────────┘
         │                         │                         │
         │                         │                         ▼
         │                         │                ┌─────────────────┐
         │                         │                │ new_knowledge   │
         │                         │                ├─────────────────┤
         │                         │                │ id (PK)         │
         │                         │                │ knowledge_id    │
         │                         │                │ ticket_id (FK)  │
         │                         │                │ conversation_id │
         │                         │                │ product         │
         │                         │                │ resolution      │
         │                         │                │ reference_articles │
         │                         │                │ created_by (FK) │
         │                         │                │ created_at      │
         │                         │                └─────────────────┘
```

---

### Table 1: `realpage_user`
Users who submit cases (Tier 1 agents / RealPage employees)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| `username` | VARCHAR(100) | NOT NULL | Display name |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | Login email |
| `password_hash` | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| `role` | VARCHAR(50) | DEFAULT 'realpage_user' | User role type |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Account creation date |

**Example:**
```json
{
  "id": 1,
  "username": "John",
  "email": "john@realpage.com",
  "password_hash": "$2b$12$...",
  "role": "realpage_user",
  "created_at": "2024-02-08T10:00:00Z"
}
```

---

### Table 2: `support_agent`
Support agents who review and resolve tickets (Tier 2/3)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| `username` | VARCHAR(100) | NOT NULL | Display name |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | Login email |
| `password_hash` | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| `agent_id` | VARCHAR(50) | UNIQUE, NOT NULL | Agent identifier (e.g., "Agent3") |
| `tier` | VARCHAR(20) | NOT NULL | Support tier (Tier2, Tier3) |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Account creation date |

**Example:**
```json
{
  "id": 1,
  "username": "Alex",
  "email": "alex@realpage.com",
  "password_hash": "$2b$12$...",
  "agent_id": "Agent3",
  "tier": "Tier3",
  "created_at": "2024-02-08T10:00:00Z"
}
```

---

### Table 3: `ticket`
Main ticket/case table with RAG resolution

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| `ticket_id` | VARCHAR(50) | UNIQUE, NOT NULL | System ticket ID (e.g., "CS-35956164") |
| `conversation_id` | VARCHAR(100) | NOT NULL | From Excel - original conversation ID |
| `channel` | VARCHAR(50) | | From Excel/metadata - support channel |
| `customer_role` | VARCHAR(100) | | From Excel - customer's role |
| `product` | VARCHAR(100) | | From Excel - product name |
| `category` | VARCHAR(100) | | RAG-detected issue category |
| `transcript` | TEXT | | From Excel - conversation transcript |
| `first_tier_agent_name` | VARCHAR(100) | | From Excel - original agent name |
| `account_name` | VARCHAR(200) | | From Excel - account name |
| `property_name` | VARCHAR(200) | | From Excel - property name |
| `property_city` | VARCHAR(100) | | From Excel - property city |
| `property_state` | VARCHAR(50) | | From Excel - property state |
| `contact_name` | VARCHAR(100) | | From Excel - contact name |
| `contact_role` | VARCHAR(100) | | From Excel - contact role |
| `contact_phone` | VARCHAR(50) | | From Excel - contact phone |
| `status` | VARCHAR(20) | DEFAULT 'pending' | pending, in_progress, approved, rejected |
| `created_by` | INTEGER | FOREIGN KEY → realpage_user.id | User who created the ticket |
| `assigned_to` | INTEGER | FOREIGN KEY → support_agent.id, NULLABLE | Assigned reviewer |
| `resolution_content` | TEXT | | RAG-generated resolution content |
| `edited_resolution` | TEXT | | Agent-edited resolution (if modified) |
| `relevancy_score` | INTEGER | | Overall relevancy score (0-100) |
| `relevancy_points` | INTEGER | | Relevancy breakdown points |
| `accuracy_points` | INTEGER | | Accuracy breakdown points |
| `completeness_points` | INTEGER | | Completeness breakdown points |
| `reasoning` | TEXT | | AI reasoning for the score |
| `kb_id` | VARCHAR(50) | | Reference KB article ID |
| `script_id` | VARCHAR(50) | | Reference Script ID |
| `generated_kb_id` | VARCHAR(50) | | AI-generated KB entry ID |
| `similarity_score` | FLOAT | | Vector similarity score |
| `distance` | FLOAT | | Vector distance |
| `priority` | VARCHAR(20) | | Priority level (High/Medium/Low) |
| `sentiment` | VARCHAR(50) | | Customer sentiment |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Ticket creation date |
| `updated_at` | DATETIME | | Last modification date |
| `resolved_at` | DATETIME | | Resolution date |

**Status Flow:**
```
pending → in_progress → approved/rejected
                ↓
         (if approved) → creates new_knowledge entry
```

**Example:**
```json
{
  "id": 1,
  "ticket_id": "CS-35956164",
  "conversation_id": "CONV-JBUXV0X4SB",
  "channel": "Chat",
  "customer_role": "Accounting Clerk",
  "product": "ExampleCo PropertySuite Affordable",
  "category": "Certifications",
  "transcript": "Customer: I need help with certification...",
  "first_tier_agent_name": "Kris",
  "account_name": "ABC Properties",
  "property_name": "Sunset Apartments",
  "property_city": "Dallas",
  "property_state": "TX",
  "contact_name": "Jane Doe",
  "contact_role": "Property Manager",
  "contact_phone": "555-123-4567",
  "status": "pending",
  "created_by": 1,
  "assigned_to": null,
  "resolution_content": "KB: KB-094D40D3B5",
  "edited_resolution": null,
  "relevancy_score": 85,
  "relevancy_points": 35,
  "accuracy_points": 30,
  "completeness_points": 20,
  "reasoning": "The generated response is relevant as it addresses the user's issue...",
  "kb_id": "KB-094D40D3B5",
  "script_id": "SCRIPT-0521",
  "generated_kb_id": "KB-SYN-0127",
  "similarity_score": 0.5718,
  "distance": 0.7487,
  "priority": "High",
  "sentiment": "Relieved",
  "created_at": "2024-02-08T10:00:00Z",
  "updated_at": null,
  "resolved_at": null
}
```

---

### Table 4: `new_knowledge`
Approved resolutions added to knowledge base

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| `knowledge_id` | VARCHAR(50) | UNIQUE, NOT NULL | Display ID (e.g., "KB-NEW-001") |
| `ticket_id` | INTEGER | FOREIGN KEY → ticket.id | Source ticket |
| `conversation_id` | VARCHAR(100) | | Original conversation ID |
| `product` | VARCHAR(100) | | Product category |
| `resolution` | TEXT | NOT NULL | Final approved resolution |
| `reference_articles` | TEXT | | JSON array of related KB/Script IDs |
| `created_by` | INTEGER | FOREIGN KEY → support_agent.id | Agent who approved |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Knowledge creation date |

**Example:**
```json
{
  "id": 1,
  "knowledge_id": "KB-NEW-0001",
  "ticket_id": 1,
  "conversation_id": "CONV-12345",
  "product": "RealPage Accounting",
  "resolution": "Final approved solution for report access issues...",
  "reference_articles": "[\"KB-001\", \"KB-023\"]",
  "created_by": 1,
  "created_at": "2024-02-08T14:30:00Z"
}
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/login` | Login (returns JWT) | No |
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/refresh` | Refresh JWT token | Yes |
| GET | `/api/auth/me` | Get current user info | Yes |

### Tickets (Cases)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/tickets/upload` | Upload Excel & create tickets | Yes (User) |
| GET | `/api/tickets` | List all tickets (filtered by role) | Yes |
| GET | `/api/tickets/{id}` | Get ticket details | Yes |
| GET | `/api/tickets/pending` | Get pending tickets | Yes (Agent) |
| GET | `/api/tickets/resolved` | Get resolved tickets | Yes (Agent) |
| PATCH | `/api/tickets/{id}/status` | Update ticket status | Yes (Agent) |
| PATCH | `/api/tickets/{id}/resolution` | Edit resolution | Yes (Agent) |
| POST | `/api/tickets/{id}/approve` | Approve ticket (creates knowledge) | Yes (Agent) |
| POST | `/api/tickets/{id}/reject` | Reject ticket | Yes (Agent) |

### Knowledge Base

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/knowledge` | List knowledge entries | Yes |
| GET | `/api/knowledge/{id}` | Get knowledge details | Yes |
| GET | `/api/knowledge/search` | Search knowledge base | Yes |

### RAG Integration

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/rag/generate` | Generate resolution from transcript | Yes |
| POST | `/api/chatbot/message` | Chat with AI assistant | Yes |

---

## RAG Response Structure

When processing a transcript, the RAG system returns this response **for each row in the Excel**:

```json
{
  "ticket_id": "CS-35956164",
  "created_date": "2024-02-08",
  "conversation_id": "CONV-JBUXV0X4SB",
  "first_tier_agent_name": "Kris",
  "product": "ExampleCo PropertySuite Affordable",
  "category": "Certifications",
  "resolution": {
    "content": "KB: KB-094D40D3B5",
    "agent_id": "Kris",
    "relevancy_score": 85,
    "relevancy_breakdown": {
      "relevancy_points": 35,
      "accuracy_points": 30,
      "completeness_points": 20
    },
    "reasoning": "The generated response is relevant as it addresses the user's issue with actionable steps. However, it lacks some accuracy as it does not mention the application of the Tier 3 script, which was a key part of the actual resolution.",
    "reference_article": {
      "kb_id": "KB-094D40D3B5",
      "script_id": "SCRIPT-0521",
      "generated_kb_id": "KB-SYN-0127"
    }
  },
  "metadata": {
    "similarity_score": 0.5718,
    "distance": 0.7487,
    "priority": "High",
    "sentiment": "Relieved",
    "channel": "Chat"
  }
}
```

### RAG Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `ticket_id` | string | Unique ticket identifier (e.g., "CS-35956164") |
| `created_date` | string | Ticket creation date |
| `conversation_id` | string | Original conversation ID from Excel |
| `first_tier_agent_name` | string | Agent who handled the conversation |
| `product` | string | Product name |
| `category` | string | Issue category |
| `resolution.content` | string | KB article reference or resolution content |
| `resolution.agent_id` | string | Agent ID |
| `resolution.relevancy_score` | integer | Overall relevancy score (0-100) |
| `resolution.relevancy_breakdown` | object | Score breakdown (relevancy, accuracy, completeness) |
| `resolution.reasoning` | string | AI reasoning for the score |
| `resolution.reference_article.kb_id` | string | Knowledge Base article ID |
| `resolution.reference_article.script_id` | string | Script ID used |
| `resolution.reference_article.generated_kb_id` | string | AI-generated KB entry ID |
| `metadata.similarity_score` | float | Vector similarity score |
| `metadata.distance` | float | Vector distance |
| `metadata.priority` | string | Priority level (High/Medium/Low) |
| `metadata.sentiment` | string | Customer sentiment |
| `metadata.channel` | string | Support channel |

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Environment configuration
│   ├── database.py             # SQLite/SQLAlchemy setup
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── agent.py
│   │   ├── ticket.py
│   │   └── knowledge.py
│   │
│   ├── schemas/                # Pydantic schemas (request/response)
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── ticket.py
│   │   └── knowledge.py
│   │
│   ├── routers/                # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── tickets.py
│   │   ├── knowledge.py
│   │   └── rag.py
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── ticket_service.py
│   │   ├── knowledge_service.py
│   │   └── rag_service.py
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── security.py         # JWT, password hashing
│       └── excel_parser.py     # Excel file processing
│
├── data/
│   └── realpage.db             # SQLite database file
│
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_tickets.py
│   └── test_knowledge.py
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup Instructions

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Create `.env` file:

```env
# Database
DATABASE_URL=sqlite:///./data/realpage.db

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (for RAG)
OPENAI_API_KEY=sk-your-openai-key

# CORS
FRONTEND_URL=http://localhost:5173
```

### 4. Initialize Database

```bash
python -c "from app.database import init_db; init_db()"
```

### 5. Run Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 6. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Requirements.txt

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
pydantic==2.5.3
openpyxl==3.1.2
langchain==0.1.0
openai==1.10.0
```

---

## Database Choice: SQLite

### Why SQLite is sufficient:

| Factor | Assessment |
|--------|------------|
| **Concurrent Users** | < 100 simultaneous → ✅ SQLite handles this |
| **Data Volume** | < 100K records → ✅ No issues |
| **Deployment** | Single server → ✅ Perfect fit |
| **Setup Complexity** | Minimal → ✅ No DB server needed |
| **Backup** | Simple file copy → ✅ Easy |
| **Development** | Fastest iteration → ✅ Ideal for MVP |

### When to migrate to PostgreSQL:

- Multiple server instances (horizontal scaling)
- > 1000 concurrent users
- Complex queries with heavy joins
- Full-text search requirements
- Production deployment with high availability needs

### Migration Path:

SQLAlchemy makes migration easy - just change the connection string:
```python
# SQLite
DATABASE_URL = "sqlite:///./data/realpage.db"

# PostgreSQL (future)
DATABASE_URL = "postgresql://user:pass@localhost/realpage"
```

---

## Flow Diagrams

### Ticket Creation Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  User Portal │────▶│ Upload Excel │────▶│  Parse Data  │────▶│  RAG Engine  │
└──────────────┘     └──────────────┘     └──────────────┘     └──────┬───────┘
                                                                      │
                     ┌──────────────┐     ┌──────────────┐            │
                     │ Create Ticket│◀────│  Generate    │◀───────────┘
                     │  (pending)   │     │  Resolution  │
                     └──────────────┘     └──────────────┘
```

### Ticket Resolution Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Agent Views  │────▶│ Review/Edit  │────▶│   Approve    │
│   Ticket     │     │  Resolution  │     │   or Reject  │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                          ┌───────────────────────┴───────────────────────┐
                          │                                               │
                          ▼                                               ▼
                  ┌──────────────┐                               ┌──────────────┐
                  │   APPROVED   │                               │   REJECTED   │
                  │              │                               │              │
                  │ • Update     │                               │ • Update     │
                  │   ticket     │                               │   ticket     │
                  │   status     │                               │   status     │
                  │              │                               │              │
                  │ • Create new │                               └──────────────┘
                  │   knowledge  │
                  │   entry      │
                  └──────────────┘
```

---

## Next Steps

1. [ ] Initialize FastAPI project structure
2. [ ] Create SQLAlchemy models
3. [ ] Implement authentication endpoints
4. [ ] Implement ticket CRUD operations
5. [ ] Integrate RAG for resolution generation
6. [ ] Connect frontend to backend APIs
7. [ ] Add unit tests
8. [ ] Deploy to production

---

## Questions?

For any clarifications on the backend architecture, please reach out to the development team.
