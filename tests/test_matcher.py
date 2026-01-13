"""
Quick test of the speaker matcher
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm.speaker_matcher import SpeakerMatcher, load_speakers_from_file


async def test_matcher():
    # Load speakers
    speakers = load_speakers_from_file("data/speakers.json")
    print(f"Loaded {len(speakers)} speakers\n")
    
    # Test user bio
    user_bio = "I sell Counter-Unmanned Aircraft Systems for an Army Air Base"
    
    print(f"User Bio: {user_bio}\n")
    print("Scoring speakers...\n")
    
    # Create matcher and get recommendations
    matcher = SpeakerMatcher()
    matches = await matcher.recommend_speakers(user_bio, speakers, threshold=6.0)
    
    # Display results
    print(f"\n{'='*60}")
    print(f"RESULTS: {len(matches)} matches found")
    print(f"{'='*60}\n")
    
    for idx, match in enumerate(matches[:10], 1):  # Show top 10
        print(f"{idx}. {match['name']} - Score: {match['score']}/10")
        print(f"   Title: {match['title']}")
        print(f"   Org: {match['organization']}")
        print(f"   Reasoning: {match['reasoning']}")
        print()


if __name__ == "__main__":
    asyncio.run(test_matcher())
