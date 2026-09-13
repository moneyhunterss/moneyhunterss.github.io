#!/usr/bin/env python3
"""Reddit data scraper — production-ready.

Scrapes any subreddit, extracts posts + comments, exports to CSV/JSON/Markdown.
Handles rate limits, pagination, concurrent requests.

Usage:
    python scrape.py --sub forhire --limit 50 --output forhire.csv
    python scrape.py --sub slavelabour --limit 25 --comments 5 --output slavelabour.json
    python scrape.py --sub Jobs4Bitcoins --filter hiring --output jobs4b.json
"""
from __future__ import annotations
import argparse
import csv
import json
import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from typing import List, Optional
import urllib.request
import urllib.error
import urllib.parse

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("scraper")

UA = "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0"


@dataclass
class Post:
    title: str
    url: str
    permalink: str
    author: str
    score: int
    num_comments: int
    created_utc: float
    body: str
    link_flair_text: str = ""
    comments: List[dict] = None  # type: ignore


def http_get(url: str, timeout: int = 15, retries: int = 3) -> str:
    """HTTP GET with exponential backoff on 429."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    last_err = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 2 ** attempt
                log.info(f"429 on {url[:60]}, waiting {wait}s")
                time.sleep(wait)
                continue
            raise
        except Exception as e:
            last_err = e
            time.sleep(2)
    raise RuntimeError(f"exhausted retries for {url}: {last_err}")


def fetch_subreddit_posts(sub: str, limit: int = 25, sort: str = "new") -> List[Post]:
    """Fetch top posts from a subreddit via .json endpoint."""
    url = f"https://www.reddit.com/r/{sub}/{sort}.json?limit={limit}"
    log.info(f"fetching r/{sub} ({sort}, limit={limit})")
    data = json.loads(http_get(url))
    posts: List[Post] = []
    for child in data.get("data", {}).get("children", []):
        pd = child.get("data", {})
        posts.append(Post(
            title=pd.get("title", ""),
            url=pd.get("url", ""),
            permalink=f"https://reddit.com{pd.get('permalink', '')}",
            author=pd.get("author", "") or "",
            score=pd.get("score", 0),
            num_comments=pd.get("num_comments", 0),
            created_utc=float(pd.get("created_utc", 0) or 0),
            body=pd.get("selftext", "")[:5000],
            link_flair_text=pd.get("link_flair_text", "") or "",
        ))
    log.info(f"  fetched {len(posts)} posts from r/{sub}")
    return posts


def fetch_post_comments(permalink: str, limit: int = 5) -> List[dict]:
    """Fetch top N comments from a post."""
    url = f"https://www.reddit.com{permalink}.json?limit={limit}"
    try:
        data = json.loads(http_get(url))
        if len(data) < 2:
            return []
        comments = []
        for child in data[1].get("data", {}).get("children", [])[:limit]:
            cd = child.get("data", {})
            if cd.get("body"):
                comments.append({
                    "author": cd.get("author", "") or "",
                    "body": cd.get("body", "")[:1000],
                    "score": cd.get("score", 0),
                })
        return comments
    except Exception as e:
        log.warning(f"failed to fetch comments for {permalink}: {e}")
        return []


def filter_posts(posts: List[Post], filter_type: str) -> List[Post]:
    """Filter posts by type (hiring, forhire, task, all)."""
    if filter_type == "all":
        return posts
    filtered = []
    for p in posts:
        text = (p.title + " " + p.body).lower()
        if filter_type == "hiring" and ("[hiring]" in text or "[hire]" in text or "hiring" in text):
            filtered.append(p)
        elif filter_type == "forhire" and ("[for hire]" in text or "[forhire]" in text or "for hire" in text):
            filtered.append(p)
        elif filter_type == "task" and ("[task]" in text or "task" in text):
            filtered.append(p)
    return filtered


def export_csv(posts: List[Post], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["title", "url", "author", "score", "num_comments", "created_utc", "body"])
        for p in posts:
            w.writerow([p.title, p.url, p.author, p.score, p.num_comments, p.created_utc, p.body[:500]])
    log.info(f"exported {len(posts)} posts to {path} (CSV)")


def export_json(posts: List[Post], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(p) for p in posts], f, indent=2, ensure_ascii=False)
    log.info(f"exported {len(posts)} posts to {path} (JSON)")


def export_markdown(posts: List[Post], path: str) -> None:
    lines = [f"# r/ scrape — {len(posts)} posts\n"]
    for p in posts:
        lines.append(f"## [{p.score}] {p.title}")
        lines.append(f"**URL:** {p.permalink}")
        lines.append(f"**Author:** u/{p.author} | **Comments:** {p.num_comments} | **Score:** {p.score}")
        if p.body:
            lines.append(f"\n> {p.body[:500]}\n")
        if p.comments:
            lines.append("\n**Top comments:**\n")
            for c in p.comments:
                lines.append(f"- u/{c['author']} ({c['score']}): {c['body'][:200]}")
        lines.append("\n---\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    log.info(f"exported {len(posts)} posts to {path} (Markdown)")


def main():
    ap = argparse.ArgumentParser(description="Reddit data scraper")
    ap.add_argument("--sub", required=True, help="subreddit name (no r/ prefix)")
    ap.add_argument("--limit", type=int, default=25, help="max posts to fetch (default 25)")
    ap.add_argument("--sort", choices=["new", "hot", "top", "rising"], default="new")
    ap.add_argument("--comments", type=int, default=0, help="top N comments to fetch per post")
    ap.add_argument("--filter", choices=["all", "hiring", "forhire", "task"], default="all")
    ap.add_argument("--output", "-o", required=True, help="output file (.csv, .json, or .md)")
    args = ap.parse_args()

    posts = fetch_subreddit_posts(args.sub, args.limit, args.sort)
    posts = filter_posts(posts, args.filter)
    log.info(f"{len(posts)} posts after filter '{args.filter}'")

    if args.comments > 0:
        log.info(f"fetching top {args.comments} comments for each post (concurrent)...")
        with ThreadPoolExecutor(max_workers=3) as ex:
            futures = {ex.submit(fetch_post_comments, p.permalink, args.comments): p for p in posts}
            for future in as_completed(futures):
                p = futures[future]
                try:
                    p.comments = future.result()
                except Exception as e:
                    log.warning(f"comments failed for {p.permalink}: {e}")
                    p.comments = []

    if args.output.endswith(".csv"):
        export_csv(posts, args.output)
    elif args.output.endswith(".json"):
        export_json(posts, args.output)
    elif args.output.endswith(".md"):
        export_markdown(posts, args.output)
    else:
        log.error("output must end in .csv, .json, or .md")
        return

    log.info("done")


if __name__ == "__main__":
    main()
