import sqlite3
import os
from datetime import datetime, timedelta
from contextlib import contextmanager

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), "email_cache.db")


def init_db():
    """Initialize the database with required tables."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Table for caching company → email domain mappings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_domains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                company_name_normalized TEXT NOT NULL UNIQUE,
                email_domain TEXT NOT NULL,
                website_url TEXT,
                source TEXT DEFAULT 'search',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 1
            )
        """)
        
        # Index for fast lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_company_normalized 
            ON company_domains(company_name_normalized)
        """)
        
        # Table for tracking API usage (for rate limiting awareness)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_name TEXT NOT NULL,
                request_count INTEGER DEFAULT 0,
                last_request TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date TEXT NOT NULL
            )
        """)
        
        conn.commit()
        print(f"Database initialized at {DB_PATH}")


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def normalize_company_name(company_name: str) -> str:
    """
    Normalize company name for consistent lookups.
    Removes common suffixes, lowercases, strips whitespace.
    """
    name = company_name.lower().strip()
    
    # Remove common company suffixes
    suffixes = [
        " inc", " inc.", " incorporated",
        " llc", " l.l.c.", " llc.",
        " ltd", " ltd.", " limited",
        " corp", " corp.", " corporation",
        " co", " co.", " company",
        " gmbh", " ag", " sa", " plc",
        " technologies", " technology", " tech",
        " software", " solutions", " services",
        " labs", " lab", " ai", " io",
    ]
    
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    
    # Remove special characters, keep only alphanumeric and spaces
    name = "".join(c for c in name if c.isalnum() or c == " ")
    
    # Remove extra whitespace
    name = " ".join(name.split())
    
    return name


def get_cached_domain(company_name: str) -> dict | None:
    """
    Look up a company's email domain from the cache.
    Returns dict with domain info or None if not found.
    """
    normalized = normalize_company_name(company_name)
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT company_name, email_domain, website_url, source, created_at
            FROM company_domains
            WHERE company_name_normalized = ?
        """, (normalized,))
        
        row = cursor.fetchone()
        
        if row:
            # Update access stats
            cursor.execute("""
                UPDATE company_domains
                SET last_accessed = CURRENT_TIMESTAMP, access_count = access_count + 1
                WHERE company_name_normalized = ?
            """, (normalized,))
            conn.commit()
            
            return {
                "company_name": row["company_name"],
                "email_domain": row["email_domain"],
                "website_url": row["website_url"],
                "source": row["source"],
                "cached_at": row["created_at"],
                "from_cache": True
            }
    
    return None


def cache_domain(company_name: str, email_domain: str, website_url: str = None, source: str = "search"):
    """
    Store a company's email domain in the cache.
    """
    normalized = normalize_company_name(company_name)
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Use INSERT OR REPLACE to handle duplicates
        cursor.execute("""
            INSERT OR REPLACE INTO company_domains 
            (company_name, company_name_normalized, email_domain, website_url, source, created_at, last_accessed, access_count)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 
                COALESCE((SELECT access_count FROM company_domains WHERE company_name_normalized = ?), 0) + 1)
        """, (company_name, normalized, email_domain, website_url, source, normalized))
        
        conn.commit()
        print(f"Cached: {company_name} → {email_domain}")


def get_cache_stats() -> dict:
    """Get statistics about the cache."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Total entries
        cursor.execute("SELECT COUNT(*) as count FROM company_domains")
        total = cursor.fetchone()["count"]
        
        # Most accessed
        cursor.execute("""
            SELECT company_name, email_domain, access_count 
            FROM company_domains 
            ORDER BY access_count DESC 
            LIMIT 10
        """)
        top_accessed = [dict(row) for row in cursor.fetchall()]
        
        # Recently added
        cursor.execute("""
            SELECT company_name, email_domain, created_at 
            FROM company_domains 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        recent = [dict(row) for row in cursor.fetchall()]
        
        return {
            "total_entries": total,
            "top_accessed": top_accessed,
            "recently_added": recent
        }


def search_cache(query: str, limit: int = 20) -> list[dict]:
    """Search the cache for companies matching a query."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT company_name, email_domain, website_url, access_count
            FROM company_domains
            WHERE company_name LIKE ? OR company_name_normalized LIKE ?
            ORDER BY access_count DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))
        
        return [dict(row) for row in cursor.fetchall()]


def bulk_import_domains(entries: list[dict]):
    """
    Bulk import company → domain mappings.
    Useful for seeding the cache with known data.
    
    entries: list of {"company_name": str, "email_domain": str, "website_url": str (optional)}
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        for entry in entries:
            normalized = normalize_company_name(entry["company_name"])
            cursor.execute("""
                INSERT OR IGNORE INTO company_domains 
                (company_name, company_name_normalized, email_domain, website_url, source)
                VALUES (?, ?, ?, ?, 'import')
            """, (
                entry["company_name"],
                normalized,
                entry["email_domain"],
                entry.get("website_url")
            ))
        
        conn.commit()
        print(f"Imported {len(entries)} entries")


def delete_cached_domain(company_name: str) -> bool:
    """
    Delete a company from the cache.
    Returns True if deleted, False if not found.
    """
    normalized = normalize_company_name(company_name)
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM company_domains
            WHERE company_name_normalized = ?
        """, (normalized,))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        
        if deleted:
            print(f"Deleted cache entry for: {company_name}")
        else:
            print(f"No cache entry found for: {company_name}")
        
        return deleted


# Initialize the database when module is imported
init_db()

