"""
Scraper utilities for rate limiting, retry logic, and fallback scraping.
"""

import time
import random
import functools
import requests
from bs4 import BeautifulSoup
from typing import Callable, Any, Optional

# Headers to mimic a real browser
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


class RateLimiter:
    """
    Rate limiter that adds delays between requests to avoid triggering anti-bot protections.
    Uses random jitter to appear more human-like.
    """
    
    def __init__(self, min_delay: float = 1.0, max_delay: float = 2.5):
        """
        Initialize rate limiter.
        
        Args:
            min_delay: Minimum delay between requests in seconds
            max_delay: Maximum delay between requests in seconds
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time: float = 0
    
    def wait(self):
        """Wait an appropriate amount of time before the next request."""
        now = time.time()
        elapsed = now - self.last_request_time
        
        # Calculate delay with random jitter
        delay = random.uniform(self.min_delay, self.max_delay)
        
        # If we haven't waited long enough since the last request, wait more
        if elapsed < delay:
            sleep_time = delay - elapsed
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def __enter__(self):
        self.wait()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# Global rate limiter instance
_global_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    return _global_rate_limiter


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (requests.RequestException, TimeoutError),
):
    """
    Decorator that retries a function with exponential backoff on failure.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        exceptions: Tuple of exceptions to catch and retry on
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        # Last attempt failed, raise the exception
                        break
                    
                    # Calculate delay with exponential backoff and jitter
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    # Add random jitter (±25%)
                    jitter = delay * random.uniform(-0.25, 0.25)
                    actual_delay = delay + jitter
                    
                    print(f"  Retry {attempt + 1}/{max_retries} after {actual_delay:.1f}s: {e}")
                    time.sleep(actual_delay)
            
            # Re-raise the last exception if all retries failed
            if last_exception:
                raise last_exception
            return None
        
        return wrapper
    return decorator


@retry_with_backoff(max_retries=2, base_delay=1.0)
def fetch_with_beautifulsoup(url: str, timeout: int = 15) -> Optional[str]:
    """
    Fetch a URL directly using requests and parse with BeautifulSoup.
    This is a fallback when Jina Reader fails.
    
    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds
        
    Returns:
        Extracted text content from the page, or None if failed
    """
    rate_limiter = get_rate_limiter()
    rate_limiter.wait()
    
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        
        if response.status_code != 200:
            print(f"  BeautifulSoup fetch returned {response.status_code} for {url}")
            return None
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Get text content
        text = soup.get_text(separator=' ', strip=True)
        
        return text
        
    except Exception as e:
        print(f"  BeautifulSoup error for {url}: {e}")
        raise


def extract_contact_links(html_content: str, base_url: str) -> list[str]:
    """
    Extract contact-related links from HTML content.
    
    Args:
        html_content: Raw HTML content
        base_url: Base URL for resolving relative links
        
    Returns:
        List of absolute URLs that might contain contact information
    """
    from urllib.parse import urljoin, urlparse
    
    contact_keywords = [
        'contact', 'about', 'team', 'people', 'leadership',
        'careers', 'jobs', 'press', 'media', 'support', 'help'
    ]
    
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag.get('href', '')
            link_text = a_tag.get_text(strip=True).lower()
            
            # Check if link text or href contains contact keywords
            is_contact_link = any(
                keyword in href.lower() or keyword in link_text
                for keyword in contact_keywords
            )
            
            if is_contact_link:
                # Resolve relative URLs
                absolute_url = urljoin(base_url, href)
                
                # Only include links from the same domain
                base_domain = urlparse(base_url).netloc
                link_domain = urlparse(absolute_url).netloc
                
                if link_domain == base_domain and absolute_url not in links:
                    links.append(absolute_url)
        
        return links[:10]  # Limit to 10 links to avoid over-crawling
        
    except Exception as e:
        print(f"  Error extracting links: {e}")
        return []


def get_page_html(url: str, timeout: int = 15) -> Optional[str]:
    """
    Get raw HTML content from a URL.
    
    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds
        
    Returns:
        Raw HTML content or None if failed
    """
    rate_limiter = get_rate_limiter()
    rate_limiter.wait()
    
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        if response.status_code == 200:
            return response.text
        return None
    except Exception as e:
        print(f"  Error fetching HTML from {url}: {e}")
        return None

