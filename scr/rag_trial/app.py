"""
Root entry point for Streamlit UI
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the Streamlit app
from src.ui.app import main

if __name__ == "__main__":
    main()
