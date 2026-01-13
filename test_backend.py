"""
Test the FastAPI backend
"""

import asyncio
import httpx
import json


async def test_backend():
    base_url = "http://localhost:8000"
    
    print("Testing FastAPI Backend")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Health check
        print("\n1. Testing health check (GET /)...")
        try:
            response = await client.get(f"{base_url}/")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
            print("\n   Make sure the backend is running:")
            print("   ./z/start_backend.sh")
            return
        
        # Test 2: Get speakers
        print("\n2. Testing get speakers (GET /speakers)...")
        try:
            response = await client.get(f"{base_url}/speakers")
            data = response.json()
            print(f"   Status: {response.status_code}")
            print(f"   Speakers loaded: {data['count']}")
            if data['count'] > 0:
                print(f"   First speaker: {data['speakers'][0]['name']}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 3: Match speakers
        print("\n3. Testing speaker matching (POST /match)...")
        user_bio = "I sell Counter-Unmanned Aircraft Systems for an Army Air Base"
        threshold = 6.0
        
        print(f"   User bio: {user_bio}")
        print(f"   Threshold: {threshold}")
        print(f"   Sending request (this will take ~30-60 seconds)...")
        
        try:
            response = await client.post(
                f"{base_url}/match",
                json={"user_bio": user_bio, "threshold": threshold},
                timeout=120.0  # 2 minute timeout for LLM calls
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Total speakers: {data['total_speakers']}")
                print(f"   Matches found: {data['matches_found']}")
                
                if data['matches_found'] > 0:
                    print(f"\n   Top 5 matches:")
                    for idx, match in enumerate(data['matches'][:5], 1):
                        print(f"   {idx}. {match['name']} - Score: {match['score']}/10")
                        print(f"      {match['title']}")
                        print(f"      {match['organization']}")
                        print(f"      Reasoning: {match['reasoning'][:100]}...")
                        print()
            else:
                print(f"   Error: {response.text}")
                
        except httpx.TimeoutException:
            print("   Error: Request timed out (LLM calls taking too long)")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    print("Backend test complete!")


if __name__ == "__main__":
    asyncio.run(test_backend())
