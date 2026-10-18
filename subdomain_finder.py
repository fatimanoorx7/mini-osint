#!/usr/bin/env python3
"""
subdomain_finder.py
Queries crt.sh certificate transparency logs to find subdomains for a given domain.
Falls back to HackerTarget's free API if crt.sh is unavailable.
"""

import requests
import json
import sys
import time
import socket
import concurrent.futures


def find_subdomains_crtsh(domain):
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    print(f"[*] Querying crt.sh for {domain} ...")

    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 404:
                print("[!] crt.sh: no certificate data found for this domain")
                return []
            if resp.status_code == 502:
                print(f"[!] crt.sh overloaded (502), retrying in 5s... (attempt {attempt+1}/3)")
                time.sleep(5)
                continue
            resp.raise_for_status()
            break
        except requests.RequestException as e:
            print(f"[!] crt.sh error: {e}")
            return None  # signal: try fallback
    else:
        print("[!] crt.sh unavailable after 3 attempts")
        return None  # signal: try fallback

    try:
        data = resp.json()
    except json.JSONDecodeError:
        print("[!] Failed to parse crt.sh response")
        return None

    subdomains = set()
    for entry in data:
        name_value = entry.get("name_value", "")
        for sub in name_value.split("\n"):
            sub = sub.strip().lower()
            if sub and "*" not in sub:
                subdomains.add(sub)

    return sorted(subdomains)


def find_subdomains_hackertarget(domain):
    url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
    print(f"[*] Falling back to HackerTarget for {domain} ...")

    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[!] HackerTarget error: {e}")
        return []

    text = resp.text.strip()
    if "error" in text.lower() or not text:
        print("[!] HackerTarget: no results or error response")
        return []

    subdomains = set()
    for line in text.split("\n"):
        parts = line.split(",")
        if parts and parts[0]:
            subdomains.add(parts[0].strip().lower())

    return sorted(subdomains)


def check_resolves(subdomain):
    """Basic check: does this subdomain resolve to an IP? (with timeout)"""
    socket.setdefaulttimeout(3)  # don't hang forever per lookup
    try:
        socket.gethostbyname(subdomain)
        return True
    except (socket.gaierror, socket.timeout):
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python subdomain_finder.py <domain>")
        sys.exit(1)

    domain = sys.argv[1]

    subdomains = find_subdomains_crtsh(domain)
    if subdomains is None:  # crt.sh failed entirely, try fallback
        subdomains = find_subdomains_hackertarget(domain)

    print(f"\n[+] Found {len(subdomains)} unique subdomains\n")
    print("[*] Checking DNS resolution (please wait)...\n")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_sub = {executor.submit(check_resolves, sub): sub for sub in subdomains}
        for future in concurrent.futures.as_completed(future_to_sub):
            sub = future_to_sub[future]
            resolves = future.result()
            status = "RESOLVES" if resolves else "no resolve"
            print(f"  {sub}  [{status}]")
            results.append({"subdomain": sub, "resolves": resolves})

    with open("output/subdomains.json", "w") as f:
        json.dump({"domain": domain, "subdomains": results}, f, indent=2)

    print(f"\n[+] Saved to output/subdomains.json")


if __name__ == "__main__":
    main()