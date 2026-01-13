"""
SOFWeek Conference Scraper
Scrapes speaker names and bios from https://sofweek.org/agenda/
"""

import asyncio
import json
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeout


class ConferenceScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.url = "https://sofweek.org/agenda/"
        self.speakers = []
        
    async def scrape_speakers(self) -> List[Dict[str, str]]:
        """
        Main scraping function to extract all speakers with their bios.
        
        Returns:
            List[Dict]: [{"name": "...", "title": "...", "bio": "..."}]
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()
            
            try:
                print(f"Navigating to {self.url}...")
                await page.goto(self.url, wait_until="networkidle", timeout=60000)
                await page.wait_for_timeout(3000)  # Wait for page to fully load
                
                # The agenda is in a Cvent iframe - we need to switch to it!
                print("\nLooking for Cvent iframe...")
                iframe_element = await page.wait_for_selector('iframe.cvt-embed', timeout=10000)
                iframe = await iframe_element.content_frame()
                
                if not iframe:
                    print("ERROR: Could not access iframe content")
                    return []
                
                print("Successfully accessed iframe!")
                await iframe.wait_for_timeout(3000)  # Wait for iframe content to load
                
                # Now work within the iframe context
                print("\nLooking for 'All Dates' section in iframe...")
                await self._scroll_all_dates_section(iframe)
                
                # Find all speaker profile elements in the iframe
                print("\nFinding speaker profiles in iframe...")
                speaker_elements = await self._find_speaker_elements(iframe)
                print(f"Found {len(speaker_elements)} speaker elements")
                
                # Process all speakers
                print(f"Processing all {len(speaker_elements)} speakers...")
                
                # Click each speaker and extract their bio
                for idx, element in enumerate(speaker_elements):
                    print(f"\nProcessing speaker {idx + 1}/{len(speaker_elements)}...")
                    speaker_data = await self._extract_speaker_data(iframe, element, idx)
                    if speaker_data:
                        self.speakers.append(speaker_data)
                        print(f"  ✓ Extracted: {speaker_data['name']}")
                        print(f"     Title: {speaker_data.get('title', 'N/A')[:50]}...")
                        print(f"     Org: {speaker_data.get('organization', 'N/A')[:50]}...")
                    
                    await iframe.wait_for_timeout(1000)  # Delay between clicks
                
                print(f"\n\nTotal speakers scraped: {len(self.speakers)}")
                
            except Exception as e:
                print(f"Error during scraping: {e}")
                import traceback
                traceback.print_exc()
            
            finally:
                await browser.close()
        
        return self.speakers
    
    async def _explore_page_structure(self, page: Page):
        """Explore the page to understand its structure."""
        # Get all clickable elements that might be speaker profiles
        result = await page.evaluate("""
            () => {
                // Look for common patterns in speaker profile elements
                const images = document.querySelectorAll('img');
                const imageInfo = Array.from(images).slice(0, 20).map(img => ({
                    src: img.src,
                    alt: img.alt,
                    classes: img.className,
                    parent: img.parentElement?.tagName
                }));
                
                // Look for elements with "speaker" in class or id
                const speakerElements = document.querySelectorAll('[class*="speaker"], [id*="speaker"]');
                
                return {
                    totalImages: images.length,
                    sampleImages: imageInfo,
                    speakerElementsCount: speakerElements.length
                };
            }
        """)
        print(f"Page structure: {json.dumps(result, indent=2)}")
    
    async def _scroll_all_dates_section(self, frame: Page):
        """Scroll through the 'All Dates' section in the iframe to load all events."""
        try:
            # Try to find and click "All Dates" tab if not already selected
            all_dates_button = frame.locator('text="All Dates"').first
            try:
                if await all_dates_button.is_visible(timeout=3000):
                    await all_dates_button.click()
                    await frame.wait_for_timeout(2000)
                    print("Clicked 'All Dates' tab")
            except:
                print("All Dates tab not found or already selected")
            
            # Scroll within the iframe to load all events
            print("Scrolling within iframe to load all events...")
            
            # Scroll multiple times to ensure all content is loaded
            for i in range(15):  # Scroll 15 times
                await frame.evaluate("window.scrollBy(0, 800)")
                await frame.wait_for_timeout(500)
                print(f"  Scroll {i+1}/15...")
            
            # Scroll back to top
            await frame.evaluate("window.scrollTo(0, 0)")
            await frame.wait_for_timeout(1000)
            
            print("Finished scrolling - all events should be loaded")
            
        except Exception as e:
            print(f"Note: Error during scrolling: {e}")
    
    async def _find_speaker_elements(self, frame: Page) -> List:
        """Find all clickable speaker profile elements in the iframe."""
        print("Searching for speaker profile images with Cvent class...")
        
        # Use the exact class from the Cvent iframe
        selector = 'img.AgendaV2Styles__speakerProfileImageBox___9256, img[data-cvent-id="speaker-card-user-profile-image"]'
        
        try:
            elements = await frame.locator(selector).all()
            print(f"Found {len(elements)} speaker profile images")
            
            # Show some info about what we found
            for i, element in enumerate(elements[:5]):
                try:
                    src = await element.get_attribute('src')
                    print(f"  Speaker {i+1}: {src[:80]}...")
                except:
                    pass
            
            return elements
            
        except Exception as e:
            print(f"Error finding speaker elements: {e}")
            return []
    
    async def _extract_speaker_data(
        self, 
        frame: Page, 
        element, 
        idx: int
    ) -> Optional[Dict[str, str]]:
        """
        Click a speaker element and extract their bio from the popup.
        
        Returns:
            Dict with keys: name, title, bio
        """
        try:
            # Ensure any previous popup is closed
            try:
                close_btn = frame.locator('[data-cvent-id="close"]').first
                if await close_btn.is_visible(timeout=1000):
                    await close_btn.click()
                    await frame.wait_for_timeout(1500)
            except:
                pass
            
            # STEP 1: Get name, title, org from the speaker card (BEFORE clicking)
            # Find the parent speaker card container
            speaker_card_data = await element.evaluate("""
                (img) => {
                    // The img is inside the speaker card, go up to find the card container
                    const card = img.closest('.AgendaV2Styles__speakerCard___9256');
                    
                    if (!card) return null;
                    
                    // Find the elements within this specific card
                    const nameEl = card.querySelector('[data-cvent-id="speaker-name"]');
                    const titleEl = card.querySelector('[data-cvent-id="speaker-card-speaker-info-speaker-title"]');
                    const orgEl = card.querySelector('[data-cvent-id="speaker-card-speaker-info-speaker-company"]');
                    
                    return {
                        name: nameEl ? nameEl.textContent?.trim() : '',
                        title: titleEl ? titleEl.textContent?.trim() : '',
                        organization: orgEl ? orgEl.textContent?.trim() : ''
                    };
                }
            """)
            
            if not speaker_card_data or not speaker_card_data.get('name'):
                print(f"  Warning: Could not extract speaker info from card")
                return None
            
            print(f"  Card data: {speaker_card_data['name']}")
            
            # STEP 2: Click to open modal and get bio
            await element.scroll_into_view_if_needed()
            await frame.wait_for_timeout(500)
            await element.click()
            
            # Wait for modal to open
            await frame.wait_for_timeout(2000)
            
            # STEP 3: Extract ONLY the bio from the modal
            bio_data = await frame.evaluate("""
                () => {
                    const bioEl = document.querySelector('.AgendaV2Styles__speakerModalBio___9256');
                    return {
                        bio: bioEl ? bioEl.textContent?.trim() : ''
                    };
                }
            """)
            
            # Combine card data with bio from modal
            if speaker_card_data and bio_data:
                speaker_info = {
                    "name": speaker_card_data.get('name', '').strip(),
                    "title": speaker_card_data.get('title', '').strip(),
                    "organization": speaker_card_data.get('organization', '').strip(),
                    "bio": bio_data.get('bio', '').strip()
                }
                
                # Close the popup using the specific Cvent close button
                try:
                    # Use the exact Cvent close button selector
                    close_button = frame.locator('[data-cvent-id="close"]').first
                    
                    # Wait for close button to be visible and click it
                    await close_button.wait_for(state="visible", timeout=3000)
                    await close_button.click()
                    
                    # Wait and verify the modal is completely gone
                    await frame.wait_for_timeout(500)
                    
                    # Check that the speaker name element is no longer visible (modal closed)
                    try:
                        speaker_name_el = frame.locator('[data-cvent-id="speaker-name"]').first
                        await speaker_name_el.wait_for(state="hidden", timeout=3000)
                    except:
                        # If modal still visible, try closing again
                        try:
                            if await close_button.is_visible(timeout=500):
                                await close_button.click()
                                await frame.wait_for_timeout(1000)
                        except:
                            pass
                    
                    # Final wait to ensure everything is settled
                    await frame.wait_for_timeout(1000)
                        
                except Exception as e:
                    print(f"  Warning: Error closing popup: {e}")
                    # Fallback: try Escape key
                    try:
                        await frame.keyboard.press('Escape')
                        await frame.wait_for_timeout(1500)
                    except:
                        pass
                
                return speaker_info
            
        except Exception as e:
            print(f"  Error extracting speaker {idx}: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def save_to_json(self, filename: str = "data/speakers.json"):
        """Save scraped speakers to JSON file."""
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.speakers, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved {len(self.speakers)} speakers to {filename}")


async def main():
    """Run the scraper."""
    scraper = ConferenceScraper(headless=False)  # Set to False to see what's happening
    speakers = await scraper.scrape_speakers()
    
    if speakers:
        scraper.save_to_json()
        
        # Print summary
        print("\n" + "="*60)
        print("SCRAPING COMPLETE")
        print("="*60)
        print(f"\nTotal speakers: {len(speakers)}")
        print("\nSample speakers:")
        for speaker in speakers[:3]:
            print(f"\n  Name: {speaker['name']}")
            print(f"  Title: {speaker['title']}")
            print(f"  Bio: {speaker['bio'][:100]}...")
    else:
        print("\nNo speakers found. The page structure may have changed.")


if __name__ == "__main__":
    asyncio.run(main())
