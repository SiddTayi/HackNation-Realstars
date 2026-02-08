"""
Test script for Generation Agent
Tests the generation agent with sample data
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from generation_agent import GenerationAgent


def test_kb_classification():
    """Test KB classification with actual KB ID from database"""
    print("\n" + "="*80)
    print("TEST 1: KB CLASSIFICATION")
    print("="*80)
    
    classification_output = {
        "RAG_response": {
            "query": "How to troubleshoot login issues?",
            "generated_answer": "Follow these steps to troubleshoot login issues...",
            "ticket_id": "CS-00000001",
            "resolution": {
                "reference_article": {
                    "kb_id": "KB-3FFBFE3C70",
                    "script_id": "None",
                    "generated_kb_id": "None"
                }
            }
        }
    }
    
    try:
        agent = GenerationAgent()
        result = agent.generate(classification_output)
        
        assert result['classification'] == 'KB', "Classification should be KB"
        assert result['generated_content'] is not None, "Should generate content"
        assert 'KB_Article_ID' in result['generated_content'], "Should have KB_Article_ID"
        
        print("\n✓ TEST PASSED")
        print(f"Generated KB Article ID: {result['generated_content']['KB_Article_ID']}")
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_script_classification():
    """Test SCRIPT classification with actual Script ID from database"""
    print("\n" + "="*80)
    print("TEST 2: SCRIPT CLASSIFICATION")
    print("="*80)
    
    classification_output = {
        "RAG_response": {
            "query": "Need a script to update site certifications",
            "generated_answer": "Here's a script for updating certifications...",
            "ticket_id": "CS-00000002",
            "resolution": {
                "reference_article": {
                    "kb_id": "None",
                    "script_id": "SCRIPT-0001",
                    "generated_kb_id": "None"
                }
            }
        }
    }
    
    try:
        agent = GenerationAgent()
        result = agent.generate(classification_output)
        
        assert result['classification'] == 'SCRIPT', "Classification should be SCRIPT"
        assert result['generated_content'] is not None, "Should generate content"
        assert 'script' in result['generated_content'], "Should have script"
        assert 'kb_article' in result['generated_content'], "Should have kb_article"
        
        print("\n✓ TEST PASSED")
        print(f"Generated Script ID: {result['generated_content']['script']['Script_ID']}")
        print(f"Generated KB Article ID: {result['generated_content']['kb_article']['KB_Article_ID']}")
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_resolution_classification():
    """Test RESOLUTION classification (no IDs)"""
    print("\n" + "="*80)
    print("TEST 3: RESOLUTION CLASSIFICATION")
    print("="*80)
    
    classification_output = {
        "RAG_response": {
            "query": "What are the system requirements?",
            "generated_answer": "System requires Windows 10, 8GB RAM...",
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
    
    try:
        agent = GenerationAgent()
        result = agent.generate(classification_output)
        
        assert result['classification'] == 'RESOLUTION', "Classification should be RESOLUTION"
        assert result['generated_content'] is not None, "Should have content"
        assert 'answer' in result['generated_content'], "Should have answer"
        
        print("\n✓ TEST PASSED")
        print(f"Answer: {result['generated_content']['answer'][:60]}...")
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_initialization():
    """Test agent initialization"""
    print("\n" + "="*80)
    print("TEST 0: AGENT INITIALIZATION")
    print("="*80)
    
    try:
        agent = GenerationAgent()
        assert agent.client is not None, "OpenAI client should be initialized"
        assert agent.api_key is not None, "API key should be loaded"
        
        print("\n✓ TEST PASSED")
        print("Agent initialized successfully")
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "#"*80)
    print("GENERATION AGENT TEST SUITE")
    print("#"*80)
    
    results = []
    
    # Test 0: Initialization
    results.append(("Initialization", test_agent_initialization()))
    
    # Test 1: KB Classification
    results.append(("KB Classification", test_kb_classification()))
    
    # Test 2: Script Classification
    results.append(("Script Classification", test_script_classification()))
    
    # Test 3: Resolution Classification
    results.append(("Resolution Classification", test_resolution_classification()))
    
    # Summary
    print("\n" + "#"*80)
    print("TEST SUMMARY")
    print("#"*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("#"*80)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
