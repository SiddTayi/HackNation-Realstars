# Project Structure Overview

## 📁 Production-Ready Organization

```
hackathon/
│
├── 📄 Root Files
│   ├── app.py                    # Streamlit UI entry point
│   ├── main.py                   # CLI entry point
│   ├── README.md                 # Main documentation
│   ├── LICENSE                   # MIT License
│   ├── requirements.txt          # Python dependencies
│   ├── pyproject.toml            # Package configuration
│   ├── .gitignore               # Git ignore rules
│   └── .env                     # Environment variables (create this)
│
├── 📦 src/                      # Source code
│   ├── __init__.py
│   ├── config.py                # Central configuration
│   ├── main.py                  # CLI application logic
│   │
│   ├── rag/                     # RAG Module
│   │   ├── __init__.py
│   │   ├── ingest.py            # Data ingestion & embedding
│   │   ├── retrieval.py         # FAISS vector search
│   │   ├── rag_pipeline.py      # RAG pipeline with memory
│   │   └── chatbot.py           # CLI chatbot interface
│   │
│   └── ui/                      # UI Components
│       ├── __init__.py
│       └── app.py               # Streamlit application
│
├── 🔧 scripts/                  # Utility Scripts
│   ├── setup.sh                 # Initial setup
│   ├── run_app.sh               # Launch Streamlit
│   └── create_sample_data.py    # Generate sample Excel
│
├── ⚙️  config/                  # Configuration Files
│   └── .env.example             # Environment template
│
├── 📊 data/                     # Data Directory
│   ├── .gitkeep                 # Keep directory in git
│   └── source.xlsx              # Your Excel file (after setup)
│
├── 📚 docs/                     # Documentation
│   ├── README.md                # Detailed documentation
│   └── USAGE.md                 # Usage guide
│
├── 🧪 tests/                    # Test Suite
│   ├── __init__.py
│   └── test_sample.py           # Sample tests
│
├── 🎨 .streamlit/               # Streamlit Config
│   └── config.toml              # UI theme settings
│
└── 🗄️  vector_store/            # Generated (not in git)
    ├── faiss_index.bin          # FAISS index
    └── metadata.parquet         # Chunk metadata
```

## 🎯 Key Design Principles

### 1. **Separation of Concerns**
- `src/rag/` - Core RAG functionality
- `src/ui/` - User interface components
- `scripts/` - Utility and setup scripts
- `config/` - Configuration files
- `tests/` - Test suite

### 2. **Clean Imports**
All imports use absolute paths from `src`:
```python
from src.rag.ingest import ingest
from src.config import CONFIG
from src.rag.rag_pipeline import RAGPipeline
```

### 3. **Entry Points**
- **Root `app.py`** - Streamlit UI entry (imports from `src.ui.app`)
- **Root `main.py`** - CLI entry (imports from `src.main`)

### 4. **Configuration**
- Single source of truth: `src/config.py`
- Environment variables: `.env` file
- Streamlit settings: `.streamlit/config.toml`

### 5. **Gitignore Strategy**
Excluded from git:
- `__pycache__/` - Python cache
- `.env` - Secrets
- `data/*.xlsx` - Data files (use .gitkeep)
- `vector_store/` - Generated indices
- Virtual environments

## 🚀 Quick Commands

### Setup
```bash
bash scripts/setup.sh          # Install & configure
```

### Run Application
```bash
streamlit run app.py           # Streamlit UI
python main.py chat            # CLI chat
python main.py ingest          # Ingest data
python main.py query "text"    # Single query
```

### Development
```bash
pytest tests/                  # Run tests
pytest --cov=src tests/        # With coverage
black src/                     # Format code
flake8 src/                    # Lint code
mypy src/                      # Type checking
```

### Helper Scripts
```bash
bash scripts/run_app.sh        # Launch Streamlit
python scripts/create_sample_data.py  # Generate sample data
```

## 📦 Package Structure

The project is configured as a proper Python package:
- `pyproject.toml` - Modern Python packaging
- Proper `__init__.py` files in all packages
- Absolute imports for reliability
- Development dependencies included

## 🔄 Migration from Old Structure

### Old Structure
```
hackathon/
├── config.py
├── main.py
├── app.py
├── rag/
│   ├── ingest.py
│   ├── retrieval.py
│   ├── rag_pipeline.py
│   └── chatbot.py
└── create_sample_data.py
```

### New Structure (Production)
```
hackathon/
├── app.py (root entry)
├── main.py (root entry)
├── src/
│   ├── config.py
│   ├── main.py
│   ├── rag/
│   │   └── [all rag files]
│   └── ui/
│       └── app.py
├── scripts/
│   └── create_sample_data.py
├── tests/
├── docs/
└── config/
```

## ✅ Production Standards Met

- ✅ Proper package structure
- ✅ Separated source code (`src/`)
- ✅ Configuration management
- ✅ Test directory structure
- ✅ Documentation organization
- ✅ Clean imports (absolute paths)
- ✅ Git ignore properly configured
- ✅ License file included
- ✅ Package metadata (`pyproject.toml`)
- ✅ Helper scripts organized
- ✅ Development dependencies

## 🎓 Best Practices Implemented

1. **Single Responsibility** - Each module has one clear purpose
2. **DRY (Don't Repeat Yourself)** - Shared code in `src/`
3. **Configuration as Code** - Centralized in `src/config.py`
4. **Environment Variables** - Secrets in `.env`
5. **Documentation** - README, USAGE, and code comments
6. **Testing** - Test structure ready for expansion
7. **Version Control** - Proper `.gitignore`
8. **Licensing** - MIT License included

## 📝 Next Steps

1. **Add your data**: Place Excel file in `data/`
2. **Configure**: Copy `config/.env.example` to `.env`
3. **Install**: Run `bash scripts/setup.sh`
4. **Ingest**: Run `python main.py ingest`
5. **Use**: Run `streamlit run app.py`

## 🤝 Contributing

Follow the established structure when adding new features:
- New RAG features → `src/rag/`
- UI components → `src/ui/`
- Utilities → `scripts/`
- Tests → `tests/`
- Docs → `docs/`
