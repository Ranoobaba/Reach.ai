"""
Background scraper that automatically discovers and caches company email domains.

This scraper runs independently and populates the database with company domains
from various sources like YC companies, tech company lists, etc.

Usage:
    python background_scraper.py                    # Run once
    python background_scraper.py --continuous       # Run continuously
    python background_scraper.py --source yc        # Scrape specific source
"""

import argparse
import time
import random
import requests
from typing import Generator
from datetime import datetime

from database import get_cached_domain, cache_domain, get_db, init_db
from domain_finder import find_company_domain, is_excluded
from scraper_utils import get_rate_limiter, RateLimiter

# Initialize database
init_db()


# ============================================
# Company Sources
# ============================================

def get_yc_companies() -> Generator[dict, None, None]:
    """
    Fetch Y Combinator companies from their public API.
    Returns company name and website if available.
    """
    print("\n[YC] Fetching Y Combinator companies...")
    
    # YC's public company list API
    url = "https://api.ycombinator.com/v0.1/companies"
    
    try:
        # They paginate, so we need to fetch multiple pages
        page = 0
        while True:
            params = {"page": page}
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                print(f"[YC] API returned {response.status_code}")
                break
            
            data = response.json()
            companies = data.get("companies", [])
            
            if not companies:
                break
            
            for company in companies:
                name = company.get("name")
                website = company.get("website") or company.get("url")
                batch = company.get("batch", "")
                
                if name:
                    yield {
                        "name": name,
                        "website": website,
                        "source": f"yc_{batch}" if batch else "yc",
                    }
            
            page += 1
            time.sleep(1)  # Rate limit
            
            # Safety limit
            if page > 100:
                break
                
    except Exception as e:
        print(f"[YC] Error fetching companies: {e}")


def get_companies_from_seed_data() -> Generator[dict, None, None]:
    """
    Get companies from the local seed_data.py file.
    """
    print("\n[SEED] Loading companies from seed data...")
    
    try:
        from seed_data import SEED_COMPANIES
        
        for company in SEED_COMPANIES:
            yield {
                "name": company.get("company_name"),
                "website": company.get("website_url"),
                "source": "seed",
            }
    except ImportError:
        print("[SEED] No seed_data.py found")
    except Exception as e:
        print(f"[SEED] Error loading seed data: {e}")


def get_tech_companies_list() -> Generator[dict, None, None]:
    """
    A curated list of popular tech companies to pre-populate.
    """
    print("\n[TECH] Loading curated tech companies...")
    
    companies = [
        # Big Tech
        "Google", "Microsoft", "Apple", "Amazon", "Meta", "Netflix", "Uber", "Lyft",
        "Airbnb", "Spotify", "Slack", "Zoom", "Dropbox", "Salesforce", "Adobe",
        "Oracle", "IBM", "Intel", "Nvidia", "AMD", "Cisco", "VMware", "Dell",
        
        # AI/ML Companies
        "OpenAI", "Anthropic", "Cohere", "Stability AI", "Midjourney", "Jasper",
        "Hugging Face", "Scale AI", "Databricks", "Snowflake", "Palantir",
        "C3.ai", "DataRobot", "H2O.ai", "Weights & Biases", "Neptune.ai",
        
        # Fintech
        "Stripe", "Square", "PayPal", "Plaid", "Robinhood", "Coinbase", "Ripple",
        "Chime", "SoFi", "Affirm", "Klarna", "Brex", "Ramp", "Mercury",
        
        # Dev Tools
        "GitHub", "GitLab", "Atlassian", "JetBrains", "Vercel", "Netlify",
        "Supabase", "PlanetScale", "Neon", "Railway", "Render", "Fly.io",
        "Postman", "Insomnia", "Figma", "Notion", "Linear", "Retool",
        
        # Cloud/Infra
        "Cloudflare", "Fastly", "DigitalOcean", "Linode", "Vultr", "Hetzner",
        "HashiCorp", "Terraform", "Docker", "Kubernetes", "Rancher",
        
        # Security
        "CrowdStrike", "Palo Alto Networks", "Okta", "Auth0", "1Password",
        "Snyk", "Lacework", "Wiz", "Orca Security",
        
        # YC Unicorns
        "Stripe", "Airbnb", "Coinbase", "DoorDash", "Instacart", "Dropbox",
        "Reddit", "Twitch", "Cruise", "Brex", "Gusto", "Zapier", "Webflow",
        "Segment", "Algolia", "Mixpanel", "Amplitude", "LaunchDarkly",
    ]
    
    for name in companies:
        yield {
            "name": name,
            "website": None,
            "source": "tech_list",
        }


# ============================================
# Scraper Logic
# ============================================

class BackgroundScraper:
    """
    Background scraper that discovers and caches company email domains.
    """
    
    def __init__(self, rate_limit_delay: float = 3.0):
        """
        Initialize the scraper.
        
        Args:
            rate_limit_delay: Minimum seconds between scraping requests
        """
        self.rate_limiter = RateLimiter(min_delay=rate_limit_delay, max_delay=rate_limit_delay + 2)
        self.stats = {
            "processed": 0,
            "cached": 0,
            "found": 0,
            "failed": 0,
            "skipped": 0,
        }
    
    def is_already_cached(self, company_name: str) -> bool:
        """Check if a company is already in the cache."""
        cached = get_cached_domain(company_name)
        return cached is not None
    
    def scrape_company(self, company: dict) -> bool:
        """
        Scrape a single company and cache the result.
        
        Returns True if domain was found, False otherwise.
        """
        name = company.get("name")
        if not name:
            return False
        
        self.stats["processed"] += 1
        
        # Skip if already cached
        if self.is_already_cached(name):
            print(f"  [SKIP] {name} - already cached")
            self.stats["skipped"] += 1
            self.stats["cached"] += 1
            return True
        
        # Apply rate limiting
        self.rate_limiter.wait()
        
        print(f"\n  [SCRAPE] {name}...")
        
        try:
            result = find_company_domain(name)
            
            if result and result.get("email_domain"):
                domain = result["email_domain"]
                if not is_excluded(domain):
                    print(f"  [FOUND] {name} → {domain}")
                    self.stats["found"] += 1
                    return True
            
            print(f"  [FAIL] {name} - no domain found")
            self.stats["failed"] += 1
            return False
            
        except Exception as e:
            print(f"  [ERROR] {name}: {e}")
            self.stats["failed"] += 1
            return False
    
    def scrape_source(self, source: str) -> dict:
        """
        Scrape companies from a specific source.
        
        Args:
            source: One of 'yc', 'seed', 'tech', 'all'
            
        Returns:
            Stats dictionary
        """
        self.stats = {
            "processed": 0,
            "cached": 0,
            "found": 0,
            "failed": 0,
            "skipped": 0,
            "source": source,
            "started_at": datetime.now().isoformat(),
        }
        
        # Get company generator based on source
        if source == "yc":
            companies = get_yc_companies()
        elif source == "seed":
            companies = get_companies_from_seed_data()
        elif source == "tech":
            companies = get_tech_companies_list()
        elif source == "all":
            # Chain all sources
            import itertools
            companies = itertools.chain(
                get_companies_from_seed_data(),
                get_tech_companies_list(),
                get_yc_companies(),
            )
        else:
            print(f"Unknown source: {source}")
            return self.stats
        
        print(f"\n{'='*60}")
        print(f"Starting background scrape: {source}")
        print(f"{'='*60}")
        
        for company in companies:
            self.scrape_company(company)
        
        self.stats["finished_at"] = datetime.now().isoformat()
        
        print(f"\n{'='*60}")
        print(f"Scrape complete: {source}")
        print(f"  Processed: {self.stats['processed']}")
        print(f"  Found: {self.stats['found']}")
        print(f"  Already cached: {self.stats['skipped']}")
        print(f"  Failed: {self.stats['failed']}")
        print(f"{'='*60}")
        
        return self.stats
    
    def run_continuous(self, interval_hours: float = 24):
        """
        Run the scraper continuously, re-scraping all sources periodically.
        
        Args:
            interval_hours: Hours between full scrapes
        """
        print(f"\nStarting continuous scraper (interval: {interval_hours}h)")
        
        while True:
            try:
                # Scrape all sources
                self.scrape_source("all")
                
                # Wait for next interval
                sleep_seconds = interval_hours * 3600
                print(f"\nSleeping for {interval_hours} hours until next scrape...")
                time.sleep(sleep_seconds)
                
            except KeyboardInterrupt:
                print("\nScraper stopped by user")
                break
            except Exception as e:
                print(f"\nError in continuous scraper: {e}")
                # Wait a bit before retrying
                time.sleep(300)


def get_scraper_status() -> dict:
    """
    Get the current status of the scraper/database.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Total cached companies
        cursor.execute("SELECT COUNT(*) as count FROM company_domains")
        total = cursor.fetchone()["count"]
        
        # By source
        cursor.execute("""
            SELECT source, COUNT(*) as count 
            FROM company_domains 
            GROUP BY source
        """)
        by_source = {row["source"]: row["count"] for row in cursor.fetchall()}
        
        # Recent additions
        cursor.execute("""
            SELECT company_name, email_domain, source, created_at
            FROM company_domains
            ORDER BY created_at DESC
            LIMIT 10
        """)
        recent = [dict(row) for row in cursor.fetchall()]
        
        return {
            "total_cached": total,
            "by_source": by_source,
            "recent_additions": recent,
        }


# ============================================
# CLI
# ============================================

def main():
    parser = argparse.ArgumentParser(description="Background company domain scraper")
    parser.add_argument(
        "--source",
        choices=["yc", "seed", "tech", "all"],
        default="all",
        help="Source to scrape (default: all)"
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Run continuously with periodic re-scrapes"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=24,
        help="Hours between scrapes in continuous mode (default: 24)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="Minimum seconds between requests (default: 3.0)"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show scraper/database status and exit"
    )
    
    args = parser.parse_args()
    
    if args.status:
        status = get_scraper_status()
        print("\n=== Scraper Status ===")
        print(f"Total cached companies: {status['total_cached']}")
        print(f"\nBy source:")
        for source, count in status['by_source'].items():
            print(f"  {source}: {count}")
        print(f"\nRecent additions:")
        for entry in status['recent_additions']:
            print(f"  {entry['company_name']} → {entry['email_domain']} ({entry['source']})")
        return
    
    scraper = BackgroundScraper(rate_limit_delay=args.delay)
    
    if args.continuous:
        scraper.run_continuous(interval_hours=args.interval)
    else:
        scraper.scrape_source(args.source)


if __name__ == "__main__":
    main()

