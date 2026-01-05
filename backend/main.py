import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional

from domain_finder import find_company_domain
from permutator import generate_email_permutations
from database import get_cache_stats, search_cache, bulk_import_domains, get_cached_domain, delete_cached_domain, get_dns_cache_stats
from email_validator import validate_emails_batch, calculate_score, get_score_label

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


class EmailWithScore(BaseModel):
    """Email address with validation score and breakdown."""
    email: str
    score: int
    max_score: int
    label: str  # "Excellent", "Good", "Fair", "Poor", "Invalid"
    breakdown: dict


class GenerateResponse(BaseModel):
    """Response with domain and scored email permutations."""
    domain: str
    emails: list[EmailWithScore]
    from_cache: bool = False
    source: Optional[str] = None


class ValidateEmailRequest(BaseModel):
    """Request to validate a single email address."""
    email: str


class ValidateEmailsRequest(BaseModel):
    """Request to validate multiple email addresses."""
    emails: list[str]


class BulkImportRequest(BaseModel):
    entries: list[dict]


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Email Permutator API is running"}


@app.post("/api/generate", response_model=GenerateResponse)
def generate_emails(request: GenerateRequest):
    """
    Generate email permutations for a person at a company with validation scores.
    
    1. Checks cache first for instant lookups
    2. If not cached, searches for the company's email domain
    3. Caches the result for future requests
    4. Generates 30 email permutations based on the person's name
    5. Validates each email and returns with scores
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
    raw_emails = generate_email_permutations(
        request.first_name,
        request.last_name,
        domain
    )
    
    # Validate all emails and get scores
    validation_results = validate_emails_batch(raw_emails)
    
    # Convert to response format with scores
    scored_emails = []
    for vr in validation_results:
        scored_emails.append(EmailWithScore(
            email=vr.email,
            score=vr.score,
            max_score=vr.max_score,
            label=get_score_label(vr.score),
            breakdown=vr.breakdown,
        ))
    
    # Sort by score (highest first)
    scored_emails.sort(key=lambda e: e.score, reverse=True)
    
    return GenerateResponse(
        domain=domain, 
        emails=scored_emails,
        from_cache=result.get("from_cache", False),
        source=result.get("source")
    )


@app.post("/api/validate")
def validate_single_email(request: ValidateEmailRequest):
    """
    Validate a single email address and return its score.
    
    Score breakdown:
    - Syntax Valid: 20 points
    - Domain Exists (DNS A record): 20 points
    - MX Records Present: 25 points
    - Not Disposable: 15 points
    - Not Role-Based: 10 points
    - Not Free Provider: 10 points
    
    Max Score: 100 points
    """
    if not request.email or not request.email.strip():
        raise HTTPException(status_code=400, detail="Email is required")
    
    result = calculate_score(request.email.strip())
    
    return {
        "email": result.email,
        "score": result.score,
        "max_score": result.max_score,
        "label": get_score_label(result.score),
        "is_valid": result.is_valid,
        "breakdown": result.breakdown,
    }


@app.post("/api/validate/batch")
def validate_multiple_emails(request: ValidateEmailsRequest):
    """
    Validate multiple email addresses at once.
    Efficient batch processing with shared DNS lookups per domain.
    """
    if not request.emails:
        raise HTTPException(status_code=400, detail="Emails list is required")
    
    if len(request.emails) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 emails per batch")
    
    results = validate_emails_batch(request.emails)
    
    return {
        "count": len(results),
        "results": [
            {
                "email": r.email,
                "score": r.score,
                "max_score": r.max_score,
                "label": get_score_label(r.score),
                "is_valid": r.is_valid,
                "breakdown": r.breakdown,
            }
            for r in results
        ]
    }


@app.get("/api/cache/stats")
def get_stats():
    """Get cache statistics including total entries, top accessed companies, and DNS cache stats."""
    company_stats = get_cache_stats()
    dns_stats = get_dns_cache_stats()
    
    return {
        **company_stats,
        "dns_cache": dns_stats,
    }


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
