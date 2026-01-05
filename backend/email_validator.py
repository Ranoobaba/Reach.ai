"""
Email validation and scoring module.
Provides conservative email validation without SMTP verification.
"""

import re
import dns.resolver
from typing import Optional
from dataclasses import dataclass

from blocklists import is_disposable_domain, is_role_based_email, is_free_provider
from database import get_dns_cache, cache_dns_result


# Scoring weights
SCORE_SYNTAX_VALID = 20
SCORE_DOMAIN_EXISTS = 20
SCORE_MX_RECORDS = 25
SCORE_NOT_DISPOSABLE = 15
SCORE_NOT_ROLE_BASED = 10
SCORE_NOT_FREE_PROVIDER = 10

# Max possible score
MAX_SCORE = (
    SCORE_SYNTAX_VALID + 
    SCORE_DOMAIN_EXISTS + 
    SCORE_MX_RECORDS + 
    SCORE_NOT_DISPOSABLE + 
    SCORE_NOT_ROLE_BASED + 
    SCORE_NOT_FREE_PROVIDER
)

# Email regex pattern (RFC 5322 simplified)
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)

# Valid TLDs (common ones for quick validation)
COMMON_TLDS = {
    "com", "org", "net", "edu", "gov", "mil", "int",
    "io", "ai", "co", "dev", "app", "me", "info", "biz",
    "us", "uk", "ca", "au", "de", "fr", "es", "it", "nl", "be",
    "ch", "at", "se", "no", "dk", "fi", "pl", "ru", "jp", "cn",
    "in", "br", "mx", "ar", "za", "nz", "ie", "pt", "cz", "hu",
    "ro", "gr", "tr", "il", "ae", "sg", "hk", "tw", "kr", "th",
    "vn", "id", "ph", "my", "pk", "bd", "lk", "np",
    "tech", "online", "site", "website", "store", "shop", "blog",
    "cloud", "email", "digital", "agency", "studio", "design",
    "software", "solutions", "services", "consulting", "group",
    "company", "business", "finance", "legal", "health", "media",
    "news", "social", "network", "systems", "technology",
}


@dataclass
class ValidationResult:
    """Result of email validation with detailed breakdown."""
    email: str
    score: int
    max_score: int
    breakdown: dict
    is_valid: bool
    
    def to_dict(self) -> dict:
        return {
            "email": self.email,
            "score": self.score,
            "max_score": self.max_score,
            "breakdown": self.breakdown,
            "is_valid": self.is_valid,
        }


def validate_syntax(email: str) -> tuple[bool, str]:
    """
    Validate email syntax using regex.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email or not isinstance(email, str):
        return False, "Email is empty or not a string"
    
    email = email.strip().lower()
    
    # Check basic structure
    if "@" not in email:
        return False, "Missing @ symbol"
    
    parts = email.split("@")
    if len(parts) != 2:
        return False, "Invalid email format - multiple @ symbols"
    
    local_part, domain = parts
    
    # Check local part
    if not local_part:
        return False, "Empty local part (before @)"
    if len(local_part) > 64:
        return False, "Local part too long (max 64 characters)"
    
    # Check domain
    if not domain:
        return False, "Empty domain part (after @)"
    if len(domain) > 253:
        return False, "Domain too long (max 253 characters)"
    if "." not in domain:
        return False, "Domain must have at least one dot"
    
    # Check TLD
    tld = domain.split(".")[-1]
    if len(tld) < 2:
        return False, "TLD too short"
    
    # Check against regex
    if not EMAIL_REGEX.match(email):
        return False, "Invalid characters in email"
    
    return True, ""


def check_dns_records(domain: str, use_cache: bool = True) -> dict:
    """
    Check DNS records for a domain (A and MX records).
    
    Args:
        domain: The domain to check
        use_cache: Whether to use cached results
        
    Returns:
        dict with has_a, has_mx, mx_records, error fields
    """
    # Check cache first
    if use_cache:
        cached = get_dns_cache(domain)
        if cached:
            return cached
    
    result = {
        "domain": domain,
        "has_a": False,
        "has_mx": False,
        "mx_records": [],
        "error": None,
    }
    
    try:
        # Check A record (domain exists)
        try:
            dns.resolver.resolve(domain, 'A')
            result["has_a"] = True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            # Try AAAA record as fallback
            try:
                dns.resolver.resolve(domain, 'AAAA')
                result["has_a"] = True
            except:
                pass
        except Exception:
            pass
        
        # Check MX records
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            result["has_mx"] = True
            result["mx_records"] = [
                {"priority": r.preference, "host": str(r.exchange).rstrip('.')}
                for r in mx_records
            ]
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            pass
        except Exception:
            pass
        
    except Exception as e:
        result["error"] = str(e)
    
    # Cache the result
    if use_cache:
        cache_dns_result(domain, result)
    
    return result


def calculate_score(email: str, dns_info: Optional[dict] = None) -> ValidationResult:
    """
    Calculate a comprehensive validation score for an email.
    
    Args:
        email: The email address to validate
        dns_info: Optional pre-fetched DNS info to avoid duplicate lookups
        
    Returns:
        ValidationResult with score and breakdown
    """
    email = email.strip().lower()
    score = 0
    breakdown = {}
    
    # 1. Syntax validation (20 points)
    syntax_valid, syntax_error = validate_syntax(email)
    if syntax_valid:
        score += SCORE_SYNTAX_VALID
        breakdown["syntax"] = {"valid": True, "points": SCORE_SYNTAX_VALID}
    else:
        breakdown["syntax"] = {"valid": False, "points": 0, "error": syntax_error}
        # If syntax is invalid, return early with zero score
        return ValidationResult(
            email=email,
            score=0,
            max_score=MAX_SCORE,
            breakdown=breakdown,
            is_valid=False,
        )
    
    # Extract domain for further checks
    domain = email.split("@")[-1]
    
    # 2. DNS checks (20 + 25 = 45 points)
    if dns_info is None:
        dns_info = check_dns_records(domain)
    
    # Domain exists (A record) - 20 points
    if dns_info.get("has_a"):
        score += SCORE_DOMAIN_EXISTS
        breakdown["domain_exists"] = {"valid": True, "points": SCORE_DOMAIN_EXISTS}
    else:
        breakdown["domain_exists"] = {"valid": False, "points": 0}
    
    # MX records present - 25 points
    if dns_info.get("has_mx"):
        score += SCORE_MX_RECORDS
        breakdown["mx_records"] = {
            "valid": True, 
            "points": SCORE_MX_RECORDS,
            "records": dns_info.get("mx_records", [])[:3]  # Limit to first 3
        }
    else:
        breakdown["mx_records"] = {"valid": False, "points": 0}
    
    # 3. Not disposable (15 points)
    if not is_disposable_domain(domain):
        score += SCORE_NOT_DISPOSABLE
        breakdown["not_disposable"] = {"valid": True, "points": SCORE_NOT_DISPOSABLE}
    else:
        breakdown["not_disposable"] = {"valid": False, "points": 0, "reason": "Disposable email domain"}
    
    # 4. Not role-based (10 points)
    if not is_role_based_email(email):
        score += SCORE_NOT_ROLE_BASED
        breakdown["not_role_based"] = {"valid": True, "points": SCORE_NOT_ROLE_BASED}
    else:
        breakdown["not_role_based"] = {"valid": False, "points": 0, "reason": "Role-based email address"}
    
    # 5. Not free provider (10 points)
    if not is_free_provider(domain):
        score += SCORE_NOT_FREE_PROVIDER
        breakdown["not_free_provider"] = {"valid": True, "points": SCORE_NOT_FREE_PROVIDER}
    else:
        breakdown["not_free_provider"] = {"valid": False, "points": 0, "reason": "Free email provider"}
    
    # Determine if email is valid (has at least syntax + domain)
    is_valid = syntax_valid and (dns_info.get("has_a") or dns_info.get("has_mx"))
    
    return ValidationResult(
        email=email,
        score=score,
        max_score=MAX_SCORE,
        breakdown=breakdown,
        is_valid=is_valid,
    )


def validate_emails_batch(emails: list[str]) -> list[ValidationResult]:
    """
    Validate a batch of emails efficiently.
    Groups emails by domain to minimize DNS lookups.
    
    Args:
        emails: List of email addresses to validate
        
    Returns:
        List of ValidationResult objects
    """
    results = []
    
    # Group emails by domain for efficient DNS caching
    domain_emails: dict[str, list[str]] = {}
    for email in emails:
        email = email.strip().lower()
        if "@" in email:
            domain = email.split("@")[-1]
            if domain not in domain_emails:
                domain_emails[domain] = []
            domain_emails[domain].append(email)
        else:
            # Invalid email, add directly with zero score
            results.append(ValidationResult(
                email=email,
                score=0,
                max_score=MAX_SCORE,
                breakdown={"syntax": {"valid": False, "error": "Missing @ symbol", "points": 0}},
                is_valid=False,
            ))
    
    # Process each domain group
    for domain, domain_email_list in domain_emails.items():
        # Fetch DNS info once per domain
        dns_info = check_dns_records(domain)
        
        # Score each email in this domain
        for email in domain_email_list:
            result = calculate_score(email, dns_info)
            results.append(result)
    
    return results


def get_score_label(score: int) -> str:
    """
    Get a human-readable label for a validation score.
    
    Args:
        score: The validation score (0-100)
        
    Returns:
        Label string (e.g., "Excellent", "Good", "Fair", "Poor")
    """
    if score >= 90:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 50:
        return "Fair"
    elif score >= 30:
        return "Poor"
    else:
        return "Invalid"

