"""
Classification Agent for RAG System
Uses FAISS vector store and LLM-as-judge for relevancy scoring
"""

from db_scripts.db_ticket import last_row_db
import os
import sys
import json
import numpy as np
import faiss
import pickle
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Add parent directory to path for db_scripts import
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()


class ClassificationAgent:
    """
    Agent for classifying and scoring support ticket relevancy using LLM-as-judge.
    """

    def __init__(self, vector_store_path="vector_store"):
        """
        Initialize the classification agent.

        Args:
            vector_store_path: Path to the FAISS vector store directory
        """
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=self.api_key)
        self.vector_store_path = Path(
            __file__).parent.parent / vector_store_path

        # Load FAISS index and metadata
        self._load_vector_store()

    def _load_vector_store(self):
        """Load the FAISS index and metadata."""
        # Resolve vector_store_path relative to script location
        if not Path(self.vector_store_path).is_absolute():
            # Go to rag_trial directory
            base_path = Path(__file__).parent.parent
            self.vector_store_path = base_path / self.vector_store_path

        index_path = self.vector_store_path / "faiss_index.bin"
        metadata_path = self.vector_store_path / "metadata.pkl"

        if not index_path.exists():
            raise FileNotFoundError(f"FAISS index not found at {index_path}")
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found at {metadata_path}")

        self.index = faiss.read_index(str(index_path))

        with open(metadata_path, 'rb') as f:
            self.metadata = pickle.load(f)

        print(f"✓ Loaded vector store with {self.index.ntotal} documents")
        print(
            f"✓ Using model: {self.metadata.get('model', 'text-embedding-3-small')}")

    def _create_query_embedding(self, query_text):
        """Create embedding for the query text."""
        response = self.client.embeddings.create(
            input=[query_text],
            model=self.metadata.get('model', 'text-embedding-3-small')
        )
        return np.array([response.data[0].embedding], dtype=np.float32)

    def _retrieve_similar_documents(self, query_text, top_k=5):
        """Retrieve the most similar documents from the vector store."""
        query_embedding = self._create_query_embedding(query_text)
        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            doc_data = self.metadata['dataframe'][idx]
            text = self.metadata['texts'][idx]

            results.append({
                'index': int(idx),
                'distance': float(distance),
                # Convert distance to similarity
                'similarity_score': 1 / (1 + float(distance)),
                'data': doc_data,
                'text': text
            })

        return results

    def _generate_llm_response(self, query, retrieved_docs):
        """
        Generate a response using LLM based on retrieved context.

        Args:
            query: User query
            retrieved_docs: List of retrieved documents

        Returns:
            Generated response text
        """
        # Build context from retrieved documents
        context_parts = []
        # Use top 3 for context
        for i, doc in enumerate(retrieved_docs[:3], 1):
            data = doc['data']
            context_parts.append(f"""
Document {i}:
- Ticket: {data.get('Ticket_Number', 'N/A')}
- Issue: {data.get('Issue_Summary', 'N/A')}
- Resolution: {data.get('Resolution', 'N/A')}
- Category: {data.get('Category_x', 'N/A')}
""")

        context = "\n".join(context_parts)

        # Create prompt for LLM
        system_prompt = """You are a support expert helping to answer customer queries based on historical support tickets.
Use the provided context to generate a helpful, accurate response to the user's query."""

        user_prompt = f"""Query: {query}

Context from similar support tickets:
{context}

Based on the above context, provide a clear and helpful response to the query."""

        # Generate response
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )

        return response.choices[0].message.content

    def _calculate_relevancy_score(self, query, generated_response, resolution):
        """
        Calculate relevancy score using LLM-as-judge.

        Compares the generated response against the query and actual resolution
        to determine how relevant and accurate the response is.

        Args:
            query: Original user query
            generated_response: LLM-generated response
            resolution: Actual resolution from the ticket

        Returns:
            Dictionary with score (0-100) and reasoning
        """
        judge_prompt = f"""You are an expert judge evaluating the quality and relevancy of a generated support response.

USER QUERY: {query}

GENERATED RESPONSE: {generated_response}

ACTUAL RESOLUTION: {resolution}

Please evaluate the generated response on these criteria:
1. Relevancy: How well does it address the user's query? (0-40 points)
2. Accuracy: How closely does it match the actual resolution? (0-40 points)
3. Completeness: Does it provide actionable information? (0-20 points)

Provide your evaluation as a JSON object with:
- "score": Total score (0-100)
- "relevancy_points": Score for relevancy (0-40)
- "accuracy_points": Score for accuracy (0-40)
- "completeness_points": Score for completeness (0-20)
- "reasoning": Brief explanation of the score

Respond ONLY with the JSON object, no other text."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert evaluator. Respond only with valid JSON."},
                {"role": "user", "content": judge_prompt}
            ],
            temperature=0.1,
            max_tokens=300
        )

        try:
            result = json.loads(response.choices[0].message.content)
            return result
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "score": 50,
                "relevancy_points": 20,
                "accuracy_points": 20,
                "completeness_points": 10,
                "reasoning": "Unable to parse judge response"
            }

    def _format_output(self, query, retrieved_doc, generated_response, relevancy_result, new_ticket_id):
        """
        Format the output in the specified structure.

        Args:
            query: Original query
            retrieved_doc: Retrieved document data
            generated_response: LLM-generated response
            relevancy_result: Relevancy scoring result
            new_ticket_id: Newly generated ticket ID from last_row_db()

        Returns:
            Formatted dictionary
        """
        data = retrieved_doc['data']

        # Extract KB/Script content
        kb_content = data.get('KB_Article_ID_x', 'N/A')
        script_content = data.get('Script_ID', 'N/A')

        # Determine content type and value
        if kb_content and kb_content != 'N/A' and str(kb_content).lower() != 'nan':
            content_type = "KB"
            content_value = kb_content
        elif script_content and script_content != 'N/A' and str(script_content).lower() != 'nan':
            content_type = "Script"
            content_value = script_content
        else:
            content_type = "Resolution"
            content_value = data.get('Resolution', 'N/A')

        output = {
            "RAG_response": {
                "query": query,
                "generated_answer": generated_response,
                "ticket_id": new_ticket_id,
                "refered_ticket_id": str(data.get('Ticket_Number', 'N/A')),
                "created_date": str(data.get('Created_Date', 'N/A')),
                "conversation_id": str(data.get('Conversation_ID', 'N/A')),
                "first_tier_agent_name": str(data.get('Agent_Name', 'N/A')),
                "product": str(data.get('Product_x', 'N/A')),
                "category": str(data.get('Category_x', 'N/A')),
                "answer_type": str(data.get('Answer_Type', 'N/A')),
                "resolution": {
                    "content": f"{content_type}: {content_value}",
                    "agent_id": str(data.get('Agent_Name', 'N/A')),
                    "relevancy_score": relevancy_result['score'],
                    "relevancy_breakdown": {
                        "relevancy_points": relevancy_result['relevancy_points'],
                        "accuracy_points": relevancy_result['accuracy_points'],
                        "completeness_points": relevancy_result['completeness_points']
                    },
                    "reasoning": relevancy_result['reasoning'],
                    "reference_article": {
                        "kb_id": str(kb_content if kb_content != 'N/A' and str(kb_content).lower() != 'nan' else None),
                        "script_id": str(script_content if script_content != 'N/A' and str(script_content).lower() != 'nan' else None),
                        "generated_kb_id": str(data.get('Generated_KB_Article_ID', 'N/A'))
                    }
                },
                "metadata": {
                    "similarity_score": retrieved_doc['similarity_score'],
                    "distance": retrieved_doc['distance'],
                    "priority": str(data.get('Priority', 'N/A')),
                    "sentiment": str(data.get('Sentiment', 'N/A')),
                    "channel": str(data.get('Channel', 'N/A'))
                }
            }
        }

        return output

    def classify_query(self, query, top_k=3, return_all=False):
        """
        Main classification method: retrieve, generate, and score.

        Args:
            query: User query text
            top_k: Number of similar documents to retrieve
            return_all: If True, return results for all top_k documents

        Returns:
            List of formatted results (or single result if return_all=False)
        """
        print(f"\n{'='*80}")
        print(f"CLASSIFICATION AGENT")
        print(f"{'='*80}")
        print(f"Query: {query}")
        print(f"Top K: {top_k}")
        print(f"{'='*80}\n")

        # Generate new ticket ID
        new_ticket_id = last_row_db()
        print(f"Generated new ticket ID: {new_ticket_id}\n")

        # Step 1: Retrieve similar documents
        print("Step 1: Retrieving similar documents...")
        retrieved_docs = self._retrieve_similar_documents(query, top_k)
        print(f"✓ Retrieved {len(retrieved_docs)} documents\n")

        # Step 2: Generate LLM response
        print("Step 2: Generating LLM response...")
        generated_response = self._generate_llm_response(query, retrieved_docs)
        print(f"✓ Generated response\n")

        # Step 3: Score each retrieved document
        print("Step 3: Calculating relevancy scores (LLM-as-judge)...")
        results = []

        for i, doc in enumerate(retrieved_docs, 1):
            print(f"  Scoring document {i}/{len(retrieved_docs)}...")

            resolution = doc['data'].get('Resolution', 'N/A')
            relevancy_result = self._calculate_relevancy_score(
                query,
                generated_response,
                resolution
            )

            formatted_output = self._format_output(
                query,
                doc,
                generated_response,
                relevancy_result,
                new_ticket_id
            )

            results.append(formatted_output)

        print(f"✓ Scoring complete\n")

        # Return results
        if return_all:
            return results
        else:
            return results[0] if results else None


def main():
    """CLI entry point for classification agent."""
    if len(sys.argv) < 2:
        print(
            "Usage: python classification_agent.py 'your query here' [top_k] [--all]")
        print("\nExamples:")
        print("  python classification_agent.py 'login issues' 3")
        print("  python classification_agent.py 'certification problems' 5 --all")
        print("\nOptions:")
        print("  top_k: Number of similar documents to retrieve (default: 1)")
        print("  --all: Return results for all top_k documents (default: top 1 only)")
        sys.exit(1)

    query = sys.argv[1]
    top_k = int(sys.argv[2]) if len(
        sys.argv) > 2 and sys.argv[2] != '--all' else 1
    return_all = '--all' in sys.argv

    # Initialize agent
    agent = ClassificationAgent()

    # Classify query
    results = agent.classify_query(query, top_k=top_k, return_all=return_all)

    # Pretty print results
    print(f"\n{'='*80}")
    print("RESULTS")
    print(f"{'='*80}\n")

    if return_all:
        for i, result in enumerate(results, 1):
            print(f"\n--- Result {i} ---")
            print(json.dumps(result, indent=2))
    else:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
