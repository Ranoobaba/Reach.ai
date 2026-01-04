# Email Finder

A web application that helps you find potential email addresses for anyone based on their name and company. **Built for scale** with caching to minimize external API calls.

## Features

- Enter first name, last name, and company name
- **Cache-first architecture** - 90%+ of lookups are instant (no API calls)
- Automatically searches for the company's email domain using free APIs
- Generates 30 common email permutations
- Copy all emails or open them directly in your email client
- Pre-seeded with 70+ popular tech companies

## Tech Stack

- **Frontend**: Next.js with Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: SQLite (for caching)
- **Domain Search**: DuckDuckGo + Jina Reader (both free, no API keys needed)

## Architecture

```
User Request → Check Cache → [HIT] → Return instantly
                    ↓
                 [MISS]
                    ↓
         Search DuckDuckGo for email
                    ↓
         Crawl contact page with Jina
                    ↓
         Cache result for future use
                    ↓
              Return to user
```

## Setup

### Prerequisites

- Node.js 18+
- Python 3.10+
- No API keys needed! 🎉

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Seed the database with common companies (optional but recommended):
   ```bash
   python seed_data.py
   ```

4. Run the backend:
   ```bash
   python main.py
   ```
   The API will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```
   The app will be available at http://localhost:3000

## Usage

1. Enter the person's first name, last name, and company name
2. Click "Generate Email Addresses"
3. The app will check the cache first (instant!), otherwise search for the domain
4. Results are cached for future lookups
5. Use "Copy All" to copy emails to clipboard, or "Open in Email" to compose an email

## API Endpoints

### POST /api/generate

Generate email permutations for a person at a company.

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "company": "LangChain"
}
```

**Response:**
```json
{
  "domain": "langchain.dev",
  "emails": ["john@langchain.dev", "doe@langchain.dev", ...],
  "from_cache": true,
  "source": "search"
}
```

### GET /api/cache/stats

Get cache statistics.

**Response:**
```json
{
  "total_entries": 75,
  "top_accessed": [...],
  "recently_added": [...]
}
```

### GET /api/cache/search?q={query}

Search the cache for companies.

### POST /api/cache/import

Bulk import company → domain mappings.

**Request Body:**
```json
{
  "entries": [
    {"company_name": "Acme Inc", "email_domain": "acme.com"},
    {"company_name": "Example Corp", "email_domain": "example.io"}
  ]
}
```

## Scaling Tips

1. **Pre-seed your cache** with companies you expect users to search
2. **Export/import cache** between environments
3. For very high scale, consider migrating SQLite to PostgreSQL
4. The cache grows organically as users search new companies

