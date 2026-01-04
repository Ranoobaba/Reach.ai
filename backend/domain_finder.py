import re
import requests
from urllib.parse import urlparse
from ddgs import DDGS

# Import cache functions
from database import get_cached_domain, cache_domain

# Headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# Jina Reader API (completely free, no API key needed)
JINA_READER_URL = "https://r.jina.ai/"

# Domains to ALWAYS exclude - these are never company email domains
EXCLUDED_DOMAINS = {
    # Social media
    "twitter.com", "x.com", "facebook.com", "instagram.com", "linkedin.com",
    "youtube.com", "tiktok.com", "pinterest.com", "reddit.com", "quora.com",
    # Info sites
    "wikipedia.org", "fandom.com", "wikia.com", "medium.com", "substack.com",
    # Business info
    "crunchbase.com", "bloomberg.com", "forbes.com", "reuters.com",
    "glassdoor.com", "indeed.com", "yelp.com", "g2.com", "trustpilot.com",
    # Email finder tools (competitors)
    "rocketreach.co", "hunter.io", "signalhire.com", "zoominfo.com", 
    "apollo.io", "lusha.com", "clearbit.com",
    # Tech/code
    "github.com", "gitlab.com", "stackoverflow.com",
    # Email providers
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com",
    "aol.com", "protonmail.com", "mail.com", "live.com", "msn.com",
    # Support subdomains
    "help.x.com", "support.google.com",
}


def extract_domain_from_url(url: str) -> str:
    """Extract the main domain from a URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def get_base_domain(domain: str) -> str:
    """Get base domain: help.spacex.com -> spacex.com"""
    parts = domain.lower().split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return domain.lower()


def is_excluded(domain: str) -> bool:
    """Check if domain is in exclusion list."""
    base = get_base_domain(domain)
    return base in EXCLUDED_DOMAINS or domain in EXCLUDED_DOMAINS


def extract_emails_from_text(text: str) -> list[str]:
    """Extract all email addresses from text."""
    if not text:
        return []
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text, re.IGNORECASE)
    # Filter out excluded domains and return unique
    valid_emails = []
    seen = set()
    for email in emails:
        email_lower = email.lower()
        domain = email_lower.split("@")[-1]
        if email_lower not in seen and not is_excluded(domain):
            valid_emails.append(email_lower)
            seen.add(email_lower)
    return valid_emails


def normalize_company(name: str) -> str:
    """Normalize company name for matching."""
    return name.lower().replace(" ", "").replace("-", "").replace(".", "").replace("_", "")


def domain_matches_company(domain: str, company: str) -> tuple[bool, int]:
    """
    Check if domain matches company name.
    Returns (matches, score) where higher score = better match.
    
    Examples:
    - spacex.com matches SpaceX (score: 100, exact)
    - tesla.com matches Tesla (score: 100, exact)
    - trycua.com matches CUA (score: 80, contains)
    """
    company_norm = normalize_company(company)
    domain_name = get_base_domain(domain).split(".")[0]  # spacex.com -> spacex
    
    # Exact match
    if domain_name == company_norm:
        return True, 100
    
    # Domain contains company name exactly
    if company_norm in domain_name and len(company_norm) >= 3:
        # Penalize if domain has extra stuff (teslamotorsclub vs tesla)
        extra_chars = len(domain_name) - len(company_norm)
        if extra_chars <= 3:  # tryspacex, getspacex are ok
            return True, 90 - extra_chars
        elif extra_chars <= 6:
            return True, 70 - extra_chars
        else:
            return False, 0  # Too different (teslamotorsclub)
    
    # Company contains domain
    if domain_name in company_norm and len(domain_name) >= 3:
        return True, 60
    
    return False, 0


def crawl_with_jina(url: str) -> str | None:
    """Use Jina Reader to get page content."""
    try:
        response = requests.get(f"{JINA_READER_URL}{url}", headers=HEADERS, timeout=30)
        if response.status_code == 200:
            return response.text
        return None
    except Exception as e:
        print(f"Jina error: {e}")
        return None


def find_company_domain(company_name: str, skip_cache: bool = False) -> dict:
    """
    Find the email domain for a company.
    
    Strategy:
    1. Check cache first
    2. Search DuckDuckGo for "{company} email" to find email addresses
    3. Score found domains by how well they match company name
    4. Return best matching domain
    """
    print(f"\n{'='*50}")
    print(f"Finding email domain for: {company_name}")
    print(f"{'='*50}")
    
    # Check cache first
    if not skip_cache:
        cached = get_cached_domain(company_name)
        if cached and not is_excluded(cached['email_domain']):
            print(f"✓ Cache hit: {cached['email_domain']}")
            return cached
    
    print("Searching...")
    
    # Collect all found domains with scores
    domain_scores = {}  # domain -> (score, source_url)
    
    try:
        with DDGS() as ddgs:
            # Search queries designed to find company emails
            queries = [
                f"{company_name} contact email",
                f"{company_name} email address",
                f"email @{company_name.lower().replace(' ', '')}",
                f"{company_name} official website",
            ]
            
            for query in queries:
                print(f"  Query: {query}")
                try:
                    results = list(ddgs.text(query, max_results=8))
                except Exception as e:
                    print(f"  Search error: {e}")
                    continue
                
                for result in results:
                    snippet = result.get("body", "") or result.get("snippet", "")
                    title = result.get("title", "")
                    url = result.get("href", "") or result.get("link", "")
                    
                    # Extract emails from snippet
                    emails = extract_emails_from_text(f"{snippet} {title}")
                    for email in emails:
                        domain = email.split("@")[-1]
                        matches, score = domain_matches_company(domain, company_name)
                        if matches and score > domain_scores.get(domain, (0, ""))[0]:
                            domain_scores[domain] = (score, url)
                            print(f"    Found email domain: {domain} (score: {score})")
                    
                    # Also check the URL domain
                    if url:
                        url_domain = extract_domain_from_url(url)
                        if url_domain and not is_excluded(url_domain):
                            base = get_base_domain(url_domain)
                            matches, score = domain_matches_company(base, company_name)
                            # URL domains get slightly lower score than email domains
                            score = int(score * 0.9)
                            if matches and score > domain_scores.get(base, (0, ""))[0]:
                                domain_scores[base] = (score, url)
                                print(f"    Found URL domain: {base} (score: {score})")
    
    except Exception as e:
        print(f"Search error: {e}")
    
    # Return best scoring domain
    if domain_scores:
        best_domain = max(domain_scores.keys(), key=lambda d: domain_scores[d][0])
        score, source_url = domain_scores[best_domain]
        print(f"\n✓ Best match: {best_domain} (score: {score})")
        
        # Cache result
        cache_domain(company_name, best_domain, source_url, source="search")
        return {
            "company_name": company_name,
            "email_domain": best_domain,
            "website_url": source_url,
            "source": "search",
            "from_cache": False
        }
    
    # Fallback: Try to crawl {company}.com directly
    print("\nNo email found in search, trying direct domain...")
    company_domain = f"{normalize_company(company_name)}.com"
    test_url = f"https://{company_domain}"
    
    try:
        # Quick check if domain exists
        response = requests.head(test_url, timeout=5, allow_redirects=True)
        if response.status_code < 400:
            final_domain = extract_domain_from_url(response.url) or company_domain
            base = get_base_domain(final_domain)
            print(f"✓ Direct domain works: {base}")
            cache_domain(company_name, base, test_url, source="direct")
            return {
                "company_name": company_name,
                "email_domain": base,
                "website_url": response.url,
                "source": "direct",
                "from_cache": False
            }
    except Exception as e:
        print(f"Direct domain check failed: {e}")
    
    print(f"✗ Could not find domain for {company_name}")
    return {
        "company_name": company_name,
        "email_domain": None,
        "website_url": None,
        "source": None,
        "from_cache": False,
        "error": "Could not find company email domain"
    }
