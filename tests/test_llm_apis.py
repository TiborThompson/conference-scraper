"""
Test script to verify OpenAI and Anthropic API keys work correctly.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load .env from project root
from dotenv import load_dotenv
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

from src.llm.openai_client import OpenAIClient
from src.llm.anthropic_client import AnthropicClient


async def test_openai():
    """Test OpenAI API with a simple extraction."""
    print("\n" + "=" * 60)
    print("Testing OpenAI API")
    print("=" * 60)
    
    try:
        client = OpenAIClient()
        print("OpenAI client initialized successfully")
        
        # Simple test content
        test_content = """
        Apple iPhone 15 Pro
        Price: $999.00
        Rating: 4.8 out of 5 stars
        In Stock
        """
        
        schema = {
            "product_name": "string",
            "price": "number",
            "rating": "number",
            "in_stock": "boolean"
        }
        
        print("\nSending test request to OpenAI...")
        result = await client.extract_structured_data(
            content=test_content,
            schema=schema
        )
        
        print("\nSUCCESS - OpenAI API is working!")
        print("\nExtracted data:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        
        return True
        
    except ValueError as e:
        print(f"\nERROR: {e}")
        print("Make sure OPENAI_API_KEY is set in your .env file")
        return False
    except Exception as e:
        print(f"\nERROR: {e}")
        print("OpenAI API call failed")
        return False


async def test_anthropic():
    """Test Anthropic API with a simple extraction."""
    print("\n" + "=" * 60)
    print("Testing Anthropic API")
    print("=" * 60)
    
    try:
        client = AnthropicClient()
        print("Anthropic client initialized successfully")
        
        # Simple test content
        test_content = """
        Sony WH-1000XM5 Headphones
        Price: $399.99
        Rating: 4.7 out of 5 stars
        Available for shipping
        """
        
        schema = {
            "product_name": "string",
            "price": "number",
            "rating": "number",
            "available": "boolean"
        }
        
        print("\nSending test request to Anthropic...")
        result = await client.extract_structured_data(
            content=test_content,
            schema=schema
        )
        
        print("\nSUCCESS - Anthropic API is working!")
        print("\nExtracted data:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        
        return True
        
    except ValueError as e:
        print(f"\nERROR: {e}")
        print("Make sure ANTHROPIC_API_KEY is set in your .env file")
        return False
    except Exception as e:
        print(f"\nERROR: {e}")
        print("Anthropic API call failed")
        return False


async def test_openai_summarization():
    """Test OpenAI summarization."""
    print("\n" + "=" * 60)
    print("Testing OpenAI Summarization")
    print("=" * 60)
    
    try:
        client = OpenAIClient()
        
        test_content = """
        Artificial intelligence has made remarkable progress in recent years.
        Large language models can now understand and generate human-like text,
        perform complex reasoning tasks, and assist with a wide variety of applications
        from customer service to scientific research. However, challenges remain
        in areas like hallucinations, bias, and computational costs.
        """
        
        print("\nSending summarization request to OpenAI...")
        summary = await client.summarize(test_content, max_length=50, style="concise")
        
        print("\nSUCCESS - OpenAI Summarization is working!")
        print(f"\nSummary: {summary}")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        return False


async def test_anthropic_classification():
    """Test Anthropic classification."""
    print("\n" + "=" * 60)
    print("Testing Anthropic Classification")
    print("=" * 60)
    
    try:
        client = AnthropicClient()
        
        test_content = """
        The new MacBook Pro features the M3 Pro chip with up to 12-core CPU.
        It includes a stunning Liquid Retina XDR display and up to 22 hours of battery life.
        """
        
        categories = ["Electronics", "Clothing", "Books", "Food", "Sports"]
        
        print("\nSending classification request to Anthropic...")
        result = await client.classify(test_content, categories)
        
        print("\nSUCCESS - Anthropic Classification is working!")
        print(f"\nCategory: {result.get('categories')}")
        print(f"Confidence: {result.get('confidence')}")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        return False


async def main():
    """Run all API tests."""
    print("\n" + "=" * 60)
    print("LLM API Integration Tests")
    print("=" * 60)
    print("\nThis will test your API keys and verify the integrations work.")
    print("Each test makes a real API call (costs a few cents total).")
    
    results = {
        "OpenAI Basic": False,
        "OpenAI Summarization": False,
        "Anthropic Basic": False,
        "Anthropic Classification": False
    }
    
    # Test OpenAI
    results["OpenAI Basic"] = await test_openai()
    
    if results["OpenAI Basic"]:
        results["OpenAI Summarization"] = await test_openai_summarization()
    
    # Test Anthropic
    results["Anthropic Basic"] = await test_anthropic()
    
    if results["Anthropic Basic"]:
        results["Anthropic Classification"] = await test_anthropic_classification()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("All tests passed! Your API integrations are working correctly.")
    else:
        print("Some tests failed. Check the errors above.")
    print("=" * 60)
    print()
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
