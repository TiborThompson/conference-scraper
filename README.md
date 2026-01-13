# SOFWeek 2025 Speaker Recommendation System

AI-powered conference networking tool that matches your business goals with relevant speakers using parallel LLM scoring.

## Stack

- **Backend**: Python FastAPI (port 8000)
- **Frontend**: Next.js with TypeScript and Tailwind CSS (port 3000)
- **AI**: OpenAI GPT-4.1 for parallel speaker scoring
- **Scraping**: Playwright for dynamic content extraction

## Features

- **Web Scraping**: Extracts speaker profiles (name, title, organization, bio) from SOFWeek conference website
- **Parallel AI Scoring**: Sends async requests to score each speaker individually (0-10 scale)
- **Smart Filtering**: Returns only speakers above your threshold, ranked by relevance
- **Modern UI**: Clean Next.js interface with real-time updates

## Quick Start

### 1. Setup

```bash
./z/run.sh
```

This will:
- Create virtual environment
- Install Python dependencies
- Install Playwright browsers

Then install frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

### 2. Scrape Conference Data

```bash
./z/scrape.sh
```

This scrapes all speakers from https://sofweek.org/agenda/ and saves to `data/speakers.json`

### 3. Start the Application

```bash
./z/start.sh
```

This starts both:
- Backend API at http://localhost:8000
- Frontend UI at http://localhost:3000

Or start them separately:

```bash
# Terminal 1 - Backend
./z/start_backend.sh

# Terminal 2 - Frontend
./z/start_frontend.sh
```

## How It Works

### Architecture

```
User Input (Business Context)
    |
    v
Next.js Frontend (port 3000)
    |
    v
HTTP POST to /match
    |
    v
FastAPI Backend (port 8000)
    |
    v
Parallel Async LLM Calls (36 speakers scored simultaneously)
    |
    v
Each speaker gets score 0-10 + reasoning
    |
    v
Filter by threshold (default: 6.0)
    |
    v
Rank by score (highest first)
    |
    v
Return JSON response
    |
    v
Display in UI
```

### Scoring Criteria

The LLM evaluates each speaker based on:
- Relevant expertise and background
- Potential business synergy or partnerships
- Decision-making authority
- Shared interests or complementary capabilities

**Score Scale:**
- **9-10**: Must talk to - Excellent match
- **7-8**: Should prioritize - Good match
- **4-6**: Could be useful - Moderate match
- **0-3**: Not worth talking to - Poor match

## Project Structure

```
llm-webscraper/
|-- backend.py                        # FastAPI server
|-- frontend/                         # Next.js app
|   |-- app/
|   |   |-- page.tsx                  # Main UI
|   |   +-- layout.tsx                # Layout
|   +-- package.json
|-- src/
|   |-- scrapers/
|   |   +-- conference_scraper.py     # SOFWeek scraper
|   |-- llm/
|   |   |-- openai_client.py          # OpenAI API client
|   |   |-- speaker_matcher.py        # Parallel scoring engine
|   |   +-- prompts.py                # LLM prompts
|   +-- models/
|       +-- schemas.py                # Pydantic models
|-- data/
|   +-- speakers.json                 # Scraped speaker data
|-- z/
|   |-- run.sh                        # Setup script
|   |-- scrape.sh                     # Run scraper
|   |-- start.sh                      # Start both servers
|   |-- start_backend.sh              # Start backend only
|   +-- start_frontend.sh             # Start frontend only
+-- .env                              # API keys (not in git)
```

## API Endpoints

### GET /
Health check and status

### GET /speakers
Returns all scraped speakers

### POST /match
Match speakers based on user bio

**Request:**
```json
{
  "user_bio": "I sell Counter-Unmanned Aircraft Systems for an Army Air Base",
  "threshold": 6.0
}
```

**Response:**
```json
{
  "matches": [
    {
      "name": "The Honorable Pete Hegseth",
      "title": "Secretary of Defense",
      "organization": "U.S. Department of Defense",
      "bio": "...",
      "score": 10.0,
      "reasoning": "As the Secretary of Defense..."
    }
  ],
  "total_speakers": 36,
  "matches_found": 25
}
```

## Environment Variables

Create a `.env` file with:

```bash
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here  # Optional
```

## Usage Examples

### Example 1: Counter-UAS Sales
```
Input: "I sell Counter-Unmanned Aircraft Systems for an Army Air Base"

Top Matches:
1. Secretary of Defense Pete Hegseth (10/10)
2. SOFWERX Director Leslie Babich (9/10)
3. USSOCOM Acquisition Executive Melissa Johnson (9/10)
```

### Example 2: Small Business Drone Manufacturer
```
Input: "I sell kamikaze drones that destroy tanks, and I am a small business"

Top Matches:
1. USSOCOM Science & Technology Director Lisa Sanders (9/10)
2. PEO Maritime Captain Jared Wyrick (8/10)
3. International Operations Chief Jeffery Barnes (8/10)
```

## Technical Details

### Scraping

- Uses **Playwright** for dynamic content (handles Cvent iframe)
- Extracts from speaker cards (name, title, org) before clicking
- Clicks profile images to get full bios from modals
- Handles 36 speakers in ~2 minutes

### LLM Matching

- **Parallel Processing**: All 36 speakers scored simultaneously
- **Model**: OpenAI GPT-4.1
- **Async**: Uses `asyncio.gather()` for concurrent API calls
- **Token Efficient**: Truncates bios to 800 chars for scoring

### Frontend

- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS
- **Features**: 
  - Real-time form updates
  - Adjustable threshold slider
  - Example prompts
  - Responsive design
  - Loading states

### Backend

- **Framework**: FastAPI
- **CORS**: Enabled for localhost:3000
- **Async**: Full async/await support
- **Validation**: Pydantic models

## Development

### Run Backend Only

```bash
./z/start_backend.sh
# or
cd /path/to/project
source venv/bin/activate
python backend.py
```

### Run Frontend Only

```bash
./z/start_frontend.sh
# or
cd frontend
npm run dev
```

### Manual Scraping

```bash
python src/scrapers/conference_scraper.py
```

### Test Backend API

```bash
curl http://localhost:8000/
curl http://localhost:8000/speakers
```

## Dependencies

### Python
- `playwright` - Web scraping
- `openai` - LLM API
- `fastapi` - Backend API
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `python-dotenv` - Environment variables

### Node.js
- `next` - React framework
- `react` - UI library
- `tailwindcss` - Styling
- `typescript` - Type safety

## Notes

- Scraper is configured for SOFWeek 2025 (https://sofweek.org/agenda/)
- Scoring takes ~30-60 seconds for 36 speakers (parallel)
- Threshold can be adjusted in UI (default: 6.0)
- All speaker data cached in `data/speakers.json`
- Backend runs on port 8000
- Frontend runs on port 3000

## License

MIT
