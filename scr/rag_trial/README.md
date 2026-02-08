# 🎧 Support Case Assistant

AI-powered assistant for support agents to search historical case data and find solutions faster.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Quick Start

```bash
# 1. Setup
conda activate ai
cp config/.env.example .env
# Edit .env: Add OPENAI_API_KEY

# 2. Ingest data (one-time, ~5-10 min for 65K cases)
python main.py ingest

# 3. Launch
streamlit run app.py
```

**Done!** Open `http://localhost:8501`

---

## What It Does

- 🔍 **Search 65K+ cases** instantly by meaning, not just keywords
- ⚡ **Find solutions fast** - similar cases with resolutions in seconds
- 📋 **Cite sources** - always shows real case numbers and KB articles
- 💬 **Contextual chat** - remembers conversation for follow-ups

### Example Query
```
Agent: "Customer can't reset password, not receiving email"

AI: Found 3 similar cases:
- Case #12345: Email in spam folder → Resolution: Whitelist sender
- Case #23456: Server delay → Resolution: Manually triggered
- Case #34567: Wrong email → Resolution: Updated customer email
```

---

## Features

- ✅ Semantic search with FAISS vector store
- ✅ Session-based conversation memory
- ✅ Configured for Salesforce case data
- ✅ Streamlit web UI + CLI mode
- ✅ OpenAI GPT-powered answers
- ✅ Production-ready structure

---

## Data Configuration

**Configured columns** (auto-extracted from Excel):
- CaseNumber, Subject, ArticleTitle
- casedescription, CaseResolution
- CasesStatus, CaseOrigin, KnowledgeArticleId

**Your data:** `data/sfdc_casedata.xlsx` (65,535 cases) ✅

---

## Usage

### Daily Use
```bash
streamlit run app.py    # Web UI (recommended)
python main.py chat     # CLI mode
```

### Maintenance
```bash
python main.py ingest   # Re-run when adding new cases
```

### Test Query
```bash
python main.py query "show me login issue cases"
```

---

## Project Structure

```
hackathon/
├── app.py                    # Streamlit UI entry
├── main.py                   # CLI entry
├── src/                      # Source code
│   ├── config.py            # Configuration
│   ├── rag/                 # RAG pipeline
│   │   ├── ingest.py        # Data ingestion
│   │   ├── retrieval.py     # Vector search
│   │   └── rag_pipeline.py  # RAG + memory
│   └── ui/                  # UI components
├── data/                     # Data directory
│   └── sfdc_casedata.xlsx   # Your case data
├── scripts/                  # Utility scripts
├── tests/                    # Test suite
└── docs/                     # Documentation
```

---

## Requirements

- Python 3.9+
- OpenAI API key
- Conda environment `ai` (activated)

**Key packages:** pandas, faiss-cpu, sentence-transformers, openai, streamlit

See `requirements.txt` for full list.

---

## How It Works

```
Excel Data → Chunks → Embeddings → FAISS Index
                                        ↓
User Query → Vector Search → Top 7 Cases → OpenAI → Answer
```

**One-time:** Build searchable database with `python main.py ingest`
**Daily:** Query the database with `streamlit run app.py`

---

## Configuration

Edit `src/config.py` to customize:

```python
chunk_size = 1200          # Text chunk size
top_k = 7                  # Similar cases to retrieve
temperature = 0.1          # Response creativity (low=factual)
```

---

## Documentation

- **Quick Start:** [QUICKSTART.md](QUICKSTART.md) - Get up and running in 3 steps
- **Full Guide:** [docs/GUIDE.md](docs/GUIDE.md) - Complete documentation
- **Structure:** [STRUCTURE.md](STRUCTURE.md) - Code organization

---

## Troubleshooting

**"Vector store not found"**
→ Run `python main.py ingest` first

**"Column not found"**
→ Check Excel has required columns (already configured for your file)

**"OpenAI API error"**
→ Verify `.env` has valid API key

---

## Support

For issues or questions:
1. Check [docs/GUIDE.md](docs/GUIDE.md)
2. Review [QUICKSTART.md](QUICKSTART.md)
3. Check configuration in `src/config.py`

---

## License

MIT License - see [LICENSE](LICENSE) file

---

**Status:** ✅ Production Ready | **Cases:** 65,535 | **Configured:** ✅
