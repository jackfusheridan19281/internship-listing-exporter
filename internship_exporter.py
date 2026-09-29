#
# ABOUT THIS TOOL
#
# NON-TECHNICAL EXPLANATION
#
# Intern List is useful for finding internships, but its listings are
# dynamically loaded as you scroll. This makes it difficult to grab the
# entire list at once for external analysis. For example, using Ctrl+A
# and copying the page only captures the listings currently loaded in
# the browser.
#
# This tool solves that problem by retrieving the full set of internship
# listings and exporting them to a CSV. Choose a job category and,
# optionally, a location, then run the script to create a structured
# file that can easily be searched, filtered, uploaded to ChatGPT, or
# analyzed with other tools.
#
# TECHNICAL EXPLANATION
#
# Rather than scraping rendered HTML from the DOM, this script retrieves
# structured job data from the underlying listing endpoint used by Intern List.
#
# It sends POST requests containing the selected category and optional
# location filter, then paginates through the results in batches of 50
# until no additional listings are returned.
#
# Each response contains structured JSON. The script extracts fields
# including job ID, title, company, location, salary, work model,
# industry, company size, and posting time. Results from every batch are
# combined and exported to a single CSV file.
#
# In short:
#
# Intern List -> Listing Endpoint -> JSON -> Pagination -> Field Extraction -> CSV
#
# Browse the internship listings here:
# https://www.intern-list.com/
#
# Use the settings below to choose which listings to export.

import csv
import requests
from pathlib import Path

# INTERNSHIP LIST

# SEARCH SETTINGS — EDIT THESE

# 1. Choose an internship category you want to export.
#
# Available categories:
#   accounting_finance        - Accounting and Finance
#   arts_entertainment        - Arts and Entertainment
#   business_analyst          - Business Analyst
#   consulting                - Consulting
#   creatives_design          - Creatives and Design
#   customer_service          - Customer Service and Support
#   cyber_security            - Cybersecurity
#   data_analysis             - Data Analysis
#   education_training        - Education and Training
#   engineering_development   - Engineering and Development
#   healthcare                - Healthcare
#   human_resources           - Human Resources
#   legal_compliance          - Legal and Compliance
#   management_executive      - Management and Executive
#   marketing_gen             - Marketing
#   ml_ai                     - Machine Learning and AI
#   product_management        - Product Management
#   public_sector             - Public Sector and Government
#   sales                     - Sales
#   swe                       - Software Engineering
#   supply_chain              - Supply Chain

CATEGORY = "data_analysis"

# 2. Optional location filter.
# Leave [] empty to return all locations.
# Example: [", CT"] for Connecticut.

LOCATION = []

# 3. Name of the CSV file to create.
# Exported files will be saved in the "Exported Internships" folder.

OUTPUT_FOLDER = Path("Exported Internships")
OUTPUT_FILE = "internships.csv"

# SCRAPER

URL = "https://jobright.ai/swan/mini-sites/list"
COUNT = 50

headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json",
    "Origin": "https://jobright.ai",
    "Referer": f"https://jobright.ai/minisites-jobs/intern/us/{CATEGORY}?embed=true",
    "Accept": "application/json, text/plain, */*",
    "x-client-type": "web"
}

position = 0
all_jobs = []

# Jobright returns listings in batches.
# Keep requesting batches until no additional jobs are returned.
while True:

    params = {
        "position": position,
        "count": COUNT
    }

    payload = {
        "category": f"intern:us:{CATEGORY}",
        "location": LOCATION
    }

    response = requests.post(
        URL,
        headers=headers,
        params=params,
        json=payload,
        timeout=30
    )

    # Stop if the request fails.
    if response.status_code != 200:
        print("Request failed:", response.status_code)
        print(response.text)
        break

    data = response.json()
    jobs = data["result"]["jobList"]

    # An empty batch means there are no more listings.
    if not jobs:
        break

    # Pull the useful fields from each job listing.
    for job in jobs:

        properties = job["properties"]

        all_jobs.append({
            "jobId": job["jobId"],
            "title": properties.get("title"),
            "company": properties.get("company"),
            "location": properties.get("location"),
            "salary": properties.get("salary"),
            "workModel": properties.get("workModel"),
            "industry": ", ".join(properties.get("industry", [])),
            "companySize": properties.get("companySize"),
            "hireTime": properties.get("hireTime")
        })

    # Move to the next batch.
    position += COUNT

# EXPORT RESULTS

print(f"Downloaded {len(all_jobs)} jobs.")

if all_jobs:

    # Create the output folder if it does not already exist.
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_FOLDER / OUTPUT_FILE

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=all_jobs[0].keys()
        )

        writer.writeheader()
        writer.writerows(all_jobs)

    print(f"Saved to {output_path}")

else:
    print("No jobs returned.")
