#!/bin/bash

echo "🚀 Setting up Excel RAG Application..."
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file..."
    cp config/.env.example .env
    echo "⚠️  Please edit .env and add your OPENAI_API_KEY"
fi

# Create sample data
echo ""
echo "📊 Creating sample Excel data..."
python scripts/create_sample_data.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your OPENAI_API_KEY"
echo "  2. Run: python main.py ingest"
echo "  3. Run: streamlit run app.py (for UI)"
echo "  4. Or run: python main.py chat (for CLI)"
echo ""
