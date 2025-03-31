# Parsing-Links-from-PhishTank

## Task
The goal was to scrape all links from the PhishTank website, determine which ones are phishing links, and save the data in CSV format. Additionally, it was necessary to bypass Cloudflare protection without using Selenium.

## Implementation
- Used the `cloudscraper` library to bypass Cloudflare protection.
- Configured automatic parsing of all website pages with pagination handling.
- Added link verification for phishing indicators (tags on the site).
- Saved data in a CSV file with `url` and `isPhishing` columns.

## Result
- Successfully implemented a fully automated scraping process.
- Stored the results in `phishing_links.csv`.

## Challenges
- Faced difficulties with site authentication, but successfully bypassed this restriction.
- Fixed errors related to page transitions.

