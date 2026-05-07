import requests
from bs4 import BeautifulSoup
from datetime import datetime, UTC
import os
import re

URL = "https://www.comune.carlentini.sr.it/novita/"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

mesi = {
    "gennaio": 1,
    "febbraio": 2,
    "marzo": 3,
    "aprile": 4,
    "maggio": 5,
    "giugno": 6,
    "luglio": 7,
    "agosto": 8,
    "settembre": 9,
    "ottobre": 10,
    "novembre": 11,
    "dicembre": 12
}

print("Scarico pagina novità...")

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

    print(f"Leggo articolo: {titolo}")

    try:

        articolo = requests.get(
            href,
            headers=headers,
            timeout=30
        )

        articolo.raise_for_status()

        articolo_soup = BeautifulSoup(
            articolo.text,
            "html.parser"
        )

        testo_pagina = articolo_soup.get_text(
            " ",
            strip=True
        )

        # DEBUG
        print(testo_pagina[:500])

        # Cerca date tipo:
        # Data: 10 Marzo 2025

        match = re.search(
            r"Data:\s*(\d{1,2})\s+([A-Za-zàèéìòù]+)\s+(\d{4})",
            testo_pagina,
            re.IGNORECASE
        )

        pub_date = datetime.now(UTC)

        if match:

            giorno = int(match.group(1))
            mese_nome = match.group(2).lower()
            anno = int(match.group(3))

            mese = mesi.get(mese_nome)

            if mese:

                pub_date = datetime(
                    anno,
                    mese,
                    giorno,
                    tzinfo=UTC
                )

                print(
                    f"DATA TROVATA: "
                    f"{giorno}/{mese}/{anno}"
                )

        else:

            print("NESSUNA DATA TROVATA")

        paragrafi = articolo_soup.find_all("p")

        descrizione = titolo

        for p in paragrafi:

            testo = p.get_text(strip=True)

            if len(testo) > 80:

                descrizione = testo[:300]
                break

        items.append({
            "title": titolo,
            "link": href,
            "description": descrizione,
            "pubDate": pub_date
        })

    except Exception as e:

        print(f"ERRORE ARTICOLO: {e}")

    if len(items) >= 15:
        break

items.sort(
    key=lambda x: x["pubDate"],
    reverse=True
)

rss_items = ""

for item in items:

    pub_date_str = item["pubDate"].strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )

    rss_items += f"""
    <item>
        <title><![CDATA[{item['title']}]]></title>
        <link>{item['link']}</link>
        <description><![CDATA[{item['description']}]]></description>
        <pubDate>{pub_date_str}</pubDate>
        <guid>{item['link']}</guid>
    </item>
    """

rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>Comune di Carlentini - Novità</title>
    <link>{URL}</link>
    <description>Feed RSS automatico</description>
    <lastBuildDate>{datetime.now(UTC).strftime('%a, %d %b %Y %H:%M:%S GMT')}</lastBuildDate>

    {rss_items}

</channel>
</rss>
"""

output_file = os.path.abspath("feed.xml")

with open(output_file, "w", encoding="utf-8") as f:
    f.write(rss_content)

print(f"Feed creato con {len(items)} elementi")
print(f"Feed salvato in: {output_file}")