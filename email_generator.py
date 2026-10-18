#!/usr/bin/env python3
"""
email_generator.py
Generates common corporate email address patterns for a domain, given a list of names.
"""

import json
import sys


def generate_emails(domain, names):
    """
    names: list of (first, last) tuples
    Returns list of dicts with generated email patterns.
    """
    patterns = []

    for first, last in names:
        first = first.lower().strip()
        last = last.lower().strip()

        candidates = {
            f"{first}.{last}@{domain}",
            f"{first}{last}@{domain}",
            f"{first[0]}{last}@{domain}",
            f"{first}.{last[0]}@{domain}",
            f"{first}@{domain}",
            f"{last}.{first}@{domain}",
            f"{first[0]}.{last}@{domain}",
        }

        for email in candidates:
            patterns.append({
                "name": f"{first.title()} {last.title()}",
                "email": email
            })

    return patterns


def load_names(filepath):
    names = []
    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    first, last = parts[0], parts[-1]
                    names.append((first, last))
    except FileNotFoundError:
        print(f"[!] Names file not found: {filepath}")
        sys.exit(1)
    return names


def main():
    if len(sys.argv) != 3:
        print("Usage: python email_generator.py <domain> <names_file>")
        sys.exit(1)

    domain = sys.argv[1]
    names_file = sys.argv[2]

    names = load_names(names_file)
    print(f"[*] Generating email patterns for {domain} using {len(names)} names from {names_file}...\n")

    results = generate_emails(domain, names)

    for entry in results:
        print(f"  {entry['name']:20s} -> {entry['email']}")

    with open("output/emails.json", "w") as f:
        json.dump({"domain": domain, "generated_emails": results}, f, indent=2)

    print(f"\n[+] Generated {len(results)} email patterns")
    print(f"[+] Saved to output/emails.json")


if __name__ == "__main__":
    main()