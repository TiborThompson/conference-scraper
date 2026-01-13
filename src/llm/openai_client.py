"""OpenAI API client for LLM-powered data extraction."""

import os
import json
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI
from dotenv import load_dotenv
from .prompts import PromptTemplates, SystemPrompts

load_dotenv()


class OpenAIClient:
    """Client for OpenAI API with web scraping utilities."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4.1",
        temperature: float = 0.1
    ):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use (gpt-4.1, gpt-4-turbo-preview, gpt-3.5-turbo, etc.)
            temperature: Sampling temperature (0-2)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
            
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        
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
        # Limit content length for token efficiency
        limited_content = content[:8000]
        
        prompt = PromptTemplates.structured_extraction(
            schema=schema,
            content=limited_content,
            instructions=instructions
        )
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SystemPrompts.DATA_EXTRACTION},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
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
        limited_content = content[:10000]
        
        prompt = PromptTemplates.summarization(
            content=limited_content,
            max_length=max_length,
            style=style
        )
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SystemPrompts.SUMMARIZATION},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
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
{content[:5000]}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a classification assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
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
{content[:8000]}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an entity extraction assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
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
{content[:10000]}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Error answering question: {str(e)}")
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Generated text
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Error generating text: {str(e)}")


# Example usage
async def main():
    """Example usage of OpenAIClient."""
    client = OpenAIClient()
    
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
