"""
Phidexion Feature Extraction Engine
Extracts structural, domain-based (WHOIS, DNS, SSL), and content/protocol features
from URLs for machine learning phishing detection.
"""

import re
import socket
import ssl
from urllib.parse import urlparse
import datetime
import tldextract
import dns.resolver

# Known URL shorteners
SHORTENERS = {
    "bit.ly", "tinyurl.com", "goo.gl", "rebrand.ly", "t.co", "is.gd",
    "buff.ly", "ow.ly", "cutt.ly", "tiny.cc", "bit.do", "shorte.st"
}

# Suspicious keywords commonly seen in phishing attempts
SUSPICIOUS_KEYWORDS = [
    "login", "verify", "verification", "secure", "banking", "update",
    "account", "confirm", "wallet", "password", "support", "signin",
    "auth", "ebayisapi", "webscr", "pay", "recover", "authenticate"
]

# Established popular domains with default high trust metadata cache
TRUSTED_DOMAINS = {
    "google.com": {"age_years": 27, "ssl": 1, "mx": 1},
    "bankofamerica.com": {"age_years": 25, "ssl": 1, "mx": 0},
    "microsoft.com": {"age_years": 33, "ssl": 1, "mx": 1},
    "apple.com": {"age_years": 37, "ssl": 1, "mx": 1},
    "amazon.com": {"age_years": 30, "ssl": 1, "mx": 1},
    "paypal.com": {"age_years": 25, "ssl": 1, "mx": 1},
    "chase.com": {"age_years": 28, "ssl": 1, "mx": 1},
    "wellsfargo.com": {"age_years": 29, "ssl": 1, "mx": 1},
    "github.com": {"age_years": 16, "ssl": 1, "mx": 1},
    "wikipedia.org": {"age_years": 23, "ssl": 1, "mx": 1},
    "netflix.com": {"age_years": 26, "ssl": 1, "mx": 1},
    "yahoo.com": {"age_years": 29, "ssl": 1, "mx": 1},
    "facebook.com": {"age_years": 20, "ssl": 1, "mx": 1},
    "instagram.com": {"age_years": 14, "ssl": 1, "mx": 1},
    "twitter.com": {"age_years": 18, "ssl": 1, "mx": 1},
    "linkedin.com": {"age_years": 21, "ssl": 1, "mx": 1}
}


def normalize_url(url: str) -> str:
    """Ensure URL has a scheme for reliable parsing."""
    url = url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    return url


def is_ip_address(hostname: str) -> int:
    """Check if the hostname is an IPv4 or IPv6 address."""
    # IPv4 regex
    ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if re.match(ipv4_pattern, hostname):
        return 1
    # Hex or IPv6 heuristic
    if ":" in hostname or hostname.startswith("0x"):
        return 1
    return 0


def check_shortening_service(hostname: str) -> int:
    """Detect if URL uses a known URL shortening service."""
    for shortener in SHORTENERS:
        if shortener in hostname.lower():
            return 1
    return 0


def check_ssl_validity(hostname: str, port: int = 443, timeout: float = 1.5) -> int:
    """Check if the domain has a valid SSL/TLS certificate."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                if cert:
                    return 1
    except Exception:
        pass
    return 0


def check_mail_server(domain: str, timeout: float = 1.2) -> int:
    """Check if MX (Mail Server) records exist for the domain."""
    try:
        resolver = dns.resolver.Resolver()
        resolver.lifetime = timeout
        answers = resolver.resolve(domain, 'MX')
        if len(answers) > 0:
            return 1
    except Exception:
        pass
    return 0


def get_domain_age_days(domain: str) -> tuple[int, str]:
    """
    Get domain registration age in days and years.
    Returns (age_in_days, formatted_string_display).
    """
    # Check trusted cache first for instant response
    for trusted_dom, meta in TRUSTED_DOMAINS.items():
        if domain.endswith(trusted_dom):
            years = meta["age_years"]
            return years * 365, f"{years} years"

    # Fast heuristic WHOIS check with timeout
    try:
        import whois
        w = whois.whois(domain)
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if creation_date:
            if isinstance(creation_date, datetime.datetime):
                age_days = (datetime.datetime.now() - creation_date).days
                if age_days > 365:
                    years = round(age_days / 365, 1)
                    return age_days, f"{int(years)} years"
                return max(1, age_days), f"{max(1, age_days)} days"
    except Exception:
        pass

    # Default heuristic for non-cached or unreachable domains
    # Phishing domains are often newly registered (e.g. 5 to 30 days)
    return 15, "15 days"


def extract_url_features(raw_url: str, fast_mode: bool = False) -> dict:
    """
    Extract complete multi-tier features from an input URL.
    Returns both the numeric feature vector for ML and human-readable key details.
    """
    url = normalize_url(raw_url)
    parsed = urlparse(url)
    
    hostname = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""
    
    extracted = tldextract.extract(url)
    registered_domain = f"{extracted.domain}.{extracted.suffix}" if extracted.suffix else extracted.domain
    subdomain = extracted.subdomain

    # 1. Structural / Lexical Features
    url_len = len(url)
    having_ip = is_ip_address(hostname)
    shortened = check_shortening_service(hostname)
    at_symbol = 1 if "@" in url else 0
    double_slash = 1 if "//" in url[7:] else 0
    prefix_suffix = 1 if "-" in (extracted.domain or "") else 0
    
    subdomain_count = len(subdomain.split(".")) if subdomain else 0
    special_chars_count = sum(url.count(c) for c in ["-", "_", "?", "=", "%", "&", "@", "!", "$", "~"])
    digits_count = sum(c.isdigit() for c in url)
    https_in_domain = 1 if "https" in hostname.lower() else 0
    suspicious_keyword_flag = 1 if any(kw in url.lower() for kw in SUSPICIOUS_KEYWORDS) else 0

    # 2. Domain & SSL/TLS Features
    # Check trusted domains cache first
    cached_info = None
    for trusted_dom, meta in TRUSTED_DOMAINS.items():
        if registered_domain.endswith(trusted_dom):
            cached_info = meta
            break

    if cached_info:
        ssl_valid = cached_info["ssl"]
        mail_server = cached_info["mx"]
        domain_age_days = cached_info["age_years"] * 365
        domain_age_display = f"{cached_info['age_years']} years"
    elif fast_mode:
        # Fast estimation for dataset batch processing
        ssl_valid = 1 if parsed.scheme == "https" and not having_ip and prefix_suffix == 0 else 0
        mail_server = 1 if suspicious_keyword_flag == 0 and len(url) < 45 else 0
        domain_age_days = 365 * 4 if (ssl_valid == 1 and not shortened) else 7
        domain_age_display = "4 years" if domain_age_days > 365 else f"{domain_age_days} days"
    else:
        # Live inspection
        ssl_valid = check_ssl_validity(hostname) if parsed.scheme == "https" else 0
        mail_server = check_mail_server(registered_domain)
        domain_age_days, domain_age_display = get_domain_age_days(registered_domain)

    # Human-readable status for UI Display (Key Details in Mockup)
    ssl_display = "Valid" if ssl_valid == 1 else "Invalid"
    mail_server_display = "Present" if mail_server == 1 else "Not Present"

    # Numeric feature dictionary matching model feature columns
    features = {
        "url_length": url_len,
        "domain_age": round(domain_age_days / 365.0, 2),  # In years
        "ssl_certificate": ssl_valid,
        "mail_server_presence": mail_server,
        "subdomain_count": subdomain_count,
        "special_characters": special_chars_count,
        "having_ip_address": having_ip,
        "shortening_service": shortened,
        "having_at_symbol": at_symbol,
        "double_slash_redirecting": double_slash,
        "prefix_suffix": prefix_suffix,
        "https_in_domain": https_in_domain,
        "suspicious_keywords": suspicious_keyword_flag,
        "digits_count": digits_count
    }

    key_details = {
        "url_length_display": f"{url_len} characters",
        "domain_age_display": domain_age_display,
        "ssl_certificate_display": ssl_display,
        "mail_server_display": mail_server_display,
        "domain": registered_domain or hostname,
        "protocol": parsed.scheme.upper()
    }

    return {
        "url": url,
        "features": features,
        "key_details": key_details
    }


if __name__ == "__main__":
    test_urls = [
        "https://www.bankofamerica.com",
        "http://secure-login-update.com"
    ]
    for u in test_urls:
        res = extract_url_features(u, fast_mode=True)
        print(f"URL: {u}")
        print("Features:", res["features"])
        print("Key Details:", res["key_details"])
        print("-" * 50)
