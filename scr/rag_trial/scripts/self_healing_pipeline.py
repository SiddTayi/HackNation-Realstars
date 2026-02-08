import os
import sys
import sqlite3
import pickle
import numpy as np
import faiss
from openai import OpenAI
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import uuid
import json

# Load environment variables
load_dotenv()


def create_text_from_row(row):
    """
    Create a comprehensive text representation from a row for embedding.
    Uses the SAME format as ingest_data.py to ensure consistency.
    Expects the 24-field schema from final_ver3.xlsx.

    Args:
        row: Dictionary containing row data with 24 fields

    Returns:
        str: Text representation for embedding
    """
    parts = []

    # Add ticket information
    if row.get('Ticket_Number') and str(row.get('Ticket_Number')) != 'None':
        parts.append(f"Ticket: {row['Ticket_Number']}")

    # Add product and category
    if row.get('Product_x') and str(row.get('Product_x')) != 'None':
        parts.append(f"Product: {row['Product_x']}")
    if row.get('Category_x') and str(row.get('Category_x')) != 'None':
        parts.append(f"Category: {row['Category_x']}")

    # Add issue summary (most important)
    if row.get('Issue_Summary') and str(row.get('Issue_Summary')) != 'None':
        parts.append(f"Issue: {row['Issue_Summary']}")

    # Add subject
    if row.get('Subject') and str(row.get('Subject')) != 'None':
        parts.append(f"Subject: {row['Subject']}")

    # Add description
    if row.get('Description') and str(row.get('Description')) != 'None':
        parts.append(f"Description: {row['Description']}")

    # Add resolution
    if row.get('Resolution') and str(row.get('Resolution')) != 'None':
        parts.append(f"Resolution: {row['Resolution']}")

    # Add root cause
    if row.get('Root_Cause') and str(row.get('Root_Cause')) != 'None':
        parts.append(f"Root Cause: {row['Root_Cause']}")

    # Add tags
    if row.get('Tags_generated_kb') and str(row.get('Tags_generated_kb')) != 'None':
        parts.append(f"Tags: {row['Tags_generated_kb']}")

    return "\n".join(parts)


def normalize_row_for_vector_store(data, data_type, issue_summary=""):
    """
    Normalize script or KB data to the 24-field schema used by the vector store.
    This ensures consistency with existing data from final_ver3.xlsx.

    Args:
        data: Dictionary with script (8 fields) or KB (10 fields) data
        data_type: 'script' or 'kb'
        issue_summary: The original user issue summary

    Returns:
        dict: Normalized 24-field row for vector store
    """
    if data_type == 'script':
        return {
            # Original 24-field schema
            'Unnamed: 0': None,
            'Ticket_Number': None,
            'Conversation_ID': None,
            'Channel': 'SELF_HEALING',
            'Customer_Role': None,
            'Agent_Name': 'AI_SYSTEM',
            'Product_x': data.get('Module', ''),
            'Category_x': data.get('Category', ''),
            'Issue_Summary': issue_summary,
            'Transcript': None,
            'Sentiment': None,
            'Priority': 'Medium',
            'Tier': '2',
            'Module_generated_kb': data.get('Module', ''),
            'Subject': data.get('Script_Title', ''),
            'Description': data.get('Script_Purpose', ''),
            'Resolution': data.get('Script_Text_Sanitized', ''),
            'Root_Cause': None,
            'Tags_generated_kb': f"script, {data.get('Category', '').lower()}, self-healing",
            'KB_Article_ID_x': None,
            'Script_ID': data.get('Script_ID', ''),
            'Generated_KB_Article_ID': None,
            'Source_ID': data.get('Script_ID', ''),
            'Answer_Type': 'Script'
        }

    elif data_type == 'kb':
        return {
            # Original 24-field schema
            'Unnamed: 0': None,
            'Ticket_Number': None,
            'Conversation_ID': None,
            'Channel': 'SELF_HEALING',
            'Customer_Role': None,
            'Agent_Name': 'AI_SYSTEM',
            'Product_x': data.get('Module', ''),
            'Category_x': data.get('Category', ''),
            'Issue_Summary': data.get('Title', ''),
            'Transcript': None,
            'Sentiment': None,
            'Priority': 'Medium',
            'Tier': '2',
            'Module_generated_kb': data.get('Module', ''),
            'Subject': data.get('Title', ''),
            'Description': data.get('Body', '')[:500] if data.get('Body') else '',
            'Resolution': data.get('Body', ''),
            'Root_Cause': None,
            'Tags_generated_kb': data.get('Tags', ''),
            'KB_Article_ID_x': data.get('KB_Article_ID', ''),
            'Script_ID': None,
            'Generated_KB_Article_ID': data.get('KB_Article_ID', ''),
            'Source_ID': data.get('KB_Article_ID', ''),
            'Answer_Type': 'KB'
        }

    return {}


def generate_and_update_script(retrieval_results, issue_summary, classification_type, db_path=None):
    """
    Generate a new custom script using GPT-4 based on similar scripts from retrieval.
    Queries scripts.db to get full script details, then inserts the new script.

    Args:
        retrieval_results: List of similar scripts from RAG retrieval (contains Script_IDs)
        issue_summary: Summary of the issue that needs a script
        classification_type: Should be 'SCRIPT'
        db_path: Path to scripts.db (optional, uses default if not provided)

    Returns:
        dict: Normalized 24-field row for vector store
    """
    # Set up database path
    if db_path is None:
        script_dir = Path(__file__).parent
        db_path = script_dir.parent / "databases" / "scripts.db"

    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    client = OpenAI(api_key=api_key)

    print(f"\n{'='*80}")
    print("GENERATING NEW SCRIPT")
    print(f"{'='*80}")
    print(f"Issue Summary: {issue_summary}")
    print(f"Number of retrieval results: {len(retrieval_results)}")

    # Connect to scripts.db
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Extract Script_IDs from retrieval results and query scripts.db for full details
    script_examples = []
    for result in retrieval_results[:3]:  # Use top 3 results
        data = result.get('data', {})
        script_id = data.get('Script_ID') or data.get('Source_ID')

        if script_id and script_id.startswith('SCRIPT-'):
            # Query scripts.db for full script details
            cursor.execute('''
                SELECT Script_ID, Script_Title, Script_Purpose, Script_Inputs, 
                       Module, Category, Script_Text_Sanitized
                FROM scripts_master 
                WHERE Script_ID = ?
            ''', (script_id,))

            script_row = cursor.fetchone()
            if script_row:
                script_examples.append({
                    'id': script_row[0],
                    'title': script_row[1],
                    'purpose': script_row[2],
                    'inputs': script_row[3],
                    'module': script_row[4],
                    'category': script_row[5],
                    'text': script_row[6]
                })
                print(f"  Retrieved script from DB: {script_row[0]}")

    if not script_examples:
        print("  Warning: No scripts found in scripts.db from Script_IDs")
        print("  Attempting to use retrieval data directly as fallback...")
        # Fallback: try to use data directly from retrieval if it has script content
        for result in retrieval_results[:3]:
            data = result.get('data', {})
            if data.get('Script_Text_Sanitized') or data.get('Resolution'):
                script_examples.append({
                    'id': data.get('Script_ID', 'N/A'),
                    'title': data.get('Script_Title', data.get('Subject', 'N/A')),
                    'purpose': data.get('Script_Purpose', data.get('Description', 'N/A')),
                    'inputs': data.get('Script_Inputs', 'N/A'),
                    'module': data.get('Module', data.get('Module_generated_kb', 'N/A')),
                    'category': data.get('Category', data.get('Category_x', 'N/A')),
                    'text': data.get('Script_Text_Sanitized', data.get('Resolution', 'N/A'))
                })

    print(f"  Using {len(script_examples)} script examples for generation")

    print(f"  Using {len(script_examples)} script examples for generation")

    # Create prompt for GPT-4
    prompt = f"""You are a database script expert. Generate a new SQL script based on the following information:

ISSUE SUMMARY:
{issue_summary}

SIMILAR SCRIPTS FOR REFERENCE:
"""

    for i, example in enumerate(script_examples, 1):
        prompt += f"""
Script {i} (ID: {example['id']}):
Title: {example['title']}
Purpose: {example['purpose']}
Inputs: {example['inputs']}
Module: {example['module']}
Category: {example['category']}
Script Text:
{example['text'][:500]}...

"""

    prompt += """
Based on the issue summary and the similar scripts provided, generate a NEW script that addresses this specific issue.

Provide your response in the following JSON format:
{
    "script_title": "Brief descriptive title",
    "script_purpose": "What this script does and when to use it",
    "script_inputs": "Placeholders needed (e.g., <DATABASE>, <SITE_NAME>)",
    "module": "Module name from examples",
    "category": "Category from examples",
    "script_text": "Complete SQL script with comments"
}

Make sure the script follows the same style and uses similar placeholders as the examples.
"""

    print("\nCalling GPT-4 to generate script...")

    # Call GPT-4
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert SQL script writer for support automation. Generate clear, well-documented scripts."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )

    # Parse response
    response_text = response.choices[0].message.content.strip()

    # Extract JSON from response (handle markdown code blocks)
    if "```json" in response_text:
        response_text = response_text.split(
            "```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()

    script_data = json.loads(response_text)

    print("\n✓ Script generated successfully")
    print(f"  Title: {script_data['script_title']}")
    print(f"  Module: {script_data['module']}")
    print(f"  Category: {script_data['category']}")

    # Generate new Script_ID - Get the highest existing script number
    cursor.execute(
        "SELECT Script_ID FROM scripts_master WHERE Script_ID LIKE 'SCRIPT-%' ORDER BY Script_ID DESC LIMIT 1")
    result = cursor.fetchone()

    if result:
        last_id = result[0]
        last_num = int(last_id.split('-')[1])
        new_num = last_num + 1
    else:
        new_num = 9000  # Start from 9000 for self-healing scripts

    new_script_id = f"SCRIPT-{new_num:04d}"

    # Prepare new row for scripts.db (8 fields only)
    new_script_db_row = {
        'Script_ID': new_script_id,
        'Script_Title': script_data['script_title'],
        'Script_Purpose': script_data['script_purpose'],
        'Script_Inputs': script_data['script_inputs'],
        'Module': script_data['module'],
        'Category': script_data['category'],
        'Source': 'SELF_HEALING',
        'Script_Text_Sanitized': script_data['script_text']
    }

    # Insert into scripts.db
    cursor.execute('''
        INSERT INTO scripts_master (
            Script_ID, Script_Title, Script_Purpose, Script_Inputs,
            Module, Category, Source, Script_Text_Sanitized
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        new_script_db_row['Script_ID'],
        new_script_db_row['Script_Title'],
        new_script_db_row['Script_Purpose'],
        new_script_db_row['Script_Inputs'],
        new_script_db_row['Module'],
        new_script_db_row['Category'],
        new_script_db_row['Source'],
        new_script_db_row['Script_Text_Sanitized']
    ))

    conn.commit()
    conn.close()

    print(f"\n✓ Script inserted into scripts.db with ID: {new_script_id}")

    # Normalize to 24-field format for vector store
    normalized_row = normalize_row_for_vector_store(
        new_script_db_row, 'script', issue_summary)
    print(f"✓ Normalized to 24-field schema for vector store")

    return normalized_row


def update_knowledge_article(kb_row_data, classification_type, db_path=None):
    """
    Add a new knowledge article to the database.
    Frontend provides all KB data (Title, Body, Tags, Module, Category).

    Args:
        kb_row_data: Dictionary containing complete KB article data from frontend
        classification_type: Should be 'KB'
        db_path: Path to knowledge_articles.db (optional, uses default if not provided)

    Returns:
        dict: Normalized 24-field row for vector store
    """
    # Set up database path
    if db_path is None:
        script_dir = Path(__file__).parent
        db_path = script_dir.parent / "databases" / "knowledge_articles.db"

    print(f"\n{'='*80}")
    print("UPDATING KNOWLEDGE ARTICLE")
    print(f"{'='*80}")

    # Generate new KB_Article_ID
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Generate UUID-based ID
    new_kb_id = f"KB-SELF-HEALING-{uuid.uuid4().hex[:8].upper()}"

    # Get current timestamp
    now = datetime.now().isoformat()

    # Prepare new row for knowledge_articles.db (10 fields only)
    new_kb_db_row = {
        'KB_Article_ID': new_kb_id,
        'Title': kb_row_data.get('Title', kb_row_data.get('Issue_Summary', 'Untitled')),
        'Body': kb_row_data.get('Body', kb_row_data.get('Resolution', '')),
        'Tags': kb_row_data.get('Tags', kb_row_data.get('Tags_generated_kb', '')),
        'Module': kb_row_data.get('Module', kb_row_data.get('Module_generated_kb', '')),
        'Category': kb_row_data.get('Category', kb_row_data.get('Category_x', '')),
        'Created_At': now,
        'Updated_At': now,
        'Status': 'Active',
        'Source_Type': 'SELF_HEALING'
    }

    print(f"Creating new KB article:")
    print(f"  ID: {new_kb_id}")
    print(f"  Title: {new_kb_db_row['Title'][:60]}...")
    print(f"  Module: {new_kb_db_row['Module']}")
    print(f"  Category: {new_kb_db_row['Category']}")

    # Insert into knowledge_articles.db
    cursor.execute('''
        INSERT INTO knowledge_articles (
            KB_Article_ID, Title, Body, Tags, Module, Category,
            Created_At, Updated_At, Status, Source_Type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        new_kb_db_row['KB_Article_ID'],
        new_kb_db_row['Title'],
        new_kb_db_row['Body'],
        new_kb_db_row['Tags'],
        new_kb_db_row['Module'],
        new_kb_db_row['Category'],
        new_kb_db_row['Created_At'],
        new_kb_db_row['Updated_At'],
        new_kb_db_row['Status'],
        new_kb_db_row['Source_Type']
    ))

    conn.commit()
    conn.close()

    print(
        f"✓ KB article inserted into knowledge_articles.db with ID: {new_kb_id}")

    # Normalize to 24-field format for vector store
    normalized_row = normalize_row_for_vector_store(new_kb_db_row, 'kb')
    print(f"✓ Normalized to 24-field schema for vector store")

    return normalized_row


def update_vector_store(new_row_data, data_type, vector_store_path=None):
    """
    Update the FAISS vector store by adding a new embedding for the new row.
    Expects new_row_data to be in the 24-field normalized format.

    Args:
        new_row_data: Dictionary containing the normalized 24-field row data
        data_type: Type of data ('script' or 'kb') - for logging only
        vector_store_path: Path to vector store directory (optional)

    Returns:
        bool: True if successful, False otherwise
    """
    # Set up paths
    if vector_store_path is None:
        script_dir = Path(__file__).parent
        vector_store_path = script_dir.parent / "vector_store"

    index_path = Path(vector_store_path) / "faiss_index.bin"
    metadata_path = Path(vector_store_path) / "metadata.pkl"

    print(f"\n{'='*80}")
    print("UPDATING VECTOR STORE")
    print(f"{'='*80}")
    print(f"Data type: {data_type}")
    print(f"Vector store: {vector_store_path}")

    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    client = OpenAI(api_key=api_key)

    # Load existing FAISS index
    print("Loading existing FAISS index...")
    index = faiss.read_index(str(index_path))
    print(f"  Current vectors: {index.ntotal}")

    # Load metadata
    print("Loading metadata...")
    with open(metadata_path, 'rb') as f:
        metadata = pickle.load(f)

    # Create text representation using the same format as ingest_data.py
    print("Creating text representation...")
    text = create_text_from_row(new_row_data)
    print(f"  Text length: {len(text)} chars")

    # Generate embedding
    print(f"Generating embedding using {metadata['model']}...")
    response = client.embeddings.create(
        input=[text],
        model=metadata['model']
    )
    embedding = np.array([response.data[0].embedding], dtype=np.float32)
    print(f"  Embedding dimension: {embedding.shape[1]}")

    # Add to FAISS index (incremental update)
    print("Adding embedding to FAISS index...")
    index.add(embedding)
    print(f"  New total vectors: {index.ntotal}")

    # Update metadata
    print("Updating metadata...")
    metadata['texts'].append(text)
    metadata['dataframe'].append(new_row_data)
    metadata['total_vectors'] = index.ntotal

    # Save updated index
    print("Saving updated FAISS index...")
    faiss.write_index(index, str(index_path))

    # Save updated metadata
    print("Saving updated metadata...")
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)

    print(f"\n✓ Vector store updated successfully")
    print(f"  Total vectors: {index.ntotal}")

    return True


def run_self_healing_pipeline(retrieval_results, issue_summary, classification_type):
    """
    Main orchestration function for the self-healing pipeline.
    Routes to appropriate function based on classification type.

    Args:
        retrieval_results: List of retrieval results from RAG
        issue_summary: Summary of the user's issue
        classification_type: One of 'SCRIPT', 'KB', or 'TICKET_RESOLUTION'

    Returns:
        dict: Status and new data (if any)
    """
    print(f"\n{'#'*80}")
    print("SELF-HEALING PIPELINE")
    print(f"{'#'*80}")
    print(f"Classification: {classification_type}")
    print(f"Issue Summary: {issue_summary}")
    print(f"Retrieval Results: {len(retrieval_results)}")
    print(f"{'#'*80}\n")

    result = {
        'status': 'success',
        'classification': classification_type,
        'new_data': None,
        'message': ''
    }

    try:
        if classification_type == 'SCRIPT':
            # Generate new script and update database
            new_script = generate_and_update_script(
                retrieval_results, issue_summary, classification_type)

            # Update vector store
            update_vector_store(new_script, data_type='script')

            result['new_data'] = new_script
            result['message'] = f"Successfully generated and stored new script: {new_script['Script_ID']}"

        elif classification_type == 'KB':
            # Get KB data from first retrieval result
            if not retrieval_results:
                raise ValueError("No retrieval results provided for KB update")

            kb_data = retrieval_results[0].get('data', {})

            # Add new KB article
            new_kb = update_knowledge_article(kb_data, classification_type)

            # Update vector store
            update_vector_store(new_kb, data_type='kb')

            result['new_data'] = new_kb
            result['message'] = f"Successfully stored new KB article: {new_kb['KB_Article_ID']}"

        elif classification_type == 'TICKET_RESOLUTION':
            # No action needed - answer was found in previous tickets
            result['message'] = "Answer found in previous ticket resolutions. No self-healing action needed."
            print(f"\n{'='*80}")
            print("TICKET_RESOLUTION - No action needed")
            print(f"{'='*80}")

        else:
            raise ValueError(
                f"Unknown classification type: {classification_type}")

        print(f"\n{'#'*80}")
        print("SELF-HEALING PIPELINE COMPLETE")
        print(f"{'#'*80}")
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        print(f"{'#'*80}\n")

        return result

    except Exception as e:
        result['status'] = 'error'
        result['message'] = f"Error in self-healing pipeline: {str(e)}"
        print(f"\n✗ ERROR: {result['message']}")
        raise


def main():
    """Example usage of the self-healing pipeline."""

    if len(sys.argv) < 3:
        print(
            "Usage: python self_healing_pipeline.py <classification_type> <issue_summary>")
        print("\nClassification types: SCRIPT, KB, TICKET_RESOLUTION")
        print("\nExample:")
        print("  python self_healing_pipeline.py SCRIPT 'Need script to update compliance certifications'")
        print("  python self_healing_pipeline.py KB 'How to reset user password'")
        sys.exit(1)

    classification_type = sys.argv[1].upper()
    issue_summary = sys.argv[2]

    # Mock retrieval results (in real usage, this comes from RAG)
    retrieval_results = [
        {
            'data': {
                'Script_ID': 'SCRIPT-0001',
                'Script_Title': 'Example Script',
                'Script_Purpose': 'Example purpose',
                'Script_Inputs': '<DATABASE>',
                'Module': 'Example Module',
                'Category': 'Example Category',
                'Script_Text_Sanitized': 'SELECT * FROM table;'
            }
        }
    ]

    result = run_self_healing_pipeline(
        retrieval_results, issue_summary, classification_type)

    print("\nFinal Result:")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
