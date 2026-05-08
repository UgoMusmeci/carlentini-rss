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

response = requests.get(
    URL,
    headers=headers,
    timeout=30
)

response.raise_for_status()

print("Pagina scaricata")

soup = BeautifulSoup(
    response.text,
    "html.parser"
)

links = soup.find_all("a", href=True)

items = []
usati = set()

# limiteremo ai primi 30 articoli validi
articoli_validi = []

for link in links:

    href = link.get("href", "")

    titolo = link.get_text(strip=True)

    if not titolo:
        continue

    if len(titolo) < 15:
        continue

    # solo articoli novità
    if "/novita/" not in href:
        continue

    # evita duplicati
    if href in usati:
        continue

    usati.add(href)

    articoli_validi.append({
        "href": href,
        "titolo": titolo
    })

# tieni solo i primi 30 articoli trovati
articoli_validi = articoli_validi[:30]

print(f"Trovati {len(articoli_validi)} articoli da analizzare")

for articolo in articoli_validi:

    href = articolo["href"]

    titolo = articolo["titolo"]

    print(f"Leggo articolo: {titolo}")

    try:

        articolo_response = requests.get(
            href,
            headers=headers,
            timeout=30
        )

        articolo_response.raise_for_status()

        articolo_soup = BeautifulSoup(
            articolo_response.text,
            "html.parser"
        )

        testo_pagina = articolo_soup.get_text(
            " ",
            strip=True
        )

        # Cerca:
        # Data: 10 Marzo 2025

        match = re.search(
            r"Data:\s*(\d{1,2})\s+([A-Za-zà]+)\s+(\d{4})",
            testo_pagina,
            re.IGNORECASE
        )

        if not match:

            print("NESSUNA DATA TROVATA")
            continue

        giorno = int(match.group(1))

        mese_nome = match.group(2).lower()

        anno = int(match.group(3))

        mese = mesi.get(mese_nome)

        if not mese:

            print("MESE NON RICONOSCIUTO")
            continue

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

        descrizione = titolo

        paragrafi = articolo_soup.find_all("p")

        for p in paragrafi:

            testo = p.get_text(strip=True)

            if len(testo) > 80:

                descrizione = testo[:500]
                break

        items.append({
            "title": titolo,
            "link": href,
            "description": descrizione,
            "pubDate": pub_date
        })

    except Exception as e:

        print(f"ERRORE ARTICOLO: {e}")

# ordina dalla più recente
items.sort(
    key=lambda x: x["pubDate"],
    reverse=True
)

# tieni solo le ultime 15 news reali
items = items[:15]

print("\n========== ORDINE FINALE ==========\n")

for item in items:

    print(
        item["pubDate"].strftime("%d/%m/%Y"),
        "-",
        item["title"]
    )

print("\n===================================\n")

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
    <description>Feed RSS automatico Comune di Carlentini</description>

    {rss_items}

</channel>
</rss>
"""

output_file = os.path.abspath("feed.xml")

with open(output_file, "w", encoding="utf-8") as f:

    f.write(rss_content)

print(f"Feed creato con {len(items)} elementi")
print(f"Feed salvato in: {output_file}")