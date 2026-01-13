"""
Centralized LLM prompts for web scraping and data extraction.

All prompts are stored here for easy modification and testing.
"""

import json
from typing import Dict, Optional


class PromptTemplates:
    """Collection of prompt templates for LLM operations."""
    
    @staticmethod
    def structured_extraction(schema: Dict[str, str], content: str, instructions: Optional[str] = None) -> str:
        """
        Generate prompt for structured data extraction.
        
        Args:
            schema: Dictionary describing fields to extract
            content: Content to extract from
            instructions: Additional extraction instructions
            
        Returns:
            Formatted prompt string
        """
        schema_str = json.dumps(schema, indent=2)
        
        prompt = f"""Extract the following information from the provided content.
Return ONLY a valid JSON object matching this schema:

{schema_str}

{f"Additional instructions: {instructions}" if instructions else ""}

If a field is not found, use null for the value.

Content:
{content}"""
        
        return prompt
    
    @staticmethod
    def summarization(content: str, max_length: int = 200, style: str = "concise") -> str:
        """
        Generate prompt for content summarization.
        
        Args:
            content: Text to summarize
            max_length: Maximum length in words
            style: Summary style (concise, detailed, bullet_points)
            
        Returns:
            Formatted prompt string
        """
        style_instructions = {
            "concise": "Create a brief, concise summary.",
            "detailed": "Create a comprehensive summary covering all key points.",
            "bullet_points": "Create a bullet-point summary of the main points."
        }
        
        instruction = style_instructions.get(style, style_instructions['concise'])
        
        prompt = f"""{instruction}
Maximum length: {max_length} words.

Content:
{content}"""
        
        return prompt
    
    @staticmethod
    def classification(content: str, categories: list[str], multi_label: bool = False) -> str:
        """
        Generate prompt for content classification.
        
        Args:
            content: Text to classify
            categories: List of possible categories
            multi_label: Allow multiple categories
            
        Returns:
            Formatted prompt string
        """
        categories_str = ", ".join(categories)
        
        prompt = f"""Classify the following content into {"one or more of" if multi_label else "one of"} these categories:
{categories_str}

Return a JSON object with:
- "categories": {"list of matching categories" if multi_label else "the single best matching category"}
- "confidence": confidence score (0-1)
- "reasoning": brief explanation

Content:
{content}"""
        
        return prompt
    
    @staticmethod
    def entity_extraction(content: str, entity_types: Optional[list[str]] = None) -> str:
        """
        Generate prompt for named entity extraction.
        
        Args:
            content: Text to extract entities from
            entity_types: Specific entity types to extract
            
        Returns:
            Formatted prompt string
        """
        if entity_types:
            entity_instruction = f"Extract only these entity types: {', '.join(entity_types)}"
        else:
            entity_instruction = "Extract all named entities (people, organizations, locations, dates, products, etc.)"
        
        prompt = f"""{entity_instruction}

Return a JSON object where keys are entity types and values are lists of entities found.

Content:
{content}"""
        
        return prompt
    
    @staticmethod
    def question_answering(content: str, question: str) -> str:
        """
        Generate prompt for question answering.
        
        Args:
            content: Source content
            question: Question to answer
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Based on the following content, answer this question: {question}

If the answer cannot be found in the content, say "I cannot find this information in the provided content."

Content:
{content}"""
        
        return prompt
    
    @staticmethod
    def html_cleaning(html_content: str) -> str:
        """
        Generate prompt for cleaning HTML content.
        
        Args:
            html_content: Raw HTML to clean
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Extract the main content from this HTML, removing navigation, ads, footers, and other boilerplate.
Return only the core article/page content in clean, readable text format.

HTML:
{html_content}"""
        
        return prompt
    
    @staticmethod
    def speaker_recommendation(user_context: str, speakers: list, top_n: int = 10) -> str:
        """
        Generate prompt for speaker recommendations.
        
        Args:
            user_context: User's business description/goals
            speakers: List of speaker dictionaries
            top_n: Number of recommendations
            
        Returns:
            Formatted prompt string
        """
        # Format speakers for the prompt (truncate bios for token efficiency)
        speakers_formatted = []
        for idx, speaker in enumerate(speakers, 1):
            bio_preview = speaker.get('bio', '')[:300] + '...' if len(speaker.get('bio', '')) > 300 else speaker.get('bio', '')
            speakers_formatted.append(f"""
Speaker {idx}:
Name: {speaker.get('name', 'N/A')}
Title: {speaker.get('title', 'N/A')}
Organization: {speaker.get('organization', 'N/A')}
Bio: {bio_preview}
""")
        
        speakers_text = "\n".join(speakers_formatted)
        
        prompt = f"""You are a conference networking assistant helping attendees identify the most relevant speakers to talk to for business purposes.

USER'S BUSINESS CONTEXT:
{user_context}

AVAILABLE SPEAKERS:
{speakers_text}

TASK:
Analyze each speaker's background and recommend the top {top_n} speakers this person should prioritize talking to at the conference.

EVALUATION CRITERIA:
- Relevant expertise and background
- Potential business synergy or partnership opportunities
- Decision-making authority and influence
- Complementary vs competitive positioning
- Shared interests or mission alignment

OUTPUT FORMAT:
Return a JSON object with this structure:
{{
  "recommendations": [
    {{
      "name": "Speaker Name",
      "rank": 1,
      "relevance_score": 0.95,
      "reasoning": "Detailed explanation of why this speaker is relevant",
      "talking_points": ["Point 1", "Point 2", "Point 3"],
      "potential_outcomes": "What could come from this conversation"
    }}
  ]
}}

Return ONLY valid JSON. Include exactly {top_n} recommendations, ranked from most to least relevant."""
        
        return prompt


class SystemPrompts:
    """System prompts for different LLM roles."""
    
    DATA_EXTRACTION = "You are a data extraction assistant. Always respond with valid JSON."
    
    SUMMARIZATION = "You are a summarization assistant. Create clear, concise summaries."
    
    CLASSIFICATION = "You are a classification assistant. Always respond with valid JSON."
    
    ENTITY_EXTRACTION = "You are an entity extraction assistant. Always respond with valid JSON."
    
    QUESTION_ANSWERING = "You are a helpful assistant that answers questions based on provided content."
    
    HTML_CLEANING = "You are a content extraction assistant. Extract main content from HTML."


class ProductExtractionPrompts:
    """Specialized prompts for e-commerce product scraping."""
    
    @staticmethod
    def product_schema() -> Dict[str, str]:
        """Standard product extraction schema."""
        return {
            "name": "string - product name",
            "price": "number - price in dollars",
            "currency": "string - currency code (USD, EUR, etc.)",
            "description": "string - brief product description",
            "brand": "string - brand name",
            "in_stock": "boolean - availability",
            "rating": "number - rating out of 5",
            "review_count": "number - number of reviews",
            "features": "array of strings - key features",
            "specifications": "object - technical specifications",
            "images": "array of strings - image URLs"
        }
    
    @staticmethod
    def product_extraction(content: str) -> str:
        """Generate prompt for product data extraction."""
        schema = ProductExtractionPrompts.product_schema()
        return PromptTemplates.structured_extraction(
            schema=schema,
            content=content,
            instructions="Focus on extracting accurate pricing and availability information."
        )


class ArticleExtractionPrompts:
    """Specialized prompts for news/article scraping."""
    
    @staticmethod
    def article_schema() -> Dict[str, str]:
        """Standard article extraction schema."""
        return {
            "headline": "string - article headline",
            "author": "string - author name",
            "published_date": "string - publication date",
            "summary": "string - brief summary",
            "key_points": "array of strings - main points",
            "category": "string - article category",
            "tags": "array of strings - relevant tags"
        }
    
    @staticmethod
    def article_extraction(content: str) -> str:
        """Generate prompt for article data extraction."""
        schema = ArticleExtractionPrompts.article_schema()
        return PromptTemplates.structured_extraction(
            schema=schema,
            content=content,
            instructions="Extract the main article content, ignoring ads and navigation."
        )


class JobListingPrompts:
    """Specialized prompts for job listing scraping."""
    
    @staticmethod
    def job_schema() -> Dict[str, str]:
        """Standard job listing extraction schema."""
        return {
            "job_title": "string - job title",
            "company": "string - company name",
            "location": "string - job location",
            "salary_range": "string - salary range if available",
            "employment_type": "string - full-time, part-time, contract, etc.",
            "requirements": "array of strings - job requirements",
            "responsibilities": "array of strings - job responsibilities",
            "benefits": "array of strings - benefits offered",
            "posted_date": "string - posting date",
            "application_deadline": "string - deadline if available"
        }
    
    @staticmethod
    def job_extraction(content: str) -> str:
        """Generate prompt for job listing data extraction."""
        schema = JobListingPrompts.job_schema()
        return PromptTemplates.structured_extraction(
            schema=schema,
            content=content,
            instructions="Extract all relevant job details including requirements and benefits."
        )


# Quick access to common prompts
def get_prompt(prompt_type: str, **kwargs) -> str:
    """
    Get a prompt by type with parameters.
    
    Args:
        prompt_type: Type of prompt (extraction, summarization, etc.)
        **kwargs: Parameters for the prompt
        
    Returns:
        Formatted prompt string
        
    Example:
        prompt = get_prompt('extraction', schema={...}, content="...")
    """
    prompt_map = {
        'extraction': PromptTemplates.structured_extraction,
        'summarization': PromptTemplates.summarization,
        'classification': PromptTemplates.classification,
        'entities': PromptTemplates.entity_extraction,
        'qa': PromptTemplates.question_answering,
        'html_clean': PromptTemplates.html_cleaning,
        'product': ProductExtractionPrompts.product_extraction,
        'article': ArticleExtractionPrompts.article_extraction,
        'job': JobListingPrompts.job_extraction,
    }
    
    if prompt_type not in prompt_map:
        raise ValueError(f"Unknown prompt type: {prompt_type}")
    
    return prompt_map[prompt_type](**kwargs)
