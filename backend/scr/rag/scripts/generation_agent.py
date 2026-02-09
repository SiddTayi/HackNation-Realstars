"""
Generation Agent for RAG System
Generates KB articles and Scripts based on classification output
"""

import os
import sys
import json
import re
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime


def repair_json(json_str):
    """Attempt to repair malformed JSON from LLM responses."""
    # Remove any trailing commas before } or ]
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    
    # Fix unescaped newlines in strings
    # This is a simplified approach - replace literal newlines with \n
    lines = json_str.split('\n')
    fixed_lines = []
    in_string = False
    for line in lines:
        # Count unescaped quotes to track if we're in a string
        quote_count = len(re.findall(r'(?<!\\)"', line))
        if in_string:
            # We're continuing a string from previous line
            fixed_lines[-1] += '\\n' + line
        else:
            fixed_lines.append(line)
        # Update in_string state
        in_string = (quote_count % 2 == 1) != in_string
    
    return '\n'.join(fixed_lines)

# Add parent directory to path for db_scripts import
sys.path.insert(0, str(Path(__file__).parent.parent))

from db_scripts.db_scripts import retrieve_script
from db_scripts.db_knowledge_articles import retrieve_kb, last_row_db as last_kb_id, insert_kb
from db_scripts.db_ticket import retrieve_ticket_by_id_string

# Load environment variables
load_dotenv()


class GenerationAgent:
    """
    Agent for generating KB articles and scripts based on classification output.
    """

    def __init__(self):
        """Initialize the generation agent with OpenAI client."""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=self.api_key)
        print("✓ Generation Agent initialized")

    def _retrieve_kb_context(self, kb_ids):
        """
        Retrieve KB articles from knowledge_articles.db by IDs.
        
        Args:
            kb_ids: List of KB article IDs
            
        Returns:
            List of KB article dictionaries
        """
        kb_articles = []
        
        for kb_id in kb_ids:
            if kb_id and kb_id != 'None' and str(kb_id).lower() != 'nan':
                kb = retrieve_kb(str(kb_id))
                if kb:
                    kb_articles.append(kb)
                    print(f"  ✓ Retrieved KB: {kb_id}")
                else:
                    print(f"  ✗ KB not found: {kb_id}")
        
        return kb_articles

    def _retrieve_script_context(self, script_ids):
        """
        Retrieve scripts from scripts.db by IDs.
        
        Args:
            script_ids: List of script IDs
            
        Returns:
            List of script dictionaries
        """
        scripts = []
        
        for script_id in script_ids:
            if script_id and script_id != 'None' and str(script_id).lower() != 'nan':
                script = retrieve_script(str(script_id))
                if script:
                    scripts.append(script)
                    print(f"  ✓ Retrieved Script: {script_id}")
                else:
                    print(f"  ✗ Script not found: {script_id}")
        
        return scripts

    def _generate_kb_article(self, query, kb_context):
        """
        Generate a new KB article by synthesizing retrieved KB articles.
        
        Args:
            query: User query
            kb_context: List of retrieved KB articles
            
        Returns:
            Dictionary with generated KB article data
        """
        print("\n" + "="*80)
        print("GENERATING KB ARTICLE")
        print("="*80)
        
        # Build context from retrieved KB articles
        context_parts = []
        for i, kb in enumerate(kb_context, 1):
            context_parts.append(f"""
KB Article {i} (ID: {kb['KB_Article_ID']}):
Title: {kb['Title']}
Module: {kb['Module']}
Category: {kb['Category']}
Tags: {kb['Tags']}
Body:
{kb['Body'][:1000]}{"..." if len(kb['Body']) > 1000 else ""}
""")
        
        context = "\n".join(context_parts)
        
        # Create LLM prompt
        system_prompt = """You are a knowledge base expert. Create comprehensive KB articles by synthesizing information from multiple sources.
Your goal is to create clear, actionable documentation that helps users solve their issues."""

        user_prompt = f"""USER QUERY: {query}

REFERENCE KB ARTICLES:
{context}

Based on the user query and the reference KB articles above, create a NEW comprehensive KB article that synthesizes this information.

Provide your response in the following JSON format:
{{
    "title": "Clear, descriptive title",
    "body": "Comprehensive body with step-by-step instructions, explanations, and examples",
    "tags": "Comma-separated relevant tags",
    "module": "Module name from reference articles",
    "category": "Category from reference articles"
}}

Make the article clear, actionable, and well-structured."""

        print("Calling GPT-4o to generate KB article...")
        
        # Generate KB article
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Parse response
        response_text = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        # Try to parse JSON, with repair attempt if it fails
        try:
            kb_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"  JSON parse error: {e}")
            print(f"  Attempting to repair JSON...")
            repaired = repair_json(response_text)
            try:
                kb_data = json.loads(repaired)
                print(f"  ✓ JSON repaired successfully")
            except json.JSONDecodeError:
                print(f"  ✗ Could not repair JSON, using fallback")
                kb_data = {
                    'title': 'Support Resolution Article',
                    'body': 'Article generation failed. Please review the original ticket.',
                    'tags': 'auto-generated',
                    'module': 'General',
                    'category': 'Support'
                }
        
        print(f"✓ KB article generated successfully")
        print(f"  Title: {kb_data['title'][:60]}...")
        print(f"  Module: {kb_data['module']}")
        print(f"  Category: {kb_data['category']}")
        
        # Generate new KB ID
        new_kb_id = last_kb_id()
        
        # Prepare KB article for insertion
        now = datetime.now().isoformat()
        kb_article = {
            'KB_Article_ID': new_kb_id,
            'Title': kb_data['title'],
            'Body': kb_data['body'],
            'Tags': kb_data['tags'],
            'Module': kb_data['module'],
            'Category': kb_data['category'],
            'Created_At': now,
            'Updated_At': now,
            'Status': 'Active',
            'Source_Type': 'GENERATED'
        }
        
        # Insert into database
        success = insert_kb(**kb_article)
        if success:
            print(f"✓ KB article saved to database: {new_kb_id}")
        else:
            print(f"✗ Failed to save KB article to database")
        
        return kb_article

    def _generate_script_and_kb(self, query, script_context, kb_context):
        """
        Generate both a new script and a new KB article.
        
        Args:
            query: User query
            script_context: List of retrieved scripts
            kb_context: List of retrieved KB articles
            
        Returns:
            Dictionary with generated script and KB article data
        """
        print("\n" + "="*80)
        print("GENERATING SCRIPT AND KB ARTICLE")
        print("="*80)
        
        # Build script context
        script_parts = []
        for i, script in enumerate(script_context, 1):
            script_parts.append(f"""
Script {i} (ID: {script['Script_ID']}):
Title: {script['Script_Title']}
Purpose: {script['Script_Purpose']}
Module: {script['Module']}
Category: {script['Category']}
Inputs: {script['Script_Inputs']}
Code:
{script['Script_Text_Sanitized'][:800]}{"..." if len(script['Script_Text_Sanitized']) > 800 else ""}
""")
        
        script_context_str = "\n".join(script_parts)
        
        # Build KB context
        kb_parts = []
        for i, kb in enumerate(kb_context, 1):
            kb_parts.append(f"""
KB Article {i} (ID: {kb['KB_Article_ID']}):
Title: {kb['Title']}
Module: {kb['Module']}
Category: {kb['Category']}
Body:
{kb['Body'][:600]}{"..." if len(kb['Body']) > 600 else ""}
""")
        
        kb_context_str = "\n".join(kb_parts) if kb_parts else "No KB articles available."
        
        # Create LLM prompt for script generation
        system_prompt = """You are a database script and documentation expert. Create both functional SQL scripts and comprehensive KB documentation.
Your scripts should be production-ready with proper error handling and comments."""

        user_prompt = f"""USER QUERY: {query}

REFERENCE SCRIPTS:
{script_context_str}

REFERENCE KB ARTICLES:
{kb_context_str}

Based on the user query and the reference materials above, create:
1. A NEW SQL script that addresses the user's needs
2. A NEW KB article that documents how to use this script

Provide your response in the following JSON format:
{{
    "script": {{
        "title": "Descriptive script title",
        "purpose": "What this script does and when to use it",
        "inputs": "Required placeholders (e.g., <DATABASE>, <TABLE_NAME>)",
        "module": "Module name from references",
        "category": "Category from references",
        "code": "Complete SQL script with comments"
    }},
    "kb_article": {{
        "title": "How to use [script title]",
        "body": "Comprehensive documentation with usage instructions, prerequisites, examples, and troubleshooting",
        "tags": "Comma-separated relevant tags",
        "module": "Same as script module",
        "category": "Same as script category"
    }}
}}

Make both outputs clear, actionable, and professional."""

        print("Calling GPT-4o to generate script and KB article...")
        
        # Generate content
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        # Parse response
        response_text = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        # Try to parse JSON, with repair attempt if it fails
        try:
            generated_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"  JSON parse error: {e}")
            print(f"  Attempting to repair JSON...")
            repaired = repair_json(response_text)
            try:
                generated_data = json.loads(repaired)
                print(f"  ✓ JSON repaired successfully")
            except json.JSONDecodeError:
                # Last resort: return a default structure
                print(f"  ✗ Could not repair JSON, using fallback")
                generated_data = {
                    'script': {
                        'title': 'Auto-generated Script',
                        'purpose': 'Generated from support ticket',
                        'inputs': 'See script comments',
                        'module': 'General',
                        'category': 'Support',
                        'code': '-- Script generation failed, manual review needed'
                    },
                    'kb_article': {
                        'title': 'Support Resolution Article',
                        'body': 'Article generation failed. Please review the original ticket.',
                        'tags': 'auto-generated',
                        'module': 'General',
                        'category': 'Support'
                    }
                }
        
        print(f"✓ Script and KB article generated successfully")
        print(f"  Script Title: {generated_data['script']['title'][:60]}...")
        print(f"  KB Title: {generated_data['kb_article']['title'][:60]}...")
        
        # Import script functions
        from db_scripts.db_scripts import last_row_db as last_script_id, insert_script
        
        # Generate new Script ID
        new_script_id = last_script_id()
        
        # Prepare script for insertion
        script_data = {
            'Script_ID': new_script_id,
            'Script_Title': generated_data['script']['title'],
            'Script_Purpose': generated_data['script']['purpose'],
            'Script_Inputs': generated_data['script']['inputs'],
            'Module': generated_data['script']['module'],
            'Category': generated_data['script']['category'],
            'Source': 'GENERATED',
            'Script_Text_Sanitized': generated_data['script']['code']
        }
        
        # Insert script into database
        success = insert_script(**script_data)
        if success:
            print(f"✓ Script saved to database: {new_script_id}")
        else:
            print(f"✗ Failed to save script to database")
        
        # Generate new KB ID
        new_kb_id = last_kb_id()
        
        # Prepare KB article for insertion
        now = datetime.now().isoformat()
        kb_data = {
            'KB_Article_ID': new_kb_id,
            'Title': generated_data['kb_article']['title'],
            'Body': generated_data['kb_article']['body'],
            'Tags': generated_data['kb_article']['tags'],
            'Module': generated_data['kb_article']['module'],
            'Category': generated_data['kb_article']['category'],
            'Created_At': now,
            'Updated_At': now,
            'Status': 'Active',
            'Source_Type': 'GENERATED'
        }
        
        # Insert KB article into database
        success = insert_kb(**kb_data)
        if success:
            print(f"✓ KB article saved to database: {new_kb_id}")
        else:
            print(f"✗ Failed to save KB article to database")
        
        return {
            'script': script_data,
            'kb_article': kb_data
        }

    def generate(self, classification_output):
        """
        Main method that routes generation based on classification.
        
        Args:
            classification_output: Output from classification_agent
            
        Returns:
            Dictionary with generated content
        """
        print("\n" + "#"*80)
        print("GENERATION AGENT")
        print("#"*80)
        
        # Extract reference article information
        rag_response = classification_output.get('RAG_response', {})
        reference = rag_response.get('resolution', {}).get('reference_article', {})
        query = rag_response.get('query', '')
        generated_answer = rag_response.get('generated_answer', '')
        
        kb_id = reference.get('kb_id')
        script_id = reference.get('script_id')
        generated_kb_id = reference.get('generated_kb_id')
        
        print(f"Query: {query}")
        print(f"KB ID: {kb_id}")
        print(f"Script ID: {script_id}")
        print(f"Generated KB ID: {generated_kb_id}")
        print("#"*80)
        
        result = {
            'classification': None,
            'generated_content': None,
            'message': ''
        }
        
        # Determine classification based on which IDs are present
        if script_id and script_id != 'None' and str(script_id).lower() != 'nan':
            # SCRIPT classification
            result['classification'] = 'SCRIPT'
            print(f"\nClassification: SCRIPT")
            
            # Collect all IDs
            script_ids = [script_id]
            kb_ids = []
            if kb_id and kb_id != 'None' and str(kb_id).lower() != 'nan':
                kb_ids.append(kb_id)
            if generated_kb_id and generated_kb_id != 'None' and str(generated_kb_id).lower() != 'nan':
                kb_ids.append(generated_kb_id)
            
            # Retrieve context
            print("\nRetrieving script context...")
            script_context = self._retrieve_script_context(script_ids)
            
            print("\nRetrieving KB context...")
            kb_context = self._retrieve_kb_context(kb_ids)
            
            # Generate script and KB article
            if script_context:
                generated = self._generate_script_and_kb(query, script_context, kb_context)
                result['generated_content'] = generated
                result['message'] = f"Generated new script ({generated['script']['Script_ID']}) and KB article ({generated['kb_article']['KB_Article_ID']})"
            else:
                result['message'] = "No script context found, cannot generate"
                
        elif (kb_id and kb_id != 'None' and str(kb_id).lower() != 'nan') or \
             (generated_kb_id and generated_kb_id != 'None' and str(generated_kb_id).lower() != 'nan'):
            # KB classification
            result['classification'] = 'KB'
            print(f"\nClassification: KB")
            
            # Collect KB IDs
            kb_ids = []
            if kb_id and kb_id != 'None' and str(kb_id).lower() != 'nan':
                kb_ids.append(kb_id)
            if generated_kb_id and generated_kb_id != 'None' and str(generated_kb_id).lower() != 'nan':
                kb_ids.append(generated_kb_id)
            
            # Retrieve KB context
            print("\nRetrieving KB context...")
            kb_context = self._retrieve_kb_context(kb_ids)
            
            # Generate KB article
            if kb_context:
                generated = self._generate_kb_article(query, kb_context)
                result['generated_content'] = generated
                result['message'] = f"Generated new KB article ({generated['KB_Article_ID']})"
            else:
                result['message'] = "No KB context found, cannot generate"
                
        else:
            # RESOLUTION classification
            result['classification'] = 'RESOLUTION'
            print(f"\nClassification: RESOLUTION")
            
            result['generated_content'] = {
                'answer': generated_answer,
                'query': query
            }
            result['message'] = "Resolution found in previous tickets, no new generation needed"
        
        print("\n" + "#"*80)
        print("GENERATION COMPLETE")
        print("#"*80)
        print(f"Classification: {result['classification']}")
        print(f"Message: {result['message']}")
        print("#"*80 + "\n")
        
        return result


def main():
    """CLI entry point for generation agent."""
    if len(sys.argv) < 2:
        print("Usage: python generation_agent.py <classification_output_json>")
        print("\nExample:")
        print('  python generation_agent.py \'{"RAG_response": {...}}\'')
        print("\nOr provide a JSON file:")
        print("  python generation_agent.py classification_output.json")
        sys.exit(1)
    
    # Load classification output
    input_arg = sys.argv[1]
    
    if input_arg.endswith('.json'):
        # Load from file
        with open(input_arg, 'r') as f:
            classification_output = json.load(f)
    else:
        # Parse from command line
        classification_output = json.loads(input_arg)
    
    # Initialize generation agent
    agent = GenerationAgent()
    
    # Generate content
    result = agent.generate(classification_output)
    
    # Pretty print result
    print("\n" + "="*80)
    print("FINAL RESULT")
    print("="*80)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
