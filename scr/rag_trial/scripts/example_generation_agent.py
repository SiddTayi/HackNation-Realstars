"""
Example usage of the Generation Agent
Demonstrates how to use the generation agent with different classification types
"""

import json
from generation_agent import GenerationAgent


def example_kb_classification():
    """Example: KB Classification - Generate new KB article"""
    print("\n" + "="*80)
    print("EXAMPLE 1: KB CLASSIFICATION")
    print("="*80)
    
    # Simulated classification output with KB reference
    classification_output = {
        "RAG_response": {
            "query": "How do I reset a user's password in the system?",
            "generated_answer": "To reset a user's password, follow the steps in the knowledge base...",
            "ticket_id": "CS-00000001",
            "resolution": {
                "reference_article": {
                    "kb_id": "KB-3FFBFE3C70",  # Existing KB ID
                    "script_id": "None",
                    "generated_kb_id": "None"
                }
            }
        }
    }
    
    # Initialize generation agent
    agent = GenerationAgent()
    
    # Generate new KB article
    result = agent.generate(classification_output)
    
    # Display result
    print("\nResult:")
    print(json.dumps(result, indent=2, default=str))


def example_script_classification():
    """Example: SCRIPT Classification - Generate script and KB article"""
    print("\n" + "="*80)
    print("EXAMPLE 2: SCRIPT CLASSIFICATION")
    print("="*80)
    
    # Simulated classification output with Script reference
    classification_output = {
        "RAG_response": {
            "query": "I need a script to update compliance certifications for all sites",
            "generated_answer": "Here's a script that can help you update compliance certifications...",
            "ticket_id": "CS-00000002",
            "resolution": {
                "reference_article": {
                    "kb_id": "KB-SYN-0161",  # Optional KB reference
                    "script_id": "SCRIPT-0001",  # Script reference
                    "generated_kb_id": "None"
                }
            }
        }
    }
    
    # Initialize generation agent
    agent = GenerationAgent()
    
    # Generate new script and KB article
    result = agent.generate(classification_output)
    
    # Display result
    print("\nResult:")
    print(json.dumps(result, indent=2, default=str))


def example_resolution_classification():
    """Example: RESOLUTION Classification - No new generation needed"""
    print("\n" + "="*80)
    print("EXAMPLE 3: RESOLUTION CLASSIFICATION")
    print("="*80)
    
    # Simulated classification output with no references (resolution only)
    classification_output = {
        "RAG_response": {
            "query": "What are the system requirements for the latest version?",
            "generated_answer": "The system requires Windows 10 or higher, 8GB RAM, and 50GB disk space...",
            "ticket_id": "CS-00000003",
            "resolution": {
                "reference_article": {
                    "kb_id": "None",
                    "script_id": "None",
                    "generated_kb_id": "None"
                }
            }
        }
    }
    
    # Initialize generation agent
    agent = GenerationAgent()
    
    # Process resolution (no generation needed)
    result = agent.generate(classification_output)
    
    # Display result
    print("\nResult:")
    print(json.dumps(result, indent=2, default=str))


def example_with_classification_agent():
    """Example: Full pipeline with classification agent"""
    print("\n" + "="*80)
    print("EXAMPLE 4: FULL PIPELINE (Classification → Generation)")
    print("="*80)
    
    try:
        from classification_agent import ClassificationAgent
        
        # Initialize agents
        classifier = ClassificationAgent()
        generator = GenerationAgent()
        
        # User query
        query = "How to configure email notifications for ticket updates"
        
        print(f"\nQuery: {query}")
        print("\nStep 1: Running classification agent...")
        
        # Get classification
        classification_result = classifier.classify_query(query, top_k=3)
        
        print("\nStep 2: Running generation agent...")
        
        # Generate content based on classification
        generation_result = generator.generate(classification_result)
        
        # Display final result
        print("\nFinal Result:")
        print(f"Classification: {generation_result['classification']}")
        print(f"Message: {generation_result['message']}")
        
        if generation_result['generated_content']:
            print("\nGenerated Content:")
            print(json.dumps(generation_result['generated_content'], indent=2, default=str))
        
    except Exception as e:
        print(f"\nError: {e}")
        print("Note: This example requires the classification agent and vector store to be set up")


def main():
    """Run all examples"""
    print("\n" + "#"*80)
    print("GENERATION AGENT EXAMPLES")
    print("#"*80)
    
    # Run examples
    try:
        # Example 1: KB Classification
        example_kb_classification()
    except Exception as e:
        print(f"\nExample 1 Error: {e}")
    
    input("\nPress Enter to continue to Example 2...")
    
    try:
        # Example 2: Script Classification
        example_script_classification()
    except Exception as e:
        print(f"\nExample 2 Error: {e}")
    
    input("\nPress Enter to continue to Example 3...")
    
    try:
        # Example 3: Resolution Classification
        example_resolution_classification()
    except Exception as e:
        print(f"\nExample 3 Error: {e}")
    
    input("\nPress Enter to continue to Example 4...")
    
    try:
        # Example 4: Full Pipeline
        example_with_classification_agent()
    except Exception as e:
        print(f"\nExample 4 Error: {e}")
    
    print("\n" + "#"*80)
    print("EXAMPLES COMPLETE")
    print("#"*80)


if __name__ == "__main__":
    main()
