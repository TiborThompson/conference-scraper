"""Playwright-based web scraper for dynamic content."""

import asyncio
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page, TimeoutError
import os
from dotenv import load_dotenv

load_dotenv()


class PlaywrightScraper:
    """Async web scraper using Playwright for JavaScript-rendered content."""
    
    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,
        user_agent: Optional[str] = None
    ):
        """
        Initialize the Playwright scraper.
        
        Args:
            headless: Run browser in headless mode
            timeout: Default timeout in milliseconds
            user_agent: Custom user agent string
        """
        self.headless = headless if headless is not None else os.getenv("HEADLESS", "true").lower() == "true"
        self.timeout = timeout or int(os.getenv("TIMEOUT", "30000"))
        self.user_agent = user_agent or os.getenv("USER_AGENT")
        self.playwright = None
        self.browser: Optional[Browser] = None
        
    async def __aenter__(self):
        """Context manager entry."""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()
        
    async def start(self):
        """Start the browser instance."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        
    async def close(self):
        """Close the browser and playwright instance."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    async def scrape(
        self,
        url: str,
        wait_for_selector: Optional[str] = None,
        wait_for_timeout: Optional[int] = None,
        screenshot: bool = False
    ) -> str:
        """
        Scrape a URL and return the HTML content.
        
        Args:
            url: URL to scrape
            wait_for_selector: CSS selector to wait for before extracting content
            wait_for_timeout: Additional timeout after page load (ms)
            screenshot: Take a screenshot (saved as screenshot.png)
            
        Returns:
            HTML content as string
        """
        if not self.browser:
            await self.start()
            
        page = await self.browser.new_page(
            user_agent=self.user_agent if self.user_agent else None
        )
        
        try:
            # Navigate to URL
            await page.goto(url, timeout=self.timeout, wait_until="networkidle")
            
            # Wait for specific selector if provided
            if wait_for_selector:
                await page.wait_for_selector(wait_for_selector, timeout=self.timeout)
                
            # Additional wait if specified
            if wait_for_timeout:
                await page.wait_for_timeout(wait_for_timeout)
                
            # Take screenshot if requested
            if screenshot:
                await page.screenshot(path="screenshot.png")
                
            # Get page content
            content = await page.content()
            return content
            
        except TimeoutError as e:
            raise Exception(f"Timeout while loading {url}: {str(e)}")
        except Exception as e:
            raise Exception(f"Error scraping {url}: {str(e)}")
        finally:
            await page.close()
            
    async def scrape_with_interaction(
        self,
        url: str,
        interactions: list[Dict[str, Any]]
    ) -> str:
        """
        Scrape a page with user interactions (clicks, typing, etc.).
        
        Args:
            url: URL to scrape
            interactions: List of interaction dictionaries with keys:
                - action: "click", "type", "select", "wait"
                - selector: CSS selector (for click, type, select)
                - value: Value to type or select
                - timeout: Wait time in ms
                
        Returns:
            HTML content after interactions
            
        Example:
            interactions = [
                {"action": "click", "selector": "#load-more"},
                {"action": "wait", "timeout": 2000},
                {"action": "type", "selector": "#search", "value": "query"}
            ]
        """
        if not self.browser:
            await self.start()
            
        page = await self.browser.new_page(
            user_agent=self.user_agent if self.user_agent else None
        )
        
        try:
            await page.goto(url, timeout=self.timeout, wait_until="networkidle")
            
            # Execute interactions
            for interaction in interactions:
                action = interaction.get("action")
                selector = interaction.get("selector")
                value = interaction.get("value")
                timeout = interaction.get("timeout", 1000)
                
                if action == "click":
                    await page.click(selector)
                    await page.wait_for_timeout(500)  # Brief pause after click
                    
                elif action == "type":
                    await page.fill(selector, value)
                    
                elif action == "select":
                    await page.select_option(selector, value)
                    
                elif action == "wait":
                    await page.wait_for_timeout(timeout)
                    
                elif action == "wait_for_selector":
                    await page.wait_for_selector(selector, timeout=timeout)
                    
            # Get final content
            content = await page.content()
            return content
            
        except Exception as e:
            raise Exception(f"Error during interaction scraping: {str(e)}")
        finally:
            await page.close()
            
    async def extract_data(
        self,
        url: str,
        selectors: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Extract specific data using CSS selectors.
        
        Args:
            url: URL to scrape
            selectors: Dictionary mapping field names to CSS selectors
            
        Returns:
            Dictionary with extracted data
            
        Example:
            selectors = {
                "title": "h1.product-title",
                "price": "span.price",
                "description": "div.description"
            }
        """
        if not self.browser:
            await self.start()
            
        page = await self.browser.new_page()
        
        try:
            await page.goto(url, timeout=self.timeout, wait_until="networkidle")
            
            results = {}
            for field, selector in selectors.items():
                try:
                    element = await page.query_selector(selector)
                    if element:
                        results[field] = await element.inner_text()
                    else:
                        results[field] = None
                except Exception:
                    results[field] = None
                    
            return results
            
        finally:
            await page.close()

    async def extract_text(self, url: str, clean: bool = True) -> str:
        """
        Extract all text content from a URL.
        
        Args:
            url: URL to scrape
            clean: Remove extra whitespace and newlines
            
        Returns:
            Extracted text content
        """
        if not self.browser:
            await self.start()
            
        page = await self.browser.new_page()
        
        try:
            await page.goto(url, timeout=self.timeout, wait_until="networkidle")
            
            # Remove script, style, and other non-content elements
            await page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('script, style, meta, link, noscript');
                    elements.forEach(el => el.remove());
                }
            """)
            
            # Get text content
            text = await page.evaluate("() => document.body.innerText")
            
            if clean:
                # Clean up whitespace
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                text = '\n'.join(lines)
            
            return text
            
        finally:
            await page.close()
    
    async def extract_links(
        self,
        url: str,
        internal_only: bool = False
    ) -> list[str]:
        """
        Extract all links from a page.
        
        Args:
            url: URL to scrape
            internal_only: Only return links from the same domain
            
        Returns:
            List of URLs
        """
        if not self.browser:
            await self.start()
            
        page = await self.browser.new_page()
        
        try:
            await page.goto(url, timeout=self.timeout, wait_until="networkidle")
            
            if internal_only:
                from urllib.parse import urlparse
                base_domain = urlparse(url).netloc
                
                links = await page.evaluate(f"""
                    () => {{
                        const baseDomain = '{base_domain}';
                        return Array.from(document.querySelectorAll('a[href]'))
                            .map(a => a.href)
                            .filter(href => {{
                                try {{
                                    return new URL(href).hostname === baseDomain;
                                }} catch {{
                                    return false;
                                }}
                            }});
                    }}
                """)
            else:
                links = await page.evaluate("""
                    () => Array.from(document.querySelectorAll('a[href]'))
                        .map(a => a.href)
                        .filter(href => href && href.startsWith('http'))
                """)
            
            return list(set(links))
            
        finally:
            await page.close()
    
    async def extract_metadata(self, url: str) -> Dict[str, str]:
        """
        Extract page metadata (title, description, keywords, etc.).
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary with metadata
        """
        if not self.browser:
            await self.start()
            
        page = await self.browser.new_page()
        
        try:
            await page.goto(url, timeout=self.timeout, wait_until="networkidle")
            
            metadata = await page.evaluate("""
                () => {
                    const meta = {};
                    
                    // Title
                    const title = document.querySelector('title');
                    if (title) meta.title = title.textContent;
                    
                    // Meta tags
                    document.querySelectorAll('meta').forEach(tag => {
                        const name = tag.getAttribute('name') || tag.getAttribute('property');
                        const content = tag.getAttribute('content');
                        if (name && content) {
                            meta[name] = content;
                        }
                    });
                    
                    return meta;
                }
            """)
            
            return metadata
            
        finally:
            await page.close()


# Example usage
async def main():
    """Example usage of PlaywrightScraper."""
    async with PlaywrightScraper() as scraper:
        # Basic scraping
        html = await scraper.scrape("https://example.com")
        print(f"Scraped {len(html)} characters")
        
        # Extract specific data
        data = await scraper.extract_data(
            "https://example.com",
            {"title": "h1", "content": "p"}
        )
        print(f"Extracted data: {data}")


if __name__ == "__main__":
    asyncio.run(main())
