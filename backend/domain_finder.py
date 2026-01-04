import re
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from ddgs import DDGS

# Import cache functions
from database import get_cached_domain, cache_domain

# Headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Jina Reader API (completely free, no API key needed)
JINA_READER_URL = "https://r.jina.ai/"

# Domains to always exclude from results
EXCLUDED_DOMAINS = [
    "wikipedia.org", "linkedin.com", "facebook.com",
    "twitter.com", "x.com", "youtube.com", "instagram.com",
    "crunchbase.com", "bloomberg.com", "forbes.com",
    "reuters.com", "glassdoor.com", "indeed.com",
    "rocketreach.co", "hunter.io", "signalhire.com",
    "zoominfo.com", "apollo.io", "yelp.com", "g2.com",
    "reddit.com", "quora.com", "medium.com", "github.com",
    "help.x.com", "support.google.com", "help.instagram.com",
    "support.apple.com", "answers.microsoft.com"
]


def extract_domain_from_url(url: str) -> str:
    """Extract the main domain from a URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def get_base_domain(domain: str) -> str:
    """
    Get the base domain without subdomains.
    e.g., 'help.tesla.com' -> 'tesla.com'
    e.g., 'teslamotorsclub.com' -> 'teslamotorsclub.com'
    """
    parts = domain.lower().split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return domain.lower()


def get_domain_name(domain: str) -> str:
    """
    Get just the domain name without TLD.
    e.g., 'tesla.com' -> 'tesla'
    e.g., 'trycua.com' -> 'trycua'
    """
    base = get_base_domain(domain)
    return base.split(".")[0]


def is_exact_company_domain(domain: str, company_name: str) -> bool:
    """
    Check if domain is an EXACT match for company name.
    e.g., 'tesla' matches 'tesla.com' but NOT 'teslamotorsclub.com'
    """
    if not domain or not company_name:
        return False
    
    company_lower = company_name.lower().replace(" ", "").replace("-", "").replace(".", "")
    domain_name = get_domain_name(domain)
    
    # Exact match
    if domain_name == company_lower:
        return True
    
    # Handle common patterns like "trycua" for "cua"
    if domain_name == f"try{company_lower}":
        return True
    if domain_name == f"get{company_lower}":
        return True
    if domain_name == f"{company_lower}hq":
        return True
    if domain_name == f"{company_lower}app":
        return True
    
    return False


def is_domain_excluded(domain: str) -> bool:
    """Check if domain should be excluded."""
    domain_lower = domain.lower()
    return any(ex in domain_lower for ex in EXCLUDED_DOMAINS)


def extract_emails_from_text(text: str) -> list[str]:
    """Extract all email addresses from text."""
    if not text:
        return []
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text, re.IGNORECASE)
    return [email.lower() for email in emails]


def filter_company_emails(emails: list[str], company_name: str = None) -> list[str]:
    """Filter out common public email providers, keep company emails."""
    excluded_providers = [
        "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", 
        "icloud.com", "aol.com", "protonmail.com", "mail.com",
        "live.com", "msn.com", "ymail.com", "example.com",
        "sentry.io", "email.com", "company.com"
    ]
    
    company_emails = []
    for email in emails:
        domain = email.split("@")[-1]
        if domain not in excluded_providers and not is_domain_excluded(domain):
            company_emails.append(email)
    
    return company_emails


def get_email_domain(emails: list[str], company_name: str = None) -> str | None:
    """
    Get the most likely company email domain from a list of emails.
    Prioritizes exact company name matches.
    """
    if not emails:
        return None
    
    # Count domain occurrences
    domain_counts = {}
    for email in emails:
        domain = email.split("@")[-1]
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    # First, look for exact company name matches
    if company_name:
        for domain in domain_counts:
            if is_exact_company_domain(domain, company_name):
                return domain
    
    # Otherwise return the most common domain
    if domain_counts:
        return max(domain_counts, key=domain_counts.get)
    
    return None


def crawl_with_jina(url: str) -> str | None:
    """
    Use Jina Reader API to crawl a webpage and get clean text content.
    This is completely free with no API key needed.
    """
    try:
        jina_url = f"{JINA_READER_URL}{url}"
        response = requests.get(jina_url, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            return response.text
        else:
            print(f"Jina Reader returned status {response.status_code} for {url}")
            return None
            
    except Exception as e:
        print(f"Error using Jina Reader for {url}: {e}")
        return None


def find_official_website(company_name: str) -> str | None:
    """
    Find the company's OFFICIAL website by searching for exact domain matches.
    """
    try:
        with DDGS() as ddgs:
            # Search for official website
            queries = [
                f"{company_name} official site",
                f"{company_name}.com",
                f'"{company_name}" company website',
            ]
            
            for query in queries:
                results = list(ddgs.text(query, max_results=10))
                
                # First pass: look for EXACT domain matches
                for result in results:
                    url = result.get("href", "") or result.get("link", "")
                    if url:
                        domain = extract_domain_from_url(url)
                        if domain and not is_domain_excluded(domain):
                            if is_exact_company_domain(domain, company_name):
                                parsed = urlparse(url)
                                print(f"Found exact match website: {parsed.scheme}://{parsed.netloc}")
                                return f"{parsed.scheme}://{parsed.netloc}"
            
            # Second pass: if no exact match, take the first non-excluded result
            for query in queries[:1]:  # Only use first query for fallback
                results = list(ddgs.text(query, max_results=5))
                for result in results:
                    url = result.get("href", "") or result.get("link", "")
                    if url:
                        domain = extract_domain_from_url(url)
                        if domain and not is_domain_excluded(domain):
                            parsed = urlparse(url)
                            print(f"Found fallback website: {parsed.scheme}://{parsed.netloc}")
                            return f"{parsed.scheme}://{parsed.netloc}"
            
            return None
            
    except Exception as e:
        print(f"Error searching DuckDuckGo: {e}")
        return None


def find_company_domain(company_name: str, skip_cache: bool = False) -> dict:
    """
    Find the email domain for a company.
    
    Strategy:
    1. Check cache first (instant, no API calls)
    2. Search for the company's official website (exact domain match preferred)
    3. Use the website domain as the email domain
    4. Cache the result for future lookups
    
    Returns a dict with domain info and cache status.
    """
    print(f"\n{'='*50}")
    print(f"Looking up email domain for: {company_name}")
    print(f"{'='*50}")
    
    # Strategy 0: Check cache first (unless skip_cache is True)
    if not skip_cache:
        cached = get_cached_domain(company_name)
        if cached:
            # Validate cached result isn't from an excluded domain
            if not is_domain_excluded(cached['email_domain']):
                print(f"Cache hit! {company_name} → {cached['email_domain']}")
                return cached
            else:
                print(f"Cached domain {cached['email_domain']} is excluded, searching fresh...")
    
    print("Cache miss, searching for official website...")
    
    # Strategy 1: Find the official company website
    website_url = find_official_website(company_name)
    
    if not website_url:
        print(f"Could not find website for {company_name}")
        return {
            "company_name": company_name,
            "email_domain": None,
            "website_url": None,
            "source": None,
            "from_cache": False,
            "error": "Could not find company website"
        }
    
    print(f"Found website: {website_url}")
    website_domain = extract_domain_from_url(website_url)
    base_domain = get_base_domain(website_domain)
    
    print(f"Using email domain: {base_domain}")
    
    # Cache and return the result
    cache_domain(company_name, base_domain, website_url, source="website")
    return {
        "company_name": company_name,
        "email_domain": base_domain,
        "website_url": website_url,
        "source": "website",
        "from_cache": False
    }
