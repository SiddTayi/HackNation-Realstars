#!/bin/bash

cd "$(dirname "$0")/.."

echo "🚀 Starting Excel RAG Chatbot UI..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create a .env file with your OPENAI_API_KEY"
    echo ""
fi

# Check if vector store exists
if [ ! -d "vector_store" ] || [ ! -f "vector_store/faiss_index.bin" ]; then
    echo "ℹ️  Vector store not found. You can ingest data from the UI."
    echo ""
fi

# Run Streamlit app
streamlit run app.py
