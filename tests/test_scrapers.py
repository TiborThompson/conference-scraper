"""Unit tests for web scrapers."""

import pytest
import asyncio
from src.scrapers.playwright_scraper import PlaywrightScraper


class TestPlaywrightScraper:
    """Tests for Playwright scraper."""
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test scraper initialization."""
        scraper = PlaywrightScraper()
        assert scraper is not None
        assert scraper.headless is True
        
    @pytest.mark.asyncio
    async def test_scrape(self):
        """Test basic scraping."""
        async with PlaywrightScraper() as scraper:
            html = await scraper.scrape("https://example.com")
            assert isinstance(html, str)
            assert len(html) > 0
            assert "<html" in html.lower()
            
    @pytest.mark.asyncio
    async def test_extract_text(self):
        """Test text extraction."""
        async with PlaywrightScraper() as scraper:
            text = await scraper.extract_text("https://example.com")
            assert isinstance(text, str)
            assert len(text) > 0
            
    @pytest.mark.asyncio
    async def test_extract_links(self):
        """Test link extraction."""
        async with PlaywrightScraper() as scraper:
            links = await scraper.extract_links("https://example.com")
            assert isinstance(links, list)
            
    @pytest.mark.asyncio
    async def test_extract_metadata(self):
        """Test metadata extraction."""
        async with PlaywrightScraper() as scraper:
            metadata = await scraper.extract_metadata("https://example.com")
            assert isinstance(metadata, dict)
            assert "title" in metadata
            
    @pytest.mark.asyncio
    async def test_extract_data(self):
        """Test data extraction with selectors."""
        async with PlaywrightScraper() as scraper:
            data = await scraper.extract_data(
                "https://example.com",
                {"title": "h1", "paragraph": "p"}
            )
            assert isinstance(data, dict)
            assert "title" in data
            assert "paragraph" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
