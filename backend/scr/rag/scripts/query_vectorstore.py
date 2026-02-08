import os
import sys
import numpy as np
import faiss
import pickle
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def query_vectorstore(query_text, top_k=5):
    """Query the vector store and return the most similar documents."""

    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    client = OpenAI(api_key=api_key)

    # Load the FAISS index
    index_path = "vector_store/faiss_index.bin"
    index = faiss.read_index(index_path)
    print(f"Loaded index with {index.ntotal} vectors")

    # Load metadata
    metadata_path = "vector_store/metadata.pkl"
    with open(metadata_path, 'rb') as f:
        metadata = pickle.load(f)

    # Create embedding for query
    print(f"Creating embedding for query: '{query_text}'")
    response = client.embeddings.create(
        input=[query_text],
        model=metadata['model']
    )
    query_embedding = np.array([response.data[0].embedding], dtype=np.float32)

    # Search the index
    distances, indices = index.search(query_embedding, top_k)

    # Display results
    print(f"\n{'='*80}")
    print(f"Top {top_k} results for: '{query_text}'")
    print(f"{'='*80}\n")

    results = []
    for i, (idx, distance) in enumerate(zip(indices[0], distances[0])):
        print(f"Result {i+1} (Distance: {distance:.4f})")
        print("-" * 80)

        # Get the original data
        doc_data = metadata['dataframe'][idx]
        text = metadata['texts'][idx]

        # Display key information
        if doc_data.get('Ticket_Number'):
            print(f"Ticket: {doc_data['Ticket_Number']}")
        if doc_data.get('Product_x'):
            print(f"Product: {doc_data['Product_x']}")
        if doc_data.get('Category_x'):
            print(f"Category: {doc_data['Category_x']}")
        if doc_data.get('Issue_Summary'):
            print(f"Issue: {doc_data['Issue_Summary']}")
        if doc_data.get('Resolution'):
            print(f"Resolution: {doc_data['Resolution'][:200]}...")

        print()

        results.append({
            'index': int(idx),
            'distance': float(distance),
            'data': doc_data,
            'text': text
        })

    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python query_vectorstore.py 'your query here' [top_k]")
        print("\nExample: python query_vectorstore.py 'login issues' 5")
        sys.exit(1)

    query = sys.argv[1]
    top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    results = query_vectorstore(query, top_k)

if __name__ == "__main__":
    main()
