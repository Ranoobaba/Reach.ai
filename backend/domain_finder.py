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


def extract_emails_from_text(text: str) -> list[str]:
    """Extract all email addresses from text."""
    if not text:
        return []
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text, re.IGNORECASE)
    return [email.lower() for email in emails]


def filter_company_emails(emails: list[str], company_domain: str = None) -> list[str]:
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
        if domain not in excluded_providers:
            company_emails.append(email)
    
    return company_emails


def get_email_domain(emails: list[str]) -> str | None:
    """Get the most likely company email domain from a list of emails."""
    if not emails:
        return None
    
    # Count domain occurrences
    domain_counts = {}
    for email in emails:
        domain = email.split("@")[-1]
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    # Return the most common domain
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


def is_domain_relevant(domain: str, company_name: str) -> bool:
    """
    Check if a domain is relevant to the company name.
    This helps filter out unrelated domains from search results.
    """
    if not domain or not company_name:
        return False
    
    # Normalize both for comparison
    domain_lower = domain.lower()
    company_lower = company_name.lower().replace(" ", "").replace("-", "").replace(".", "")
    
    # Remove common TLDs and prefixes for comparison
    domain_base = domain_lower.split(".")[0]
    
    # Check if company name is in the domain or vice versa
    if company_lower in domain_base or domain_base in company_lower:
        return True
    
    # Check for partial matches (at least 4 chars matching)
    if len(company_lower) >= 4 and company_lower[:4] in domain_base:
        return True
    if len(domain_base) >= 4 and domain_base[:4] in company_lower:
        return True
    
    return False


def search_company_contact_email(company_name: str) -> tuple[str | None, str | None]:
    """
    Use DuckDuckGo to search directly for company contact/support email.
    This often returns the email domain in search snippets.
    Returns: (email_domain, website_url)
    """
    website_url = None
    all_found_emails = []
    
    try:
        with DDGS() as ddgs:
            # Search specifically for contact email
            queries = [
                f"{company_name} official contact email",
                f"{company_name} company email address",
                f'"{company_name}" email @',
            ]
            
            for query in queries:
                results = list(ddgs.text(query, max_results=5))
                
                for result in results:
                    # Capture website URL - prioritize URLs matching company name
                    url = result.get("href", "") or result.get("link", "")
                    if url:
                        domain = extract_domain_from_url(url)
                        excluded = ["wikipedia.org", "linkedin.com", "facebook.com", 
                                   "twitter.com", "youtube.com", "crunchbase.com",
                                   "reddit.com", "quora.com", "medium.com"]
                        if domain and not any(ex in domain for ex in excluded):
                            # Prefer URLs that match company name
                            if not website_url or is_domain_relevant(domain, company_name):
                                parsed = urlparse(url)
                                website_url = f"{parsed.scheme}://{parsed.netloc}"
                    
                    # Check snippet/body for email addresses
                    snippet = result.get("body", "") or result.get("snippet", "")
                    title = result.get("title", "")
                    
                    # Extract emails from the search result
                    emails = extract_emails_from_text(snippet + " " + title)
                    filtered_emails = filter_company_emails(emails)
                    all_found_emails.extend(filtered_emails)
            
            # Prioritize emails with domains that match the company name
            for email in all_found_emails:
                email_domain = email.split("@")[-1]
                if is_domain_relevant(email_domain, company_name):
                    print(f"Found relevant email domain: {email_domain} for {company_name}")
                    return email_domain, website_url
            
            # If no relevant domain found, don't return unrelated emails
            # Let the fallback strategies handle it
            if all_found_emails:
                print(f"Found emails but none match company name: {all_found_emails}")
            
            return None, website_url
            
    except Exception as e:
        print(f"Error searching for contact email: {e}")
        return None, None


def find_company_website(company_name: str) -> str | None:
    """Use DuckDuckGo to find the company's official website."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f"{company_name} official website", max_results=5))
            
            # Filter out common non-company domains
            excluded_domains = [
                "wikipedia.org", "linkedin.com", "facebook.com",
                "twitter.com", "youtube.com", "instagram.com",
                "crunchbase.com", "bloomberg.com", "forbes.com",
                "reuters.com", "glassdoor.com", "indeed.com",
                "rocketreach.co", "hunter.io", "signalhire.com",
                "zoominfo.com", "apollo.io", "yelp.com", "g2.com"
            ]
            
            for result in results:
                url = result.get("href", "") or result.get("link", "")
                if url:
                    domain = extract_domain_from_url(url)
                    if domain and not any(ex in domain for ex in excluded_domains):
                        # Return the base URL
                        parsed = urlparse(url)
                        return f"{parsed.scheme}://{parsed.netloc}"
            
            return None
            
    except Exception as e:
        print(f"Error searching DuckDuckGo: {e}")
        return None


def find_company_domain(company_name: str, skip_cache: bool = False) -> dict:
    """
    Find the email domain for a company using cache-first strategy:
    
    1. Check cache first (instant, no API calls)
    2. If not cached, search DuckDuckGo for contact/support email
    3. If no email found, crawl contact page with Jina Reader
    4. Fall back to website domain
    5. Cache the result for future lookups
    
    Returns a dict with domain info and cache status.
    """
    print(f"Looking up email domain for: {company_name}")
    
    # Strategy 0: Check cache first (unless skip_cache is True)
    if not skip_cache:
        cached = get_cached_domain(company_name)
        if cached:
            print(f"Cache hit! {company_name} → {cached['email_domain']}")
            return cached
    
    print("Cache miss, searching...")
    website_url = None
    
    # Strategy 1: Search directly for contact email in DuckDuckGo
    print("Strategy 1: Searching for contact email in search results...")
    email_domain, website_url = search_company_contact_email(company_name)
    
    if email_domain:
        print(f"Found email domain from search: {email_domain}")
        # Cache the result
        cache_domain(company_name, email_domain, website_url, source="search")
        return {
            "company_name": company_name,
            "email_domain": email_domain,
            "website_url": website_url,
            "source": "search",
            "from_cache": False
        }
    
    # Strategy 2: Find website and crawl contact page
    print("Strategy 2: Finding company website...")
    if not website_url:
        website_url = find_company_website(company_name)
    
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
    
    # Try to find contact page and crawl it with Jina Reader
    contact_paths = ["/contact", "/contact-us", "/about", "/support", ""]
    
    all_emails = []
    
    for path in contact_paths:
        page_url = urljoin(website_url, path)
        print(f"Crawling {page_url} with Jina Reader...")
        
        content = crawl_with_jina(page_url)
        if content:
            emails = extract_emails_from_text(content)
            filtered = filter_company_emails(emails)
            
            if filtered:
                print(f"Found emails: {filtered}")
                all_emails.extend(filtered)
                break  # Found emails, no need to check more pages
    
    # Get the most common email domain
    if all_emails:
        email_domain = get_email_domain(all_emails)
        if email_domain:
            print(f"Email domain found: {email_domain}")
            # Cache the result
            cache_domain(company_name, email_domain, website_url, source="crawl")
            return {
                "company_name": company_name,
                "email_domain": email_domain,
                "website_url": website_url,
                "source": "crawl",
                "from_cache": False
            }
    
    # Strategy 3: Fall back to website domain
    print(f"No emails found, falling back to website domain: {website_domain}")
    # Cache the fallback result too
    cache_domain(company_name, website_domain, website_url, source="fallback")
    return {
        "company_name": company_name,
        "email_domain": website_domain,
        "website_url": website_url,
        "source": "fallback",
        "from_cache": False
    }
