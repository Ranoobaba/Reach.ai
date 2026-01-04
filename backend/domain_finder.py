import re
import requests
from urllib.parse import urlparse, urljoin
from ddgs import DDGS

# Import cache functions
from database import get_cached_domain, cache_domain

# Headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# Jina Reader API - free, no API key needed, gets clean text from any URL
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
    # Startup/VC directories
    "ycombinator.com", "techcrunch.com", "producthunt.com", "angel.co", "angellist.com",
    # Email finder tools
    "rocketreach.co", "hunter.io", "signalhire.com", "zoominfo.com", 
    "apollo.io", "lusha.com", "clearbit.com",
    # Tech/code
    "github.com", "gitlab.com", "stackoverflow.com",
    # Email providers
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com",
    "aol.com", "protonmail.com", "mail.com", "live.com", "msn.com",
}


def get_base_domain(domain: str) -> str:
    """Get base domain: help.spacex.com -> spacex.com"""
    parts = domain.lower().split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return domain.lower()


def is_excluded(domain: str) -> bool:
    """Check if domain is in exclusion list."""
    if not domain:
        return True
    base = get_base_domain(domain)
    return base in EXCLUDED_DOMAINS or domain.lower() in EXCLUDED_DOMAINS


def extract_emails_from_text(text: str) -> list[str]:
    """Extract all email addresses from text."""
    if not text:
        return []
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text, re.IGNORECASE)
    
    # Filter and dedupe
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


def is_domain_input(name: str) -> str | None:
    """
    Check if the input looks like a domain name.
    Returns the domain if it is, None otherwise.
    """
    name_lower = name.lower().strip()
    # Common TLDs
    tlds = [".com", ".io", ".ai", ".dev", ".co", ".org", ".net", ".app", ".xyz"]
    for tld in tlds:
        if name_lower.endswith(tld):
            return name_lower
    return None


def crawl_website(url: str) -> str | None:
    """
    Use Jina Reader to crawl a website and get clean text.
    Jina handles JavaScript rendering, bypasses some blocks, etc.
    """
    try:
        jina_url = f"{JINA_READER_URL}{url}"
        print(f"  Crawling: {url}")
        response = requests.get(jina_url, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            return response.text
        print(f"  Jina returned {response.status_code}")
        return None
    except Exception as e:
        print(f"  Crawl error: {e}")
        return None


def find_company_website(company_name: str) -> str | None:
    """
    Search DuckDuckGo to find the company's official website.
    Returns the URL of the most likely official site.
    """
    # Check if user provided a domain directly (e.g., "a0.dev")
    domain_input = is_domain_input(company_name)
    if domain_input:
        # User provided a domain, use it directly
        try:
            test_url = f"https://{domain_input}"
            response = requests.head(test_url, timeout=5, allow_redirects=True, headers=HEADERS)
            if response.status_code < 400:
                print(f"  User provided domain: {domain_input}")
                return test_url
        except Exception:
            pass
    
    # First, try direct domain check for {company}.com
    normalized = normalize_company(company_name)
    direct_domains = [
        f"{normalized}.com",
        f"try{normalized}.com",
        f"get{normalized}.com",
        f"{normalized}.ai",
        f"{normalized}.io",
    ]
    
    for direct_domain in direct_domains:
        try:
            test_url = f"https://{direct_domain}"
            response = requests.head(test_url, timeout=5, allow_redirects=True, headers=HEADERS)
            if response.status_code < 400:
                print(f"  Direct domain found: {direct_domain}")
                return test_url
        except Exception:
            continue
    
    # Fall back to DuckDuckGo search
    try:
        with DDGS() as ddgs:
            # Try multiple search queries - prioritize tech/startup context
            queries = [
                f"{company_name} company website",
                f"{company_name} startup",
                f"{company_name} official website",
                f'"{company_name}" company',
            ]
            
            for query in queries:
                print(f"  Searching: {query}")
                results = list(ddgs.text(query, max_results=5))
                
                for result in results:
                    url = result.get("href", "") or result.get("link", "")
                    if not url:
                        continue
                    
                    try:
                        parsed = urlparse(url)
                        domain = parsed.netloc.lower()
                        if domain.startswith("www."):
                            domain = domain[4:]
                        
                        # Skip excluded domains
                        if is_excluded(domain):
                            continue
                        
                        # Return the website URL
                        website_url = f"{parsed.scheme}://{parsed.netloc}"
                        print(f"  Found website: {website_url}")
                        return website_url
                        
                    except Exception:
                        continue
            
            return None
            
    except Exception as e:
        print(f"  Search error: {e}")
        return None


def find_emails_on_website(website_url: str) -> list[str]:
    """
    Crawl a website to find email addresses.
    Checks the homepage and common contact pages.
    """
    all_emails = []
    
    # Pages to check for contact info
    pages_to_check = [
        "",           # Homepage
        "/contact",
        "/contact-us", 
        "/about",
        "/support",
        "/help",
    ]
    
    for page in pages_to_check:
        page_url = urljoin(website_url, page)
        content = crawl_website(page_url)
        
        if content:
            emails = extract_emails_from_text(content)
            if emails:
                print(f"  Found emails on {page_url}: {emails}")
                all_emails.extend(emails)
                # If we found emails, we can stop
                break
    
    return list(set(all_emails))


def get_best_email_domain(emails: list[str], company_name: str) -> str | None:
    """
    From a list of emails, find the most likely company email domain.
    Prioritizes domains that match the company name.
    """
    if not emails:
        return None
    
    company_norm = normalize_company(company_name)
    
    # Score each domain
    domain_scores = {}
    for email in emails:
        domain = email.split("@")[-1]
        base = get_base_domain(domain)
        domain_name = base.split(".")[0]
        
        # Calculate match score
        if domain_name == company_norm:
            score = 100  # Exact match
        elif company_norm in domain_name:
            score = 80   # Company name in domain
        elif domain_name in company_norm:
            score = 60   # Domain in company name
        else:
            score = 40   # No match but found on company site
        
        if base not in domain_scores or score > domain_scores[base]:
            domain_scores[base] = score
    
    if domain_scores:
        return max(domain_scores.keys(), key=lambda d: domain_scores[d])
    
    return None


def find_company_domain(company_name: str, skip_cache: bool = False) -> dict:
    """
    Find the email domain for a company.
    
    Strategy:
    1. Check cache first
    2. Search DuckDuckGo to find company's official website
    3. Crawl the website to find email addresses
    4. Extract the email domain
    5. Cache and return
    """
    print(f"\n{'='*60}")
    print(f"Finding email domain for: {company_name}")
    print(f"{'='*60}")
    
    # Step 1: Check cache
    if not skip_cache:
        cached = get_cached_domain(company_name)
        if cached and not is_excluded(cached['email_domain']):
            print(f"✓ Cache hit: {cached['email_domain']}")
            return cached
    
    # Step 2: Find company website
    print("\nStep 1: Finding company website...")
    website_url = find_company_website(company_name)
    
    if not website_url:
        print(f"✗ Could not find website for {company_name}")
        return {
            "company_name": company_name,
            "email_domain": None,
            "website_url": None,
            "source": None,
            "from_cache": False,
            "error": "Could not find company website"
        }
    
    # Step 3: Crawl website to find emails
    print(f"\nStep 2: Crawling {website_url} to find emails...")
    emails = find_emails_on_website(website_url)
    
    if emails:
        # Step 4: Get best matching domain from emails
        email_domain = get_best_email_domain(emails, company_name)
        if email_domain:
            print(f"\n✓ Found email domain: {email_domain}")
            cache_domain(company_name, email_domain, website_url, source="crawl")
            return {
                "company_name": company_name,
                "email_domain": email_domain,
                "website_url": website_url,
                "source": "crawl",
                "from_cache": False
            }
    
    # Step 5: Fallback - use the website domain
    print("\nNo emails found, falling back to website domain...")
    try:
        parsed = urlparse(website_url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        base_domain = get_base_domain(domain)
        
        print(f"✓ Using website domain: {base_domain}")
        cache_domain(company_name, base_domain, website_url, source="fallback")
        return {
            "company_name": company_name,
            "email_domain": base_domain,
            "website_url": website_url,
            "source": "fallback",
            "from_cache": False
        }
    except Exception as e:
        print(f"✗ Error: {e}")
        return {
            "company_name": company_name,
            "email_domain": None,
            "website_url": website_url,
            "source": None,
            "from_cache": False,
            "error": str(e)
        }
