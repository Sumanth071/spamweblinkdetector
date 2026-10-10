"""
Dataset Generator & Preprocessor for Phidexion
Generates a representative, labeled phishing vs legitimate dataset (6,000 samples)
using real-world feature distributions matching the research design.
"""

import os
import random
import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "phishing_dataset.csv")

def generate_synthetic_dataset(num_samples: int = 6000) -> pd.DataFrame:
    half = num_samples // 2

    # --- 1. LEGITIMATE SAMPLES (Label = 0) ---
    # Legitimate sites generally have:
    # - Older domain age (1 to 25 years)
    # - Valid SSL certificates (95%+ valid)
    # - Shorter or standard URL lengths (15 to 45 chars)
    # - Mail servers configured (MX present ~85%)
    # - Low subdomain count (0 to 2)
    # - Low special characters (1 to 4)
    # - Almost never IP address hosts (0%)
    # - Low presence of URL shorteners (2%)
    # - Rare suspicious keywords in URL string (3%)
    
    legit_domain_age = np.clip(np.random.gamma(shape=5.0, scale=2.5, size=half), 1.0, 30.0)
    legit_ssl = np.random.choice([1, 0], size=half, p=[0.97, 0.03])
    legit_url_len = np.clip(np.random.normal(loc=28, scale=8, size=half), 14, 65).astype(int)
    legit_mx = np.random.choice([1, 0], size=half, p=[0.88, 0.12])
    legit_subdomains = np.random.choice([0, 1, 2], size=half, p=[0.60, 0.35, 0.05])
    legit_special_chars = np.random.poisson(lam=1.5, size=half)
    legit_ip_addr = np.zeros(half, dtype=int)
    legit_shortened = np.random.choice([1, 0], size=half, p=[0.02, 0.98])
    legit_at_symbol = np.zeros(half, dtype=int)
    legit_double_slash = np.random.choice([1, 0], size=half, p=[0.01, 0.99])
    legit_prefix_suffix = np.random.choice([1, 0], size=half, p=[0.05, 0.95])
    legit_https_domain = np.zeros(half, dtype=int)
    legit_suspicious_kw = np.random.choice([1, 0], size=half, p=[0.04, 0.96])
    legit_digits = np.random.poisson(lam=0.8, size=half)
    legit_labels = np.zeros(half, dtype=int)

    # --- 2. PHISHING SAMPLES (Label = 1) ---
    # Phishing sites typically have:
    # - Very new domain age (0.01 to 0.8 years = few days to months)
    # - Invalid / self-signed / expired SSL (or free brief certs, ~75% invalid/missing)
    # - Longer URLs with deep paths/queries (40 to 120 chars)
    # - Mail servers often missing or disposable (~70% not present)
    # - High subdomain count (2 to 6 subdomains to mimic legitimate brand names)
    # - High special characters and hyphens (brand-login-update)
    # - IP addresses used as hostname in ~15% of cases
    # - URL shorteners used in ~18% of cases
    # - Frequent suspicious keywords (login, verify, update, account) in 78%
    
    phish_domain_age = np.clip(np.random.exponential(scale=0.25, size=half), 0.01, 2.5)
    phish_ssl = np.random.choice([1, 0], size=half, p=[0.24, 0.76])
    phish_url_len = np.clip(np.random.normal(loc=58, scale=18, size=half), 30, 140).astype(int)
    phish_mx = np.random.choice([1, 0], size=half, p=[0.28, 0.72])
    phish_subdomains = np.random.choice([1, 2, 3, 4, 5], size=half, p=[0.15, 0.35, 0.30, 0.15, 0.05])
    phish_special_chars = np.random.poisson(lam=5.2, size=half)
    phish_ip_addr = np.random.choice([1, 0], size=half, p=[0.14, 0.86])
    phish_shortened = np.random.choice([1, 0], size=half, p=[0.16, 0.84])
    phish_at_symbol = np.random.choice([1, 0], size=half, p=[0.12, 0.88])
    phish_double_slash = np.random.choice([1, 0], size=half, p=[0.10, 0.90])
    phish_prefix_suffix = np.random.choice([1, 0], size=half, p=[0.48, 0.52])
    phish_https_domain = np.random.choice([1, 0], size=half, p=[0.20, 0.80])
    phish_suspicious_kw = np.random.choice([1, 0], size=half, p=[0.82, 0.18])
    phish_digits = np.random.poisson(lam=5.5, size=half)
    phish_labels = np.ones(half, dtype=int)

    # Combine datasets
    data = {
        "domain_age": np.concatenate([legit_domain_age, phish_domain_age]),
        "ssl_certificate": np.concatenate([legit_ssl, phish_ssl]),
        "url_length": np.concatenate([legit_url_len, phish_url_len]),
        "mail_server_presence": np.concatenate([legit_mx, phish_mx]),
        "subdomain_count": np.concatenate([legit_subdomains, phish_subdomains]),
        "special_characters": np.concatenate([legit_special_chars, phish_special_chars]),
        "having_ip_address": np.concatenate([legit_ip_addr, phish_ip_addr]),
        "shortening_service": np.concatenate([legit_shortened, phish_shortened]),
        "having_at_symbol": np.concatenate([legit_at_symbol, phish_at_symbol]),
        "double_slash_redirecting": np.concatenate([legit_double_slash, phish_double_slash]),
        "prefix_suffix": np.concatenate([legit_prefix_suffix, phish_prefix_suffix]),
        "https_in_domain": np.concatenate([legit_https_domain, phish_https_domain]),
        "suspicious_keywords": np.concatenate([legit_suspicious_kw, phish_suspicious_kw]),
        "digits_count": np.concatenate([legit_digits, phish_digits]),
        "label": np.concatenate([legit_labels, phish_labels])
    }

    df = pd.DataFrame(data)
    # Shuffle dataframe
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    return df

if __name__ == "__main__":
    print("[*] Generating Phidexion labeled dataset...")
    df = generate_synthetic_dataset(6000)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"[+] Dataset saved to {OUTPUT_FILE} with shape {df.shape}")
    print(f"[+] Label distribution:\n{df['label'].value_counts()}")
