#!/usr/bin/env python3
"""Scrape Evan's Past Writings index and create Markdown files.

Usage:
    source venv/bin/activate
    python scripts/scrape.py
"""

import re
import os
import sys
import time
import json
import urllib.parse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

INDEX_URL = "https://paragraph.com/@evandekim/past-writings"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
WRITINGS_DIR = Path(__file__).resolve().parent.parent / "src" / "writings"
OUTPUT_DIR = WRITINGS_DIR
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Paragraph editor links do not expose the public slug; map known editor URLs to public URLs.
EDITOR_URL_MAP = {
    "https://paragraph.com/editor/31o6StqKYWR7B5fGsWYv": "https://paragraph.com/@evandekim/on-chain-atomic-gaussian-math",
    "https://paragraph.com/editor/IZ7hruMsuonAs8DFhJXt": "https://paragraph.com/@evandekim/building-an-agentic-native-mcp-for-data-science",
}


def fetch(url, retries=2):
    headers = {"User-Agent": USER_AGENT}
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            if attempt == retries:
                print(f"  fetch failed after {retries+1} attempts: {e}")
                return None
            time.sleep(1)


def parse_date(text):
    """Parse strings like '(December 2025)', '(blog, November 2022)', or '(Mathematica, April 2021)' into a date."""
    # Try a plain month-year pattern first
    m = re.search(r"\(([A-Za-z]+\s+\d{4})\)", text)
    if m:
        try:
            return datetime.strptime(m.group(1), "%B %Y").date().isoformat()
        except ValueError:
            pass
    # Try patterns with a qualifier before the date: '(qualifier, Month Year)'
    m = re.search(r"\([^,]+,\s+([A-Za-z]+\s+\d{4})\)", text)
    if m:
        try:
            return datetime.strptime(m.group(1), "%B %Y").date().isoformat()
        except ValueError:
            return None
    return None


def slugify(title):
    s = re.sub(r"[^\w\s-]", "", title.lower())
    s = re.sub(r"[-\s]+", "-", s).strip("-")
    return s


def extract_platform(url):
    host = urllib.parse.urlparse(url).netloc.lower()
    if "paragraph" in host:
        return "paragraph"
    if "mirror" in host:
        return "mirror"
    if "ethresear.ch" in host:
        return "ethresear.ch"
    if "github" in host:
        return "github"
    if "frontier" in host:
        return "frontier.tech"
    if "primitive" in host:
        return "primitive.mirror"
    return "external"


def parse_index(html):
    soup = BeautifulSoup(html, "html.parser")

    # Find the rich-text container that holds headings and lists
    container = soup.find("div", class_="ProseMirror")
    if container:
        container = container.find("div", class_="webrender") or container

    if not container:
        # Fallback: find any container that has h2 + ul
        for div in soup.find_all("div"):
            if div.find_all("h2") and div.find_all("ul"):
                container = div
                break

    collections = defaultdict(list)
    seen_urls = set()
    current_heading = "uncategorized"

    for child in container.children:
        if not child.name:
            continue

        # Heading detection: either a direct h2 or a div containing an h2
        heading_text = None
        if child.name == "h2":
            heading_text = child.get_text(strip=True).lower()
        elif child.name == "div":
            h2 = child.find("h2", recursive=False)
            if h2:
                heading_text = h2.get_text(strip=True).lower()

        if heading_text and heading_text in {"collected works", "latest", "highlights", "data", "mev", "defi", "math"}:
            current_heading = heading_text
            continue

        if child.name in ("ul", "ol"):
            for li in child.find_all("li"):
                a = li.find("a")
                if not a or not a.get("href"):
                    continue
                text = li.get_text(" ", strip=True)
                date = parse_date(text)
                date_text = ""
                if date:
                    m = re.search(r"\(([A-Za-z]+\s+\d{4})\)", text)
                    date_text = m.group(1) if m else ""
                # Split the trailing parenthetical into qualifier and date if possible
                raw_title = re.sub(r"\s*\([^)]*\d{4}[^)]*\)\s*$", "", text).strip()
                qualifier_match = re.search(r"\(([^,]+),\s+[A-Za-z]+\s+\d{4}\)\s*$", text)
                qualifier = qualifier_match.group(1).strip() if qualifier_match else ""
                title = raw_title
                if qualifier and qualifier.lower() not in {"blog", "paper"}:
                    title = f"{raw_title} ({qualifier})"
                elif qualifier:
                    title = f"{raw_title} ({qualifier})"
                url = urllib.parse.unquote(a.get("href").strip())
                url = EDITOR_URL_MAP.get(url, url)

                if url in seen_urls:
                    continue
                seen_urls.add(url)

                collections[current_heading].append({
                    "title": title,
                    "url": url,
                    "date_text": date_text,
                    "date": date,
                })

    return [(name, items) for name, items in collections.items() if items]


def extract_body_paragraph(html):
    soup = BeautifulSoup(html, "html.parser")
    # Try to find the main article container
    article = soup.find("article") or soup.find("main") or soup.find("div", class_=re.compile("article|post|content"))
    if article:
        return md(str(article), heading_style="ATX")
    # Fallback to body text
    body = soup.find("body")
    if body:
        return md(str(body), heading_style="ATX")
    return ""


def extract_body_ethresearch(html):
    soup = BeautifulSoup(html, "html.parser")
    # Discourse topic body
    post = soup.find("div", class_=re.compile("post|topic-post"))
    if post:
        return md(str(post), heading_style="ATX")
    return ""


def extract_body_frontier(html):
    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("article") or soup.find("main")
    if article:
        return md(str(article), heading_style="ATX")
    return ""


def extract_body_mirror(html):
    soup = BeautifulSoup(html, "html.parser")
    # Mirror has a rich text article
    article = soup.find("article")
    if article:
        return md(str(article), heading_style="ATX")
    # Try to find the main published content
    for sel in ["main", '[class*="article"]', '[class*="post"]', "div#__next"]:
        el = soup.select_one(sel)
        if el:
            return md(str(el), heading_style="ATX")
    return ""


def fetch_body(url, platform):
    print(f"  fetching body from {platform}...")
    html = fetch(url)
    if not html:
        return None
    if platform == "paragraph":
        return extract_body_paragraph(html)
    if platform == "mirror":
        return extract_body_mirror(html)
    if platform == "ethresear.ch":
        return extract_body_ethresearch(html)
    if platform == "frontier.tech":
        return extract_body_frontier(html)
    return ""


def save_writing(item, collection, body=None, slug=None):
    title = item["title"]
    url = item["url"]
    date = item["date"]
    platform = extract_platform(url)
    slug = slug or slugify(title)
    path = OUTPUT_DIR / f"{slug}.md"

    tags = ["writing"]
    if collection:
        tags.append(collection)
    if platform:
        tags.append(platform)

    frontmatter = {
        "title": title,
        "date": date or "",
        "collection": collection or "uncategorized",
        "tags": tags,
        "source_url": url,
        "source_platform": platform,
        "slug": slug,
    }

    if body:
        body = re.sub(r"\n{3,}", "\n\n", body).strip()
        if body:
            body_text = f"\n\n{body}\n"
        else:
            body_text = "\n\n"
    else:
        body_text = f"\n\nRead the original on [{platform}]({url}).\n"

    fm_lines = ["---"]
    for key, value in frontmatter.items():
        if key == "title":
            # Quote the title to avoid YAML parsing issues with colons or special chars
            fm_lines.append(f'{key}: "{value.replace(chr(34), chr(92) + chr(34))}"')
        elif key == "date":
            # Quote the date so it stays a string and avoids UTC timezone shift
            fm_lines.append(f'{key}: "{value}"')
        elif isinstance(value, list):
            fm_lines.append(f"{key}:")
            for v in value:
                fm_lines.append(f"  - {v}")
        else:
            fm_lines.append(f"{key}: {value}")
    fm_lines.append("---")

    content = "\n".join(fm_lines) + body_text
    path.write_text(content, encoding="utf-8")
    print(f"  saved {path}")


def main():
    print(f"Fetching {INDEX_URL}...")
    html = fetch(INDEX_URL)
    if not html:
        print("Failed to fetch index.")
        sys.exit(1)

    collections = parse_index(html)
    print(f"Found {len(collections)} collections")

    stats = defaultdict(int)
    seen_slugs = set()
    for collection, items in collections:
        print(f"Collection: {collection} ({len(items)} items)")
        for item in items:
            print(f"  - {item['title']} ({item['date']})")
            platform = extract_platform(item["url"])
            stats[platform] += 1

            base_slug = slugify(item["title"])
            slug = base_slug
            counter = 1
            while slug in seen_slugs:
                counter += 1
                slug = f"{base_slug}-{counter}"
            seen_slugs.add(slug)

            body = None
            if platform in {"paragraph", "mirror", "ethresear.ch", "frontier.tech"}:
                body = fetch_body(item["url"], platform)

            save_writing(item, collection, body, slug=slug)

    print("\nStats:")
    print(json.dumps(dict(stats), indent=2))
    print(f"\nDone. Files written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
