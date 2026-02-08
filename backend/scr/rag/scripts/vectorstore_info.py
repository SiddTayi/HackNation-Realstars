import os
import faiss
import pickle
from collections import Counter

def show_vectorstore_info():
    """Display information about the vector store."""

    # Load the FAISS index
    index_path = "vector_store/faiss_index.bin"
    if not os.path.exists(index_path):
        print("Vector store not found. Run ingest_data.py first.")
        return

    index = faiss.read_index(index_path)

    # Load metadata
    metadata_path = "vector_store/metadata.pkl"
    with open(metadata_path, 'rb') as f:
        metadata = pickle.load(f)

    print("=" * 80)
    print("VECTOR STORE INFORMATION")
    print("=" * 80)
    print(f"\nModel: {metadata['model']}")
    print(f"Embedding Dimension: {metadata['dimension']}")
    print(f"Total Documents: {metadata['total_vectors']}")
    print(f"Index Size: {os.path.getsize(index_path) / (1024*1024):.2f} MB")
    print(f"Metadata Size: {os.path.getsize(metadata_path) / (1024*1024):.2f} MB")

    # Analyze the data
    df_records = metadata['dataframe']

    print("\n" + "=" * 80)
    print("DATA STATISTICS")
    print("=" * 80)

    # Product distribution
    products = [r.get('Product_x') for r in df_records if r.get('Product_x')]
    if products:
        print(f"\nTop 5 Products:")
        for product, count in Counter(products).most_common(5):
            print(f"  - {product}: {count}")

    # Category distribution
    categories = [r.get('Category_x') for r in df_records if r.get('Category_x')]
    if categories:
        print(f"\nTop 5 Categories:")
        for category, count in Counter(categories).most_common(5):
            print(f"  - {category}: {count}")

    # Sentiment distribution
    sentiments = [r.get('Sentiment') for r in df_records if r.get('Sentiment')]
    if sentiments:
        print(f"\nSentiment Distribution:")
        for sentiment, count in Counter(sentiments).most_common():
            print(f"  - {sentiment}: {count}")

    # Priority distribution
    priorities = [r.get('Priority') for r in df_records if r.get('Priority')]
    if priorities:
        print(f"\nPriority Distribution:")
        for priority, count in Counter(priorities).most_common():
            print(f"  - {priority}: {count}")

    # Answer type distribution
    answer_types = [r.get('Answer_Type') for r in df_records if r.get('Answer_Type')]
    if answer_types:
        print(f"\nAnswer Type Distribution:")
        for answer_type, count in Counter(answer_types).most_common():
            print(f"  - {answer_type}: {count}")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    show_vectorstore_info()
