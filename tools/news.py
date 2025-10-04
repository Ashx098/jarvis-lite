import os, time, json
from urllib.parse import urlencode
import requests, httpx
from tenacity import retry, stop_after_attempt, wait_fixed
from bs4 import BeautifulSoup
from readability import Document
from ddgs import DDGS

DEFAULT_TIMEOUT = 15
MAX_ARTICLE_CHARS = 8000
MAX_OBS_CHARS = 4000

# Simple credibility scores (0..1). Adjust as you like.
TRUST = {
    "bbc.com": 0.95,
    "reuters.com": 0.95,
    "thehindu.com": 0.9,
    "indianexpress.com": 0.85,
    "ndtv.com": 0.85,
    "timesofindia.indiatimes.com": 0.8,
}

USE_NEWS_API = os.getenv("USE_NEWS_API", "false").lower() == "true"
NEWS_API_PROVIDER = os.getenv("NEWS_API_PROVIDER", "GNEWS").upper()
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
NEWS_COUNTRY = os.getenv("NEWS_COUNTRY", "in")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def _fetch(url: str) -> str:
    r = requests.get(url, timeout=DEFAULT_TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    return r.text

def _clean(html: str) -> str:
    doc = Document(html)
    txt = BeautifulSoup(doc.summary(), "lxml").get_text(" ")
    return txt[:MAX_ARTICLE_CHARS]

# -------- API paths --------

def _news_api_search(query: str, country: str = None, max_results: int = 8):
    if not NEWS_API_KEY:
        return []
    if NEWS_API_PROVIDER == "GNEWS":
        params = {
            "q": query,
            "lang": "en",
            "country": (country or NEWS_COUNTRY),
            "max": max_results,
            "apikey": NEWS_API_KEY,
        }
        url = f"https://gnews.io/api/v4/search?{urlencode(params)}"
        data = requests.get(url, timeout=DEFAULT_TIMEOUT).json()
        arts = data.get("articles", [])
        return [{"title": a.get("title"), "href": a.get("url"), "source": a.get("source", {}).get("name") or ""} for a in arts]
    elif NEWS_API_PROVIDER == "NEWSAPI":
        params = {
            "q": query,
            "language": "en",
            "pageSize": max_results,
            "apiKey": NEWS_API_KEY,
        }
        url = f"https://newsapi.org/v2/everything?{urlencode(params)}"
        data = requests.get(url, timeout=DEFAULT_TIMEOUT).json()
        arts = data.get("articles", [])
        return [{"title": a.get("title"), "href": a.get("url"), "source": (a.get("source") or {}).get("name") or ""} for a in arts]
    return []

# -------- Search paths (no API key) --------

def _ddg_news(query: str, max_results: int = 8):
    with DDGS() as ddgs:
        return list(ddgs.text(query + " site:reuters.com OR site:bbc.com OR site:ndtv.com OR site:thehindu.com OR site:indianexpress.com", max_results=max_results))


def search_news(query: str, max_results: int = 8):
    # Prefer API if available
    if USE_NEWS_API and NEWS_API_KEY:
        return _news_api_search(query, max_results=max_results)
    # Fallback to curated DDG search
    rows = _ddg_news(query, max_results)
    return [{"title": r.get("title"), "href": r.get("href"), "source": r.get("source") or ""} for r in rows]


def multi_fetch_and_merge(urls: list[str], top_k: int = 3):
    texts, used = [], []
    for u in urls[:top_k]:
        try:
            html = _fetch(u)
            txt = _clean(html)
            if len(txt) > 200:
                texts.append(txt)
                used.append(u)
        except Exception:
            continue
    merged = "\n\n".join(texts)[:MAX_ARTICLE_CHARS]
    return merged, used


def credibility(url: str) -> float:
    for k, score in TRUST.items():
        if k in url:
            return score
    return 0.5

# High-level function the agent can call

def news_bundle(query: str, llm_call, max_results: int = 8):
    """
    Returns dict with: items (title, url, source, weight), summary, citations
    llm_call: callable(messages:list[dict]) -> str
    """
    items = search_news(query, max_results)
    if not items:
        return {"items": [], "summary": "No news found.", "citations": []}

    # sort by credibility
    items = sorted(items, key=lambda x: credibility(x.get("href","")), reverse=True)
    urls = [i["href"] for i in items if i.get("href")]

    merged, used_urls = multi_fetch_and_merge(urls, top_k=3)

    if not merged:
        # fallback: summarize titles/snippets only
        bullets = "\n".join(f"- {i['title']} ({i.get('source','')})" for i in items[:6])
        msg = [
            {"role":"system", "content":"Write a crisp 6-bullet digest of today's news from the list. Each bullet ≤ 20 words."},
            {"role":"user", "content": bullets}
        ]
        summary = llm_call(msg)
        cites = [i["href"] for i in items[:6] if i.get("href")]
        # attach weights
        out_items = [{**i, "weight": credibility(i.get("href",""))} for i in items[:8]]
        return {"items": out_items, "summary": summary, "citations": cites}

    # hierarchical summarization
    chunks = [merged[i:i+2000] for i in range(0, len(merged), 2000)]
    partials = []
    for c in chunks:
        msg = [
            {"role":"system","content":"Summarize this news content into 3 sharp bullets with dates, names, and numbers."},
            {"role":"user","content": c}
        ]
        partials.append(llm_call(msg))
    msg = [
        {"role":"system","content":"Merge these partial news summaries into a single 6-bullet India-first digest, include sources if inferable."},
        {"role":"user","content": "\n".join(partials)}
    ]
    final = llm_call(msg)

    # annotate items with credibility
    out_items = [{**i, "weight": credibility(i.get("href",""))} for i in items[:8]]
    return {"items": out_items, "summary": final, "citations": used_urls}
