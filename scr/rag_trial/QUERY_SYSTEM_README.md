# Support Ticket Query System - Documentation

## Overview
This system provides intelligent search and retrieval over your support ticket database using OpenAI embeddings and FAISS vector search.

## Embedding Model
**Model Used:** `text-embedding-3-small`
- **Dimension:** 1536
- **Provider:** OpenAI
- **Performance:** Fast and cost-effective for semantic search

## Features

### 1. Automatic Query Summarization
- **Threshold:** 15 words
- **Behavior:** Queries exceeding 15 words are automatically summarized using GPT-4o-mini
- **Format:** Converted to structured "Subject + Description" format for optimal search results

### 2. Comprehensive Output Fields
Each search result includes the following fields:

| Field | Source | Description |
|-------|--------|-------------|
| Issue Summary | Original Data | Question/Transcript summary |
| Description | Original Data | Full transcript/question case |
| Subject | Original Data | Extracted subject from transcript |
| Category | RAG | Issue category |
| Module | RAG | System module affected |
| Priority | RAG + LLM | Ticket priority level |
| Tier | RAG + LLM | Support tier required |
| Answer Type | RAG | Script, KB, or Ticket resolution |
| Resolution | Original Data | Full resolution steps |
| Root Cause | Original Data | Identified root cause |
| Tags | Original Data | Generated knowledge base tags |
| Ticket Number | Original Data | Unique ticket identifier |
| Full Transcript | Original Data | Complete conversation transcript |

### 3. Full Output Display
- **No truncation:** All fields are displayed in full
- **Clear formatting:** Section separators for easy reading
- **Similarity scores:** Distance metrics and normalized scores

## Usage

### Option 1: Command-Line Query
```bash
python scripts/enhanced_query.py "your query here" [number_of_results]
```

**Examples:**
```bash
# Short query (≤15 words)
python scripts/enhanced_query.py "login issue" 3

# Long query (>15 words - will be auto-summarized)
python scripts/enhanced_query.py "I am having trouble with the date advance feature in PropertySuite Affordable and I keep getting an error message that says there is a backend voucher reference that is invalid" 5
```

### Option 2: Interactive Mode
```bash
python scripts/interactive_query.py
```

This starts an interactive session where you can:
- Enter multiple queries without restarting
- Specify number of results per query
- Exit with 'quit' or Ctrl+C

## Query Processing Flow

```
User Input (Query)
    ↓
Word Count Check
    ↓
    ├─ ≤15 words → Use as-is
    ↓
    └─ >15 words → Summarize with GPT-4o-mini
                   ↓
                   Create "Subject + Description" format
    ↓
Create Embedding (text-embedding-3-small)
    ↓
FAISS Vector Search
    ↓
Return Top K Results (with full details)
```

## Vector Store Information

- **Total Documents:** 722 support tickets
- **Index Size:** 4.23 MB
- **Metadata Size:** 1.53 MB
- **Storage Location:** `vector_store/`
- **Files:**
  - `faiss_index.bin` - FAISS vector index
  - `metadata.pkl` - Document metadata and original data

## Data Statistics

### Product Distribution
- ExampleCo PropertySuite Affordable: 722 tickets

### Top Categories
1. Advance Property Date: 352 tickets
2. General: 138 tickets
3. Certifications: 78 tickets
4. HAP / Voucher Processing: 57 tickets
5. TRACS File: 21 tickets

### Sentiment Distribution
- Neutral: 262 tickets
- Relieved: 238 tickets
- Frustrated: 144 tickets
- Curious: 78 tickets

### Priority Distribution
- Medium: 256 tickets
- High: 249 tickets
- Critical: 150 tickets
- Low: 67 tickets

### Answer Types
- SEED_KB: 474 tickets
- Script: 161 tickets
- Mixed: 87 tickets

## Example Output

When you run a query, you'll see output like this:

```
====================================================================================================
ORIGINAL QUERY (Word Count: 44)
====================================================================================================
I am having trouble with the date advance feature...

====================================================================================================
QUERY EXCEEDS 15 WORDS - CREATING SUMMARIZED SEARCH QUERY
====================================================================================================

Subject: Issue with Date Advance Feature in PropertySuite
Description: Customer encounters an error regarding an invalid backend voucher reference...

====================================================================================================
EMBEDDING MODEL: text-embedding-3-small
====================================================================================================

====================================================================================================
RETRIEVAL RESULTS - TOP 2 MATCHES
====================================================================================================

####################################################################################################
RESULT 1 - SIMILARITY SCORE: 0.7452 (Distance: 0.3418)
####################################################################################################

────────────────────────────────────────────────────────────────────────────────────────────────────
ISSUE SUMMARY (Question/Transcript Summary)
────────────────────────────────────────────────────────────────────────────────────────────────────
Date advance fails because a backend voucher reference is invalid...

[... Full details for each field ...]
```

## Re-ingesting Data

If you need to update the vector store with new data:

```bash
python scripts/ingest_data.py
```

This will:
1. Read the Excel file from `data/final_ver3.xlsx`
2. Create embeddings for all records
3. Rebuild the FAISS index
4. Save updated metadata

## Conda Environment

Make sure you're using the correct environment:

```bash
# Activate the ai environment
conda activate ai

# Verify Python path
which python3
# Should show: /Users/siddhart.tayi/miniconda3/envs/ai/bin/python3
```

## Troubleshooting

### "OPENAI_API_KEY not found"
- Check that `.env` file exists in the project root
- Verify the key is uncommented and valid

### "Vector store not found"
- Run `python scripts/ingest_data.py` first to create the vector store

### Low similarity scores
- Try rephrasing your query
- Use more specific terms from the domain
- For long queries, let the system auto-summarize (>15 words)

## Files Created

1. **scripts/ingest_data.py** - Initial data ingestion
2. **scripts/enhanced_query.py** - Command-line query interface
3. **scripts/interactive_query.py** - Interactive query mode
4. **scripts/query_vectorstore.py** - Original simple query script
5. **scripts/vectorstore_info.py** - Display vector store statistics

## Performance

- **Query time:** ~1-2 seconds per query (including embedding creation)
- **Embedding creation:** ~4 minutes for 722 documents (batch processing)
- **Memory usage:** ~10-20 MB for loaded index
