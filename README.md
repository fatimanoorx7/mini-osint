# Mini OSINT Reconnaissance Tool

A lightweight Python tool that automates the passive reconnaissance phase of a
security assessment — subdomain enumeration, email pattern generation, and
breach-exposure checking — and combines the results into a single interactive
HTML dashboard with a risk-based exposure score.

**For authorized security assessments and educational use only.** All data
sources used are public (certificate transparency logs, DNS, public breach
databases). This tool performs passive lookups only — it does not scan,
exploit, or interact with any target system.

## What it does

1. **Subdomain enumeration** — queries crt.sh (certificate transparency
   logs), with automatic fallback to HackerTarget's API if crt.sh is
   unavailable. Checks which discovered subdomains currently resolve via DNS.
2. **Interesting-subdomain flagging** — automatically flags subdomains
   containing high-value keywords (`admin`, `dev`, `staging`, `test`, `vpn`,
   `api`, `backup`, etc.) and surfaces them first — a real technique used in
   reconnaissance workflows.
3. **Email pattern generation** — given a list of names, generates common
   corporate email address patterns (e.g. `first.last@domain.com`).
4. **Breach exposure check** — checks generated emails against breach
   databases, built against the HaveIBeenPwned API format.
5. **Combined report** — merges all findings into one JSON report with a
   project-defined exposure score.
6. **HTML dashboard** — renders the combined report as a readable,
   interactive dashboard.

## Pipeline

'''
subdomain_finder.py -> email_generator.py -> breach_check.py -> report.py -> generate_html.py
'''

Run the whole thing with one command via `run_all.py`, or run each stage
individually.

## Setup

```bash
git clone https://github.com/fatimanoorx7/mini-osint.git
cd mini-osint
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

## Usage

Add target names to `names.txt` (one name per line — see note below), then:

```bash
python run_all.py <domain> names.txt
```

Example:
```bash
python run_all.py example.com names.txt
```

Open `output/dashboard.html` in your browser to view the report.

### Running individual stages

```bash
python subdomain_finder.py <domain>
python email_generator.py <domain> names.txt
python breach_check.py
python report.py
python generate_html.py
```

## Note on names.txt

The names included are **fictional placeholder data** for demonstration.
Real OSINT engagements gather employee names manually from public sources
(company website, press releases, LinkedIn) — this tool intentionally does
not automate name harvesting, since scraping platforms like LinkedIn
violates their Terms of Service. Only use real names for domains you own or
are explicitly authorized to assess.

## Breach checking: demo mode vs. live mode

HaveIBeenPwned's email-check API requires a paid API key (an anti-abuse
measure HIBP introduced). To keep this project runnable by anyone without a
subscription, breach_check.py runs in **demo mode** by default, using a
small set of realistic sample breach data so the full pipeline can be
demonstrated end-to-end.

To run **live** checks against the real HIBP API:
```bash
set HIBP_API_KEY=your_key_here        # Windows
# export HIBP_API_KEY=your_key_here     # macOS/Linux
python breach_check.py
```
The script automatically switches to live mode when the key is present,
including rate-limit handling.

## Exposure score

A simple, project-defined scoring formula (not a standardized industry
metric) used to rank overall exposure for triage purposes:

- Each resolving subdomain: +1 point
- Each non-resolving subdomain: +0.2 points
- Each breached email: +10 points

## Limitations

- Email patterns are generated, not confirmed — they are guesses based on
  common corporate naming conventions, not verified addresses.
- Subdomain discovery depends on public certificate logs and DNS; it does
  not guarantee a complete list of an organization's infrastructure.
- Breach data (in demo mode) is sample data for demonstration purposes only.
- This tool performs passive reconnaissance only — it does not test for
  vulnerabilities or attempt any exploitation.

## Tech stack

Python, Requests, crt.sh API, HackerTarget API, HaveIBeenPwned API format
