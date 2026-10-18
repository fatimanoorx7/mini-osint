#!/usr/bin/env python3
"""
report.py
Combines subdomains.json, emails.json, and breach_results.json into one
unified report with a basic exposure score and interesting-subdomain flagging.
"""

import json
import sys


INTERESTING_KEYWORDS = [
    "admin", "dev", "staging", "stage", "test", "vpn", "internal",
    "api", "backup", "db", "database", "git", "jenkins", "portal",
    "remote", "ftp", "mail", "secure", "login", "sso", "beta"
]


def load_json(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[!] Missing file: {filepath} — run the earlier steps first.")
        sys.exit(1)


def calculate_exposure_score(subdomain_count, resolving_count, email_count, breached_count):
    """
    Simple weighted score — not a standardized metric, just a project-defined
    way to rank overall exposure. Documented as such in the README.
    """
    score = 0
    score += resolving_count * 1       # each live subdomain = 1 point
    score += breached_count * 10       # each breached email = 10 points (high weight)
    score += (subdomain_count - resolving_count) * 0.2  # dead subdomains = low weight
    return round(score, 1)


def flag_interesting(subdomain):
    """Flag a subdomain as interesting if it contains common high-value keywords."""
    sub_lower = subdomain.lower()
    for keyword in INTERESTING_KEYWORDS:
        if keyword in sub_lower:
            return keyword
    return None


def main():
    sub_data = load_json("output/subdomains.json")
    email_data = load_json("output/emails.json")
    breach_data = load_json("output/breach_results.json")

    domain = sub_data.get("domain", "unknown")

    subdomains = sub_data.get("subdomains", [])
    subdomain_count = len(subdomains)
    resolving_count = sum(1 for s in subdomains if s.get("resolves"))

    # Flag interesting subdomains
    for sub in subdomains:
        matched_keyword = flag_interesting(sub["subdomain"])
        sub["interesting"] = matched_keyword is not None
        sub["matched_keyword"] = matched_keyword

    interesting_count = sum(1 for s in subdomains if s["interesting"])

    emails = email_data.get("generated_emails", [])
    email_count = len(emails)

    breach_results = breach_data.get("results", [])
    breached_count = breach_data.get("breached_count", 0)

    score = calculate_exposure_score(subdomain_count, resolving_count, email_count, breached_count)

    report = {
        "domain": domain,
        "summary": {
            "subdomains_found": subdomain_count,
            "subdomains_resolving": resolving_count,
            "subdomains_interesting": interesting_count,
            "emails_generated": email_count,
            "emails_breached": breached_count,
            "exposure_score": score
        },
        "subdomains": subdomains,
        "emails": breach_results  # includes breach status per email
    }

    with open("output/final_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"[+] Combined report for {domain}")
    print(f"    Subdomains found:     {subdomain_count} ({resolving_count} resolving, {interesting_count} flagged interesting)")
    print(f"    Emails generated:     {email_count}")
    print(f"    Emails breached:      {breached_count}")
    print(f"    Exposure score:       {score}")
    print(f"\n[+] Saved to output/final_report.json")


if __name__ == "__main__":
    main()