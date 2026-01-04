def generate_email_permutations(first_name: str, last_name: str, domain: str) -> list[str]:
    """
    Generate 30 common email permutations based on first name, last name, and domain.
    """
    first = first_name.lower().strip()
    last = last_name.lower().strip()
    f = first[0] if first else ""
    l = last[0] if last else ""
    
    patterns = [
        # First name based
        f"{first}",
        # Last name based
        f"{last}",
        # First + Last combinations
        f"{first}{last}",
        f"{first}.{last}",
        f"{first}_{last}",
        f"{first}-{last}",
        # Last + First combinations
        f"{last}{first}",
        f"{last}.{first}",
        f"{last}_{first}",
        f"{last}-{first}",
        # Initial + Last name
        f"{f}{last}",
        f"{f}.{last}",
        f"{f}_{last}",
        f"{f}-{last}",
        # First name + Initial
        f"{first}{l}",
        f"{first}.{l}",
        f"{first}_{l}",
        f"{first}-{l}",
        # Last name + Initial
        f"{last}{f}",
        f"{last}.{f}",
        f"{last}_{f}",
        f"{last}-{f}",
        # Initial + First name
        f"{l}{first}",
        f"{l}.{first}",
        # Two initials
        f"{f}{l}",
        f"{f}.{l}",
        f"{l}{f}",
        f"{l}.{f}",
        # Underscore variants
        f"{first}{last[0:3]}" if len(last) >= 3 else f"{first}{last}",
        f"{last}{first[0:3]}" if len(first) >= 3 else f"{last}{first}",
    ]
    
    # Create email addresses and remove duplicates while preserving order
    emails = []
    seen = set()
    for pattern in patterns:
        email = f"{pattern}@{domain}"
        if email not in seen:
            seen.add(email)
            emails.append(email)
    
    return emails[:30]

