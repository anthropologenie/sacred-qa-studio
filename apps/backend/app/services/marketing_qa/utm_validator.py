import re
from urllib.parse import urlparse, parse_qs

REQUIRED = ("utm_source","utm_medium","utm_campaign")


def validate_utm(url: str) -> dict:
    """Check UTM parameter presence and consistency"""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    
    required_utms = ['utm_source', 'utm_medium', 'utm_campaign']
    found_utms = [p for p in required_utms if p in params]
    
    return {
        "status": "pass" if len(found_utms) == len(required_utms) else "fail",
        "found": found_utms,
        "missing": [p for p in required_utms if p not in found_utms],
        "details": f"Found {len(found_utms)}/{len(required_utms)} required UTM parameters"
    }
