# Reddit Data Scraper

A production-ready Python script that scrapes any subreddit, extracts posts + comments,
and exports to CSV/JSON. Handles rate limits, pagination, and concurrent requests.

## Features

- Scrape any subreddit by name (e.g. `r/forhire`)
- Filter by post type (Hiring / For Hire / Task / All)
- Extract: title, URL, author, score, num_comments, body text, created date
- Optional: scrape top N comments per post
- Export to CSV, JSON, or Markdown
- Handles Reddit rate limits (429) with exponential backoff
- Concurrent requests (3 workers) for speed
- No Reddit account required — uses public RSS / .json endpoints

## Quick start

```bash
pip install -r requirements.txt

# Scrape r/forhire, top 50 posts, no comments
python scrape.py --sub forhire --limit 50 --output forhire.csv

# Scrape r/slavelabour, top 25 posts, top 5 comments each
python scrape.py --sub slavelabour --limit 25 --comments 5 --output slavelabour.json

# Filter only [Hiring] posts
python scrape.py --sub Jobs4Bitcoins --filter hiring --output jobs4b.json
```

## Use cases

- Market research (find what gigs are common in your niche)
- Lead generation (scrape hiring posts, contact via DM)
- Content analysis (find trending topics, sentiment)
- Competitor research (see what other freelancers offer)

## Output format

### CSV
```
title,url,author,score,num_comments,created_utc,body
"[Hiring] Shopify UX Designer","https://reddit.com/r/forhire/comments/...","user123",45,12,1700000000,"Looking for..."
```

### JSON
```json
[
  {
    "title": "[Hiring] Shopify UX Designer",
    "url": "https://reddit.com/r/forhire/comments/...",
    "author": "user123",
    "score": 45,
    "num_comments": 12,
    "created_utc": 1700000000,
    "body": "Looking for...",
    "comments": [
      {"author": "user456", "body": "I can do this...", "score": 5}
    ]
  }
]
```

## Tech stack

- Python 3.10+
- `requests` — HTTP
- `concurrent.futures` — async workers
- Standard library only otherwise

## Why this exists

I built this for a client who needed to monitor 50+ Reddit subs daily for paid gig posts.
The full production version includes LLM scoring, Telegram notifications, and a pipeline
tracker. This is the simplified open-source release.

## License

MIT — use it for anything, including commercial.
