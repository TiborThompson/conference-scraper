"""Anthropic Claude API client for LLM-powered data extraction."""

import os
import json
from typing import Optional, Dict, Any, List
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()


class AnthropicClient:
    """Client for Anthropic Claude API with web scraping utilities."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        temperature: float = 0.1,
        max_tokens: int = 4096
    ):
        """
        Initialize Anthropic client.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model to use (claude-sonnet-4-5-20250929, claude-3-opus-20240229, etc.)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided")
            
        self.client = AsyncAnthropic(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
    async def extract_structured_data(
        self,
        content: str,
        schema: Dict[str, str],
        instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from content using a schema.
        
        Args:
            content: Text content to extract from
            schema: Dictionary describing the fields to extract
                    e.g., {"name": "string", "price": "number", "in_stock": "boolean"}
            instructions: Additional extraction instructions
            
        Returns:
            Dictionary with extracted data
        """
        schema_str = json.dumps(schema, indent=2)
        
        prompt = f"""Extract the following information from the provided content.
Return ONLY a valid JSON object matching this schema:

{schema_str}

{f"Additional instructions: {instructions}" if instructions else ""}

If a field is not found, use null for the value.

Content:
{content[:100000]}  # Claude has large context window
"""
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response.content[0].text
            
            # Extract JSON from response (Claude sometimes adds explanation)
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
                
            return json.loads(result)
            
        except Exception as e:
            raise Exception(f"Error extracting structured data: {str(e)}")
            
    async def summarize(
        self,
        content: str,
        max_length: int = 200,
        style: str = "concise"
    ) -> str:
        """
        Summarize content.
        
        Args:
            content: Text to summarize
            max_length: Maximum length of summary in words
            style: Summary style ("concise", "detailed", "bullet_points")
            
        Returns:
            Summary text
        """
        style_instructions = {
            "concise": "Create a brief, concise summary.",
            "detailed": "Create a comprehensive summary covering all key points.",
            "bullet_points": "Create a bullet-point summary of the main points."
        }
        
        prompt = f"""{style_instructions.get(style, style_instructions['concise'])}
Maximum length: {max_length} words.

Content:
{content[:100000]}
"""
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            raise Exception(f"Error summarizing content: {str(e)}")
            
    async def classify(
        self,
        content: str,
        categories: List[str],
        multi_label: bool = False
    ) -> Dict[str, Any]:
        """
        Classify content into categories.
        
        Args:
            content: Text to classify
            categories: List of possible categories
            multi_label: If True, allow multiple categories; if False, return single category
            
        Returns:
            Dictionary with classification results
        """
        categories_str = ", ".join(categories)
        
        prompt = f"""Classify the following content into {"one or more of" if multi_label else "one of"} these categories:
{categories_str}

Return a JSON object with:
- "categories": {" list of matching categories" if multi_label else "the single best matching category"}
- "confidence": confidence score (0-1)
- "reasoning": brief explanation

Content:
{content[:50000]}
"""
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response.content[0].text
            
            # Extract JSON from response
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
                
            return json.loads(result)
            
        except Exception as e:
            raise Exception(f"Error classifying content: {str(e)}")
            
    async def extract_entities(
        self,
        content: str,
        entity_types: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """
        Extract named entities from content.
        
        Args:
            content: Text to extract entities from
            entity_types: Specific entity types to extract (e.g., ["person", "organization", "location"])
                         If None, extracts all common entity types
            
        Returns:
            Dictionary mapping entity types to lists of entities
        """
        if entity_types:
            entity_instruction = f"Extract only these entity types: {', '.join(entity_types)}"
        else:
            entity_instruction = "Extract all named entities (people, organizations, locations, dates, products, etc.)"
            
        prompt = f"""{entity_instruction}

Return a JSON object where keys are entity types and values are lists of entities found.

Content:
{content[:100000]}
"""
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response.content[0].text
            
            # Extract JSON from response
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
                
            return json.loads(result)
            
        except Exception as e:
            raise Exception(f"Error extracting entities: {str(e)}")
            
    async def answer_question(
        self,
        content: str,
        question: str
    ) -> str:
        """
        Answer a question based on provided content.
        
        Args:
            content: Source content
            question: Question to answer
            
        Returns:
            Answer text
        """
        prompt = f"""Based on the following content, answer this question: {question}

If the answer cannot be found in the content, say "I cannot find this information in the provided content."

Content:
{content[:100000]}
"""
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            raise Exception(f"Error answering question: {str(e)}")
            
    async def clean_html_content(
        self,
        html_content: str
    ) -> str:
        """
        Clean and extract main content from HTML, removing boilerplate.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Cleaned, readable text content
        """
        prompt = f"""Extract the main content from this HTML, removing navigation, ads, footers, and other boilerplate.
Return only the core article/page content in clean, readable text format.

HTML:
{html_content[:100000]}
"""
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            raise Exception(f"Error cleaning HTML content: {str(e)}")


# Example usage
async def main():
    """Example usage of AnthropicClient."""
    client = AnthropicClient()
    
    sample_content = """
    Apple iPhone 15 Pro - $999
    Available in Natural Titanium, Blue Titanium, White Titanium, Black Titanium
    Features: A17 Pro chip, 48MP camera, Action button
    In stock - Ships in 1-2 business days
    """
    
    # Extract structured data
    schema = {
        "product_name": "string",
        "price": "number",
        "colors": "array of strings",
        "in_stock": "boolean"
    }
    
    result = await client.extract_structured_data(sample_content, schema)
    print(f"Extracted data: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
