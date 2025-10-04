from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
from readability import Document


def search(query: str, max_results: int = 5):
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
    return [{"title": r.get("title"), "href": r.get("href"), "snippet": r.get("body")} for r in results]


def fetch_clean(url: str, max_chars: int = 4000):
    html = requests.get(url, timeout=15).text
    doc = Document(html)
    txt = BeautifulSoup(doc.summary(), "lxml").get_text(" ")
    return txt[:max_chars]
