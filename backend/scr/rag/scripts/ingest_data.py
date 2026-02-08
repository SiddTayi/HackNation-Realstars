import os
import sys
import pandas as pd
import numpy as np
import faiss
import pickle
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_text_from_row(row):
    """Create a comprehensive text representation from each row for embedding."""
    parts = []

    # Add ticket information
    if pd.notna(row.get('Ticket_Number')):
        parts.append(f"Ticket: {row['Ticket_Number']}")

    # Add product and category
    if pd.notna(row.get('Product_x')):
        parts.append(f"Product: {row['Product_x']}")
    if pd.notna(row.get('Category_x')):
        parts.append(f"Category: {row['Category_x']}")

    # Add issue summary (most important)
    if pd.notna(row.get('Issue_Summary')):
        parts.append(f"Issue: {row['Issue_Summary']}")

    # Add subject
    if pd.notna(row.get('Subject')):
        parts.append(f"Subject: {row['Subject']}")

    # Add description
    if pd.notna(row.get('Description')):
        parts.append(f"Description: {row['Description']}")

    # Add resolution
    if pd.notna(row.get('Resolution')):
        parts.append(f"Resolution: {row['Resolution']}")

    # Add root cause
    if pd.notna(row.get('Root_Cause')):
        parts.append(f"Root Cause: {row['Root_Cause']}")

    # Add tags
    if pd.notna(row.get('Tags_generated_kb')):
        parts.append(f"Tags: {row['Tags_generated_kb']}")

    return "\n".join(parts)

def create_embeddings_batch(texts, client, model="text-embedding-3-small", batch_size=100):
    """Create embeddings in batches to handle API rate limits."""
    all_embeddings = []

    for i in tqdm(range(0, len(texts), batch_size), desc="Creating embeddings"):
        batch = texts[i:i+batch_size]
        try:
            response = client.embeddings.create(
                input=batch,
                model=model
            )
            embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(embeddings)
        except Exception as e:
            print(f"Error processing batch {i//batch_size}: {e}")
            raise

    return np.array(all_embeddings, dtype=np.float32)

def main():
    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    client = OpenAI(api_key=api_key)

    # Load the Excel file
    print("Loading Excel file...")
    data_path = "data/final_ver3.xlsx"
    df = pd.read_excel(data_path)
    print(f"Loaded {len(df)} rows")

    # Create text representations
    print("Creating text representations...")
    texts = []
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
        text = create_text_from_row(row)
        texts.append(text)

    # Create embeddings
    print(f"Creating embeddings using OpenAI...")
    embeddings = create_embeddings_batch(texts, client)
    print(f"Created {len(embeddings)} embeddings with dimension {embeddings.shape[1]}")

    # Create FAISS index
    print("Creating FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    print(f"Added {index.ntotal} vectors to index")

    # Save the index
    vector_store_path = "vector_store"
    os.makedirs(vector_store_path, exist_ok=True)

    index_path = os.path.join(vector_store_path, "faiss_index.bin")
    faiss.write_index(index, index_path)
    print(f"Saved FAISS index to {index_path}")

    # Save metadata
    metadata = {
        'texts': texts,
        'dataframe': df.to_dict('records'),
        'model': 'text-embedding-3-small',
        'dimension': dimension,
        'total_vectors': len(embeddings)
    }

    metadata_path = os.path.join(vector_store_path, "metadata.pkl")
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"Saved metadata to {metadata_path}")

    print("\n✓ Ingestion complete!")
    print(f"  - Total documents: {len(texts)}")
    print(f"  - Embedding dimension: {dimension}")
    print(f"  - Index file: {index_path}")
    print(f"  - Metadata file: {metadata_path}")

if __name__ == "__main__":
    main()
