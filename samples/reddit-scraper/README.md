# Web Scraper Framework

Production-ready concurrent scraper. Scrapes any paginated web endpoint,
extracts structured data, exports to CSV/JSON/Markdown. Built for any site,
not just one.

## Features

- Concurrent scraping (3 workers by default, configurable)
- Rate-limit handling with exponential backoff
- Pagination support (cursor, offset, or page-number based)
- Export to CSV, JSON, or Markdown
- Comment / sub-page extraction
- Filter by post type (hiring, for-hire, task, all)

## Quick start

```bash
pip install -r requirements.txt

# Scrape a paginated API endpoint, top 50 results
python scrape.py --url "https://api.example.com/posts" --limit 50 --output results.csv

# Scrape + extract child pages (top 5 each)
python scrape.py --url "https://example.com/list" --children 5 --output results.json

# Filter by content type
python scrape.py --url "https://example.com/list" --filter hiring --output hiring.json
```

## Use cases

- Market research (find common patterns across 100s of listings)
- Lead generation (scrape job postings, contact via email/DM)
- Content analysis (find trending topics, sentiment)
- Competitor research (price monitoring, feature comparison)
- News aggregation (collect headlines from N sources)
- Academic research (collect papers, citation networks)

## Output format

### CSV
```
title,url,author,score,num_comments,created_utc,body
"Shopify UX Designer role","https://example.com/post/123","user",45,12,1700000000,"Looking for..."
```

### JSON
```json
[
  {
    "title": "Shopify UX Designer role",
    "url": "https://example.com/post/123",
    "author": "user",
    "score": 45,
    "num_comments": 12,
    "created_utc": 1700000000,
    "body": "Looking for...",
    "children": [
      {"author": "user2", "body": "I can do this...", "score": 5}
    ]
  }
]
```

## Tech

- Python 3.10+
- `concurrent.futures` — parallel workers
- `urllib.request` — HTTP (no external deps)
- Standard library only otherwise

## Production-ready upgrades

For real production use, I'd add:
- Proxy rotation (residential proxies for anti-bot evasion)
- Headless browser fallback (Selenium/Playwright for JS-rendered sites)
- Database sink (Postgres, S3, BigQuery)
- Scheduling (cron, GitHub Actions, Airflow)
- Monitoring (alert on 0 results / high error rate)
- Anti-detection (random User-Agents, request jitter)

## License

MIT — use for any legal scraping (respect robots.txt + ToS).
