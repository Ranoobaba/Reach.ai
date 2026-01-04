import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional

from domain_finder import find_company_domain
from permutator import generate_email_permutations
from database import get_cache_stats, search_cache, bulk_import_domains, get_cached_domain, delete_cached_domain

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Email Permutator API",
    description="Find email domains and generate email permutations. Uses caching for performance at scale."
)

# Configure CORS for frontend
# Allow localhost for development and production frontend URL from environment
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Add production frontend URL if set (handle with/without trailing slash)
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    # Remove trailing slash for consistency
    frontend_url = frontend_url.rstrip("/")
    allowed_origins.append(frontend_url)
    # Also add with trailing slash just in case
    allowed_origins.append(f"{frontend_url}/")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    first_name: str
    last_name: str
    company: str


class GenerateResponse(BaseModel):
    domain: str
    emails: list[str]
    from_cache: bool = False
    source: Optional[str] = None


class BulkImportRequest(BaseModel):
    entries: list[dict]


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Email Permutator API is running"}


@app.post("/api/generate", response_model=GenerateResponse)
def generate_emails(request: GenerateRequest):
    """
    Generate email permutations for a person at a company.
    
    1. Checks cache first for instant lookups
    2. If not cached, searches for the company's email domain
    3. Caches the result for future requests
    4. Generates 30 email permutations based on the person's name
    """
    if not request.first_name.strip():
        raise HTTPException(status_code=400, detail="First name is required")
    if not request.last_name.strip():
        raise HTTPException(status_code=400, detail="Last name is required")
    if not request.company.strip():
        raise HTTPException(status_code=400, detail="Company name is required")
    
    # Find the company domain (checks cache first)
    result = find_company_domain(request.company)
    
    if not result or not result.get("email_domain"):
        raise HTTPException(
            status_code=404,
            detail=f"Could not find domain for company: {request.company}"
        )
    
    domain = result["email_domain"]
    
    # Generate email permutations
    emails = generate_email_permutations(
        request.first_name,
        request.last_name,
        domain
    )
    
    return GenerateResponse(
        domain=domain, 
        emails=emails,
        from_cache=result.get("from_cache", False),
        source=result.get("source")
    )


@app.get("/api/cache/stats")
def get_stats():
    """Get cache statistics including total entries and top accessed companies."""
    return get_cache_stats()


@app.get("/api/cache/search")
def search_cached_domains(q: str = Query(..., description="Search query")):
    """Search the cache for companies matching a query."""
    results = search_cache(q)
    return {"query": q, "results": results, "count": len(results)}


@app.get("/api/cache/lookup/{company_name}")
def lookup_cached_domain(company_name: str):
    """Look up a specific company in the cache without triggering a search."""
    cached = get_cached_domain(company_name)
    if cached:
        return cached
    return {"cached": False, "company_name": company_name}


@app.post("/api/cache/import")
def import_domains(request: BulkImportRequest):
    """
    Bulk import company → domain mappings to seed the cache.
    
    Each entry should have:
    - company_name: str (required)
    - email_domain: str (required)
    - website_url: str (optional)
    
    Example:
    {
        "entries": [
            {"company_name": "LangChain", "email_domain": "langchain.dev"},
            {"company_name": "Hugging Face", "email_domain": "huggingface.co"}
        ]
    }
    """
    if not request.entries:
        raise HTTPException(status_code=400, detail="No entries provided")
    
    # Validate entries
    for i, entry in enumerate(request.entries):
        if "company_name" not in entry or "email_domain" not in entry:
            raise HTTPException(
                status_code=400, 
                detail=f"Entry {i} missing required fields (company_name, email_domain)"
            )
    
    bulk_import_domains(request.entries)
    return {"imported": len(request.entries), "status": "success"}


@app.delete("/api/cache/{company_name}")
def delete_cache_entry(company_name: str):
    """Delete a company from the cache to force a fresh lookup."""
    deleted = delete_cached_domain(company_name)
    if deleted:
        return {"status": "deleted", "company_name": company_name}
    return {"status": "not_found", "company_name": company_name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
