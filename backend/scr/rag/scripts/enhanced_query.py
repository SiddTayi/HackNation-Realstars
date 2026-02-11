import os
import sys
import numpy as np
import faiss
import pickle
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def summarize_query(client, query_text):
    """Use OpenAI to summarize long queries into Subject and Description format."""

    prompt = f"""Given the following customer question or transcript, create a concise search query for a support ticket database.

Format your response as:
Subject: [Brief subject line, 5-10 words]
Description: [Detailed description of the issue, 15-25 words]

Input: {query_text}

Output:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that creates searchable query formats for a support ticket database."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=150
    )

    summary = response.choices[0].message.content.strip()

    # Parse Subject and Description
    lines = summary.split('\n')
    subject = ""
    description = ""

    for line in lines:
        if line.startswith('Subject:'):
            subject = line.replace('Subject:', '').strip()
        elif line.startswith('Description:'):
            description = line.replace('Description:', '').strip()

    return subject, description, summary

def query_vectorstore(query_text, top_k=3):
    """Query the vector store and return comprehensive results."""

    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    client = OpenAI(api_key=api_key)

    # Count words in query
    word_count = len(query_text.split())

    print(f"\n{'='*100}")
    print(f"ORIGINAL QUERY (Word Count: {word_count})")
    print(f"{'='*100}")
    print(f"{query_text}\n")

    # If query is longer than 15 words, summarize it
    search_query = query_text
    if word_count > 15:
        print(f"{'='*100}")
        print(f"QUERY EXCEEDS 15 WORDS - CREATING SUMMARIZED SEARCH QUERY")
        print(f"{'='*100}")
        subject, description, full_summary = summarize_query(client, query_text)
        print(f"\n{full_summary}\n")

        # Combine subject and description for search
        search_query = f"{subject}\n{description}"
        print(f"Search Query for Vector DB:")
        print(f"{search_query}\n")

    # Load the FAISS index
    # Use absolute path based on script location
    script_dir = Path(__file__).parent.parent  # Go up to rag/ directory
    index_path = script_dir / "vector_store" / "faiss_index.bin"
    index = faiss.read_index(str(index_path))

    # Load metadata
    metadata_path = script_dir / "vector_store" / "metadata.pkl"
    with open(metadata_path, 'rb') as f:
        metadata = pickle.load(f)

    print(f"{'='*100}")
    print(f"EMBEDDING MODEL: {metadata['model']}")
    print(f"{'='*100}\n")

    # Create embedding for search query
    response = client.embeddings.create(
        input=[search_query],
        model=metadata['model']
    )
    query_embedding = np.array([response.data[0].embedding], dtype=np.float32)

    # Search the index
    distances, indices = index.search(query_embedding, top_k)

    # Display results
    print(f"{'='*100}")
    print(f"RETRIEVAL RESULTS - TOP {top_k} MATCHES")
    print(f"{'='*100}\n")

    results = []
    for i, (idx, distance) in enumerate(zip(indices[0], distances[0])):
        doc_data = metadata['dataframe'][idx]

        print(f"\n{'#'*100}")
        print(f"RESULT {i+1} - SIMILARITY SCORE: {1 / (1 + distance):.4f} (Distance: {distance:.4f})")
        print(f"{'#'*100}\n")

        # Output fields as requested
        print(f"{'─'*100}")
        print(f"ISSUE SUMMARY (Question/Transcript Summary)")
        print(f"{'─'*100}")
        print(f"{doc_data.get('Issue_Summary', 'N/A')}\n")

        print(f"{'─'*100}")
        print(f"DESCRIPTION (Transcript/Question Case)")
        print(f"{'─'*100}")
        print(f"{doc_data.get('Description', 'N/A')}\n")

        print(f"{'─'*100}")
        print(f"SUBJECT (Transcript)")
        print(f"{'─'*100}")
        print(f"{doc_data.get('Subject', 'N/A')}\n")

        print(f"{'─'*100}")
        print(f"CATEGORY (RAG)")
        print(f"{'─'*100}")
        print(f"{doc_data.get('Category_x', 'N/A')}\n")

        print(f"{'─'*100}")
        print(f"MODULE (RAG)")
        print(f"{'─'*100}")
        print(f"{doc_data.get('Module_generated_kb', 'N/A')}\n")

        print(f"{'─'*100}")
        print(f"PRIORITY (RAG + LLM)")
        print(f"{'─'*100}")
        print(f"{doc_data.get('Priority', 'N/A')}\n")

        print(f"{'─'*100}")
        print(f"TIER (RAG + LLM)")
        print(f"{'─'*100}")
        print(f"{doc_data.get('Tier', 'N/A')}\n")

        print(f"{'─'*100}")
        print(f"ANSWER TYPE (RAG)")
        print(f"{'─'*100}")
        print(f"{doc_data.get('Answer_Type', 'N/A')}\n")

        print(f"{'─'*100}")
        print(f"RESOLUTION")
        print(f"{'─'*100}")
        print(f"{doc_data.get('Resolution', 'N/A')}\n")

        print(f"{'─'*100}")
        print(f"ROOT CAUSE")
        print(f"{'─'*100}")
        print(f"{doc_data.get('Root_Cause', 'N/A')}\n")

        print(f"{'─'*100}")
        print(f"TAGS")
        print(f"{'─'*100}")
        print(f"{doc_data.get('Tags_generated_kb', 'N/A')}\n")

        print(f"{'─'*100}")
        print(f"TICKET NUMBER")
        print(f"{'─'*100}")
        print(f"{doc_data.get('Ticket_Number', 'N/A')}\n")

        print(f"{'─'*100}")
        print(f"FULL TRANSCRIPT")
        print(f"{'─'*100}")
        print(f"{doc_data.get('Transcript', 'N/A')}\n")

        results.append({
            'index': int(idx),
            'distance': float(distance),
            'similarity_score': float(1 / (1 + distance)),
            'data': doc_data
        })

    print(f"\n{'='*100}")
    print(f"END OF RESULTS")
    print(f"{'='*100}\n")

    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python enhanced_query.py 'your query here' [top_k]")
        print("\nExample: python enhanced_query.py 'I am having trouble logging into my account and cannot reset my password' 3")
        sys.exit(1)

    query = sys.argv[1]
    top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    results = query_vectorstore(query, top_k)

if __name__ == "__main__":
    main()
