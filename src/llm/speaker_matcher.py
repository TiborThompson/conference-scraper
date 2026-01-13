"""
Speaker Recommendation Engine
Sends parallel async requests to LLM to score each speaker individually
"""

import json
import asyncio
from typing import List, Dict, Optional
from .openai_client import OpenAIClient


class SpeakerMatcher:
    """Matches user business context with relevant speakers using parallel LLM scoring."""
    
    def __init__(self):
        """Initialize with OpenAI client."""
        self.llm = OpenAIClient()
    
    def load_speakers(self, filepath: str = "data/speakers.json") -> List[Dict]:
        """Load speakers from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def score_speaker(
        self, 
        user_bio: str,
        speaker: Dict
    ) -> Dict:
        """
        Score a single speaker against user's bio.
        
        Args:
            user_bio: User's business description/goals
            speaker: Speaker dictionary with name, title, org, bio
            
        Returns:
            Dict with speaker info and match score (0-10)
        """
        prompt = f"""You are a strategic business advisor evaluating conference networking opportunities. Be STRICT and SELECTIVE.

USER'S BUSINESS/GOALS:
{user_bio}

SPEAKER:
Name: {speaker.get('name', 'N/A')}
Title: {speaker.get('title', 'N/A')}
Organization: {speaker.get('organization', 'N/A')}
Bio: {speaker.get('bio', 'N/A')[:800]}

EVALUATION CRITERIA (ALL must be considered):

1. DIRECT RELEVANCE (40% weight)
   - Does their work DIRECTLY relate to the user's specific product/service?
   - Is there clear overlap in technology, mission, or market?
   - Would they immediately understand the value proposition?

2. DECISION-MAKING POWER (30% weight)
   - Can they influence purchasing decisions?
   - Do they control budget or procurement?
   - Are they a key stakeholder in relevant programs?

3. ACTIONABLE OPPORTUNITY (20% weight)
   - Is there a concrete business outcome possible (sale, partnership, introduction)?
   - Can this conversation lead to a specific next step?
   - Is the timing right for engagement?

4. MUTUAL BENEFIT (10% weight)
   - Is there value for both parties?
   - Does the user have something they need?

SCORING RULES (be conservative):
- 9-10: EXCEPTIONAL - Direct decision-maker with immediate need for user's offering. Clear path to business outcome.
- 7-8: STRONG - Highly relevant expertise and influence. Likely to lead to concrete opportunity.
- 5-6: MODERATE - Some relevance but indirect. May be useful for information/networking only.
- 3-4: WEAK - Tangential connection. Low probability of business value.
- 0-2: POOR - No meaningful connection. Not worth the conversation time.

BE STRICT: Only give 9-10 if there's EXCEPTIONAL alignment. Most matches should be 5-7.

Return ONLY a JSON object:
{{
  "score": <number 0-10>,
  "reasoning": "<2-3 sentences explaining the score based on criteria above>"
}}"""

        try:
            response = await self.llm.generate_text(prompt)
            result = json.loads(response)
            
            return {
                "name": speaker.get('name'),
                "title": speaker.get('title'),
                "organization": speaker.get('organization'),
                "bio": speaker.get('bio'),
                "score": result.get('score', 0),
                "reasoning": result.get('reasoning', '')
            }
        except Exception as e:
            print(f"Error scoring {speaker.get('name')}: {e}")
            return {
                "name": speaker.get('name'),
                "title": speaker.get('title'),
                "organization": speaker.get('organization'),
                "bio": speaker.get('bio'),
                "score": 0,
                "reasoning": f"Error: {str(e)}"
            }
    
    async def recommend_speakers(
        self, 
        user_bio: str, 
        speakers: List[Dict],
        threshold: float = 6.0
    ) -> List[Dict]:
        """
        Score all speakers in parallel and return ranked matches above threshold.
        
        Args:
            user_bio: User's business description/goals
            speakers: List of speaker dictionaries
            threshold: Minimum score to include (0-10)
            
        Returns:
            List of speakers with scores, sorted by score descending
        """
        # Score all speakers in parallel
        print(f"Scoring {len(speakers)} speakers in parallel...")
        tasks = [self.score_speaker(user_bio, speaker) for speaker in speakers]
        scored_speakers = await asyncio.gather(*tasks)
        
        # Filter by threshold
        matches = [s for s in scored_speakers if s['score'] >= threshold]
        
        # Sort by score descending
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"Found {len(matches)} matches above threshold {threshold}")
        
        return matches


def load_speakers_from_file(filepath: str = "data/speakers.json") -> List[Dict]:
    """Utility function to load speakers."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
