#!/usr/bin/env python3
"""
Submit all URLs from sitemap to Bing via IndexNow + URL Submission API.
Run once for bulk, then GitHub Actions handles new URLs on each deploy.
"""
import requests
import xml.etree.ElementTree as ET
import time
import os

# ===== CONFIG =====
SITEMAP_INDEX = "https://farsalinos.github.io/sitemap.xml"
INDEXNOW_KEY = os.environ.get("INDEXNOW_KEY")  # Set in GitHub Actions secrets
BING_API_KEY = os.environ.get("BING_API_KEY")  # Set in GitHub Actions secrets
# ===================

def fetch_all_urls():
    """Fetch all URLs from sitemap index + language sitemaps."""
    urls = []
    
    # Get sitemap index
    resp = requests.get(SITEMAP_INDEX, timeout=30)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    
    sitemap_urls = [elem.text for elem in root.findall(".//sm:sitemap/sm:loc", ns)]
    
    for sm_url in sitemap_urls:
        resp = requests.get(sm_url, timeout=30)
        resp.raise_for_status()
        sm_root = ET.fromstring(resp.content)
        urls.extend([elem.text for elem in sm_root.findall(".//sm:url/sm:loc", ns)])
    
    return urls

def submit_indexnow(urls, key):
    """Submit via IndexNow protocol."""
    if not key:
        print("⚠️ INDEXNOW_KEY not set, skipping IndexNow")
        return
    
    payload = {
        "host": "farsalinos.github.io",
        "key": key,
        "urlList": urls
    }
    
    # IndexNow accepts max 10,000 URLs per request
    for i in range(0, len(urls), 10000):
        batch = urls[i:i+10000]
        payload["urlList"] = batch
        resp = requests.post("https://api.indexnow.org/indexnow", json=payload, timeout=30)
        if resp.status_code == 200:
            print(f"✅ IndexNow: Submitted {len(batch)} URLs")
        else:
            print(f"❌ IndexNow failed: {resp.status_code} {resp.text}")
        time.sleep(1)  # Rate limit

def submit_bing_api(urls, api_key):
    """Submit via Bing URL Submission API."""
    if not api_key:
        print("⚠️ BING_API_KEY not set, skipping Bing API")
        return
    
    headers = {"Content-Type": "application/json"}
    endpoint = f"https://ssl.bing.com/webmaster/api.svc/json/SubmitUrlbatch?apikey={api_key}"
    
    # Bing API accepts max 10,000 URLs per day
    for i in range(0, min(len(urls), 10000), 1000):
        batch = urls[i:i+1000]
        payload = {"siteUrl": "https://farsalinos.github.io/", "urlList": batch}
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        if resp.status_code == 200:
            print(f"✅ Bing API: Submitted {len(batch)} URLs")
        else:
            print(f"❌ Bing API failed: {resp.status_code} {resp.text}")
        time.sleep(0.5)

if __name__ == "__main__":
    print("Fetching all URLs from sitemap...")
    urls = fetch_all_urls()
    print(f"Found {len(urls)} URLs")
    
    print("\nSubmitting to IndexNow...")
    submit_indexnow(urls, INDEXNOW_KEY)
    
    print("\nSubmitting to Bing URL Submission API...")
    submit_bing_api(urls, BING_API_KEY)
    
    print("\nDone!")