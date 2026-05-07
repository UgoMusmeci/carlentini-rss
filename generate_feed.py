import requests
from bs4 import BeautifulSoup
from datetime import datetime, UTC
import os

URL = "https://www.comune.carlentini.sr.it/novita/"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

print("Scarico pagina...")

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

print("Pagina scaricata")

soup = BeautifulSoup(response.text, "html.parser")

links = soup.find_all("a", href=True)

usati = set()
items = []

for link in links:
    href = link["href"]
    titolo = link.get_text(strip=True)

    if not titolo:
        continue

    if href in usati:
        continue

    if "/novita/" not in href:
        continue

    if len(titolo) < 10:
        continue

    usati.add(href)

    items.append({
        "title": titolo,
        "link": href,
        "description": titolo
    })

    if len(items) >= 15:
        break

rss_items = ""

for item in items:
    rss_items += f"""
    <item>
        <title><![CDATA[{item['title']}]]></title>
        <link>{item['link']}</link>
        <description><![CDATA[{item['description']}]]></description>
    </item>
    """

rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>Comune di Carlentini - Novità</title>
    <link>{URL}</link>
    <description>Feed RSS automatico</description>
    <lastBuildDate>{datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}</lastBuildDate>

    {rss_items}

</channel>
</rss>
"""

output_file = os.path.abspath("feed.xml")

with open(output_file, "w", encoding="utf-8") as f:
    f.write(rss_content)

print(f"Feed creato con {len(items)} elementi")
print(f"Feed salvato in: {output_file}")