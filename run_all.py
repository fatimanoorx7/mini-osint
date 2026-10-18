#!/usr/bin/env python3
"""
run_all.py
Runs the full mini-OSINT pipeline in order:
  1. subdomain_finder.py
  2. email_generator.py
  3. breach_check.py
  4. report.py
  5. generate_html.py
"""

import subprocess
import sys


def run_step(description, command):
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}\n")

    result = subprocess.run(command, shell=False)
    if result.returncode != 0:
        print(f"\n[!] Step failed: {description}")
        sys.exit(1)


def main():
    if len(sys.argv) < 3:
        print("Usage: python run_all.py <domain> <names_file>")
        print("Example: python run_all.py google.com names.txt")
        sys.exit(1)

    domain = sys.argv[1]
    names_file = sys.argv[2]

    run_step("Step 1/5: Subdomain Enumeration", ["python", "subdomain_finder.py", domain])
    run_step("Step 2/5: Email Pattern Generation", ["python", "email_generator.py", domain, names_file])
    run_step("Step 3/5: Breach Check", ["python", "breach_check.py"])
    run_step("Step 4/5: Combined Report", ["python", "report.py"])
    run_step("Step 5/5: HTML Dashboard", ["python", "generate_html.py"])

    print(f"\n{'='*60}")
    print("  DONE — full OSINT pipeline complete")
    print(f"{'='*60}")
    print("\n[+] Open output/dashboard.html in your browser to view the report.")


if __name__ == "__main__":
    main()