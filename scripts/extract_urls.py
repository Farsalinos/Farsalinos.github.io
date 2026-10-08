#!/usr/bin/env python3
"""
Extract all URLs from sitemap for bulk submission.
Outputs one URL per line.
"""
import requests
import xml.etree.ElementTree as ET

SITEMAP_INDEX = "https://farsalinos.github.io/sitemap.xml"

def main():
    resp = requests.get(SITEMAP_INDEX, timeout=30)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    
    sitemap_urls = [elem.text for elem in root.findall(".//sm:sitemap/sm:loc", ns)]
    
    all_urls = []
    for sm_url in sitemap_urls:
        resp = requests.get(sm_url, timeout=30)
        resp.raise_for_status()
        sm_root = ET.fromstring(resp.content)
        urls = [elem.text for elem in sm_root.findall(".//sm:url/sm:loc", ns)]
        all_urls.extend(urls)
    
    for url in sorted(all_urls):
        print(url)

if __name__ == "__main__":
    main()