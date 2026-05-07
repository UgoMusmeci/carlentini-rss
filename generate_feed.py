import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

URL = "https://www.comune.carlentini.sr.it/novita/"

# Simula un browser reale
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

# Scarica la pagina
response = requests.get(URL, headers=headers)
response.raise_for_status()

# Parsing HTML
soup = BeautifulSoup(response.text, "html.parser")

# Crea feed RSS
fg = FeedGenerator()
fg.title("Comune di Carlentini - Novità")
fg.link(href=URL)
fg.description("Feed RSS automatico generato esternamente")

# Cerca tutti i link presenti nella pagina
links = soup.find_all("a", href=True)

usati = set()
contatore = 0

for link in links:
    href = link["href"]
    testo = link.get_text(strip=True)

    # Salta elementi inutili
    if not testo:
        continue

    if href in usati:
        continue

    # Tiene solo link relativi alle novità
    if "/novita/" not in href:
        continue

    # Evita testi troppo corti
    if len(testo) < 10:
        continue

    usati.add(href)

    # Aggiunge elemento al feed
    fe = fg.add_entry()
    fe.title(testo)
    fe.link(href=href)
    fe.description(testo)

    contatore += 1

    # Limita numero elementi
    if contatore >= 15:
        break

# Salva file RSS
fg.rss_file("feed.xml")

print(f"Feed creato con {contatore} elementi")
print("File generato: feed.xml")