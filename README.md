# RealPage SupportMind AI - AI-Powered Customer Support System

## 🎯 Overview

RealPage SupportMind AI is an intelligent customer support resolution system that leverages Retrieval-Augmented Generation (RAG) and AI agents to automatically analyze support tickets, suggest resolutions, and build a self-learning knowledge base.

## 🚀 Key Features

### 1. **AI-Powered Ticket Resolution**
- Automatically processes support tickets and generates relevant resolutions
- Uses classification agents to categorize and prioritize tickets
- Assigns tickets to appropriate support tiers (Tier 1/2/3)

### 2. **RAG-Powered Knowledge Search**
- Semantic search across 722+ support tickets using FAISS vector store
- Natural language query support with automatic summarization
- Returns similar cases with relevance scores and detailed resolutions
- Search by conversation transcripts, issues, or keywords

### 3. **Support Agent Portal**
- Dashboard with pending and resolved ticket management
- Real-time SLA tracking and breach alerts
- Knowledge base integration for quick reference
- Interactive ticket resolution workflow

### 4. **Knowledge Base Management**
- Auto-generates knowledge articles from approved resolutions
- Searchable repository of solutions
- Reference linking to related KB articles and scripts

## 🏗️ Architecture

### Tech Stack

**Frontend:**
- React 18 + Vite
- TailwindCSS for styling
- React Router for navigation
- Radix UI components

**Backend:**
- Flask (Python) for REST API
- SQLite for data persistence
- JWT authentication
- OpenAI GPT-4 for AI capabilities

**AI/ML:**
- OpenAI Embeddings (text-embedding-3-small)
- FAISS for vector similarity search
- Classification and Generation agents
- RAG pipeline for knowledge retrieval

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                        │
│  - User Portal (Ticket Upload)                              │
│  - Agent Portal (Ticket Management & Knowledge Search)      │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST API
┌─────────────────────▼───────────────────────────────────────┐
│                   Backend (Flask)                            │
│  - Authentication (JWT)                                      │
│  - Ticket Management API                                     │
│  - RAG Search API                                            │
│  - Knowledge Base API                                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼──────┐ ┌───▼────┐ ┌─────▼──────────┐
│   Database   │ │   AI   │ │ Vector Store   │
│   (SQLite)   │ │ Agents │ │    (FAISS)     │
│              │ │        │ │                │
│ - Users      │ │ - Cls. │ │ - Embeddings   │
│ - Agents     │ │ - Gen. │ │ - Metadata     │
│ - Tickets    │ │        │ │ - Index        │
│ - Knowledge  │ │        │ │                │
└──────────────┘ └────────┘ └────────────────┘
```

## 📁 Project Structure

```
HackNation-Realstars/
├── realpage-ai-system/          # Frontend React application
│   ├── src/
│   │   ├── pages/               # Page components
│   │   │   ├── AgentPortal.jsx  # Agent dashboard
│   │   │   └── UserPortal.jsx   # User ticket submission
│   │   ├── components/          # Reusable UI components
│   │   └── services/            # API integration
│   └── package.json
│
├── backend/                     # Backend API and services
│   ├── scr/
│   │   ├── app.py              # Flask application entry point
│   │   ├── rag/                # RAG system components
│   │   │   ├── scripts/
│   │   │   │   ├── classification_agent.py
│   │   │   │   ├── generation_agent.py
│   │   │   │   └── enhanced_query.py    # RAG search logic
│   │   │   ├── db_scripts/     # Database utilities
│   │   │   └── vector_store/   # FAISS index and embeddings
│   │   └── utils/
│   └── databases/
│       ├── realpage.db         # Main application database
│       ├── knowledge_articles.db
│       └── scripts.db
│
├── README.md                    # This file
├── README_Backend.md            # Detailed backend documentation
└── requirements.txt
```

## 🚦 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 16+
- OpenAI API key
- Conda (optional, but recommended)

### Backend Setup

1. **Create and activate environment:**
```bash
conda create -n ai python=3.11
conda activate ai
```

2. **Install dependencies:**
```bash
pip install flask flask-cors PyJWT python-dotenv werkzeug
pip install openai pandas openpyxl chromadb tiktoken tqdm
```

3. **Set up environment variables:**
Create `.env` file in the project root:
```env
OPENAI_API_KEY=your-openai-key-here
SECRET_KEY=your-secret-key
```

4. **Run backend server:**
```bash
cd backend/scr
python app.py
```
Backend runs at: `http://localhost:5000`

### Frontend Setup

1. **Install dependencies:**
```bash
cd realpage-ai-system
npm install
```

2. **Configure API endpoint:**
Create `.env` file:
```env
VITE_API_BASE_URL=http://localhost:5000/api
```

3. **Run frontend:**
```bash
npm run dev
```
Frontend runs at: `http://localhost:5173`

## 📚 API Documentation

### Key Endpoints

#### Authentication
- `POST /api/auth/login` - User/Agent login
- `POST /api/auth/logout` - Logout

#### Tickets
- `POST /api/tickets/upload` - Upload tickets for AI processing
- `GET /api/tickets/pending` - Get pending tickets
- `GET /api/tickets/resolved` - Get resolved tickets
- `PATCH /api/tickets/{id}` - Update ticket status

#### RAG Search
- `GET /api/rag/search?q=query&top_k=5` - Semantic search across knowledge base

#### Knowledge Base
- `GET /api/knowledge` - List all knowledge articles
- `POST /api/knowledge` - Add new knowledge article
- `GET /api/knowledge/search?q=query` - Search knowledge base

See [README_Backend.md](README_Backend.md) for complete API documentation.

## 🎨 Features in Detail

### RAG-Powered Search
- **Semantic Understanding**: Searches by meaning, not just keywords
- **Auto-Summarization**: Long queries are automatically condensed
- **Relevance Scoring**: Results ranked by similarity (0-100%)
- **Rich Results**: Includes ticket details, resolutions, root causes, tags

### AI Agents
- **Classification Agent**: Categorizes tickets, assigns priority and tier
- **Generation Agent**: Creates resolution suggestions based on similar cases
- **Self-Learning**: System improves as more tickets are processed

### Agent Portal
- **Three-Panel Dashboard**: Resolved tickets, Knowledge search, Pending tickets
- **SLA Tracking**: Automatic breach detection (>3 days)
- **Ticket Management**: Approve, reject, or edit AI suggestions
- **Knowledge Articles**: View and reference approved solutions

## 🔐 Authentication

Default test accounts:
- **Agents**: agent1@realpage.com, agent2@realpage.com, agent3@realpage.com
- **Password Pattern**: password1, password2, password3

## 📊 Database Schema

- **realpage_user**: End users who submit tickets
- **support_agent**: Support agents (Tier 1/2/3)
- **ticket**: Support tickets with AI resolutions
- **new_knowledge**: Approved resolutions added to knowledge base

## 🛠️ Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd realpage-ai-system
npm test
```

### Building for Production
```bash
# Frontend build
cd realpage-ai-system
npm run build

# Backend (uses Flask in production mode)
cd backend/scr
flask run --host=0.0.0.0 --port=5000
```

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📝 License

This project is part of the HackNation hackathon submission.

## 🙏 Acknowledgments

- Built for RealPage HackNation challenge
- Powered by OpenAI GPT-4 and Embeddings
- FAISS for vector similarity search

---

**Team:** HackNation-Realstars
**Event:** HackNation 2026
**Category:** AI-Powered Customer Support
