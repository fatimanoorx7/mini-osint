#!/usr/bin/env python3
"""
breach_check.py
Checks a list of emails against the HaveIBeenPwned breach database.

NOTE: HIBP's email-check API requires a paid API key (~$4/month) as of
their anti-abuse policy change. This script is built against HIBP's real
API format. Set the HIBP_API_KEY environment variable to run live checks.

Without a key, this script runs in DEMO MODE using a small set of
realistic sample responses, so the full pipeline (generation -> dashboard)
can still be demonstrated end-to-end.
"""

import requests
import json
import sys
import os
import time

HIBP_API_KEY = os.environ.get("HIBP_API_KEY")

# Demo-mode sample data: a couple of emails are marked "breached" so the
# dashboard and report logic can be demonstrated without a paid API key.
DEMO_BREACH_DATA = {
    "john.smith@": ["Collection1", "LinkedIn2016"],
    "sarah.johnson@": ["Adobe2013"],
}


def check_email_live(email):
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    headers = {
        "hibp-api-key": HIBP_API_KEY,
        "User-Agent": "osint-portfolio-tool"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
    except requests.RequestException as e:
        return {"email": email, "breached": False, "breaches": [], "error": str(e)}

    if resp.status_code == 404:
        return {"email": email, "breached": False, "breaches": []}

    if resp.status_code == 429:
        time.sleep(2)
        return check_email_live(email)  # retry once after rate-limit pause

    if resp.status_code != 200:
        return {"email": email, "breached": False, "breaches": [], "error": f"HTTP {resp.status_code}"}

    data = resp.json()
    breach_names = [b.get("Name", "Unknown") for b in data]
    return {"email": email, "breached": True, "breaches": breach_names}


def check_email_demo(email):
    for prefix, breaches in DEMO_BREACH_DATA.items():
        if email.startswith(prefix):
            return {"email": email, "breached": True, "breaches": breaches}
    return {"email": email, "breached": False, "breaches": []}


def check_email(email):
    if HIBP_API_KEY:
        return check_email_live(email)
    return check_email_demo(email)


def main():
    try:
        with open("output/emails.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("[!] output/emails.json not found. Run email_generator.py first.")
        sys.exit(1)

    emails = [entry["email"] for entry in data.get("generated_emails", [])]

    mode = "LIVE (HIBP API)" if HIBP_API_KEY else "DEMO MODE (no HIBP_API_KEY set)"
    print(f"[*] Checking {len(emails)} emails — mode: {mode}\n")

    results = []
    for email in emails:
        result = check_email(email)
        status = "BREACHED" if result["breached"] else "clean"
        print(f"  {email:30s} [{status}]")
        if result["breached"]:
            print(f"      -> {', '.join(result['breaches'])}")
        results.append(result)
        if HIBP_API_KEY:
            time.sleep(1.5)  # HIBP rate limit: ~1 request per 1.5s on basic tier

    breached_count = sum(1 for r in results if r["breached"])

    with open("output/breach_results.json", "w") as f:
        json.dump({
            "domain": data.get("domain", ""),
            "mode": mode,
            "total_checked": len(results),
            "breached_count": breached_count,
            "results": results
        }, f, indent=2)

    print(f"\n[+] {breached_count} of {len(results)} emails found in breaches")
    print(f"[+] Saved to output/breach_results.json")


if __name__ == "__main__":
    main()