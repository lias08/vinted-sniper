import os
import time
import re
import asyncio
import discord
from discord.ext import commands, tasks
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from discord_webhook import DiscordWebhook, DiscordEmbed

# =================================================================
# KONFIGURATION
# =================================================================
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
BOT_NAME = "Costello Sniper by Lias"
DEFAULT_SHIPPING = 3.50 
PREFIX = "!" 

# Durchschnittliche Marktwerte für Profit-Berechnung (wird für 'PROFIT' genutzt)
MARKET_DATA = {
    "ralph lauren": 45.0, "lacoste": 50.0, "nike": 35.0, 
    "stussy": 65.0, "carhartt": 40.0, "stone island": 85.0,
    "pashanim": 40.0
}

VALID_SIZES = ["XXS", "XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL", 
               "34", "36", "38", "40", "42", "44", "46", "48", "50", 
               "W30", "W32", "W34", "W36", "ONE SIZE"]

# ALLE DEINE SUCHAUFTRÄGE
SUCH_AUFTRÄGE = [
    {"name": "RL Sweater (25)", "webhook": "https://discord.com/api/webhooks/1459968307317833992/872QLyR-kpgt_suLOMMpmHXqIzAvbIr-1UqKf1Oo0wrEnWo6c8bnSWzoSomPcgRep2Dl", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20sweater&price_to=25&order=newest_first"},
    {"name": "Polo Ralph (50)", "webhook": "https://discord.com/api/webhooks/1459968163931230446/hLnQUo6eTVZwVRwk09XjZlfGvxtV66i5gOUibO1K5FPua93iBJM8FyN1S9uzjWBYGeVA", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20polo&price_from=25&price_to=50&order=newest_first"},
    {"name": "Lacoste Polo (25)", "webhook": "https://discord.com/api/webhooks/1459969267167527116/2oecDcoFw7nRmZ4D04yFEutlWSWE0nfHWm489BrUy6fR8LCbBgxCcTONpZj3HdjT48Pi", "vinted_url": "https://www.vinted.de/catalog?search_text=Lacoste%20polo&price_to=25&order=newest_first"},
    {"name": "RL Sweater (50)", "webhook": "https://discord.com/api/webhooks/1459968307317833992/872QLyR-kpgt_suLOMMpmHXqIzAvbIr-1UqKf1Oo0wrEnWo6c8bnSWzoSomPcgRep2Dl", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20sweater&price_from=25&price_to=50&order=newest_first"},
    {"name": "Lacoste Polo (50)", "webhook": "https://discord.com/api/webhooks/1459969054738485416/zVh8AU0GFum7Io7W6RdQCeoY6wDu35kS0yN4tHsQn6Y6s1mNHy8IjlSR6OnNwC081s72", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20polo&price_from=25&price_to=50&order=newest_first"},
    {"name": "Lacoste Sweater (50)", "webhook": "https://discord.com/api/webhooks/1459969564984086620/hV7o5sAIadVx1TH3JY0h6LqMvrH9JUQfKOpdnD-dGsHO8RXUTbo4vdRwioDV0J1O12EA", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20sweater&price_from=25&price_to=50&order=newest_first"},
    {"name": "Lacoste Sweater (25)", "webhook": "https://discord.com/api/webhooks/1459969414978867424/loVwVme0cTeyzihMfDPsIjeMw-CbK3JJjf7iQSmRnTqPrOlTyLBMapL6BvkZ-dQqu4py", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20sweater&price_to=25&order=newest_first"},
    {"name": "Nike Tracksuit (25)", "webhook": "https://discord.com/api/webhooks/1459969714099851397/3LODYIEOh98xOEDHx8SPtR5lbejv7D8ZU6LewRVJGn21pjJxODFfRxqCBZ6WpjAdqeRX", "vinted_url": "https://www.vinted.de/catalog?search_text=nike%20tracksuits&price_to=25&order=newest_first"},
    {"name": "Nike Tracksuit (50)", "webhook": "https://discord.com/api/webhooks/1459969817581715466/l_HmH5J_SDR_FE-m_aoWIKU7x2Qh2FJ3FgBRldPpWwBhrFmMjS6U-DsdLTbLzaWJrboO", "vinted_url": "https://www.vinted.de/catalog?search_text=nike%20track%20suit&price_from=25&price_to=50&order=newest_first"},
    {"name": "Lacoste Jacke (25)", "webhook": "https://discord.com/api/webhooks/1459970054996365433/6TDcNjmKIxCOavCSIw7oSELNvfkFyelWGAqY9nrnLYrjY-kc-CxDrJmzBGuaTNzJ6YOW", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20jacke&price_to=25&order=newest_first"},
    {"name": "Polo Ralph (25)", "webhook": "https://discord.com/api/webhooks/1459968897259409716/Uhl_qhTtU04X8mUAv6Api_yFrWeV6UgY1bUE-TjImFmOj59agkwiqtqk-bFliUBQG6oX", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20polo&price_to=25&order=newest_first"},
    {"name": "Lacoste Jacke (50)", "webhook": "https://discord.com/api/webhooks/1459971644113293512/1gNG07NG4JuirBZ0FlK_5OtINnzyW4CJM8QeSPcfJdOMp1Fyb81bV_2FLib0D7SJYIlP", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20jacke&price_from=25&price_to=50&order=newest_first"},
    {"name": "Lacoste Jacke (15)", "webhook": "https://discord.com/api/webhooks/1459986874905919721/6pjtyAQVF75Zn7ZY4DLNSPUV9U_KFguGKb9cd86D20wNzFnNsTGp4CbCMnblfFk4mzvt", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20jacke&price_to=15&order=newest_first"},
    {"name": "Lacoste Polo (15)", "webhook": "https://discord.com/api/webhooks/1459985966411551008/ytIBTOlto_8RSqUAZYeBgX3qavbHh23ajC0BJLnIoXgKyKwwQ6OWqmf40BGEeVbHDfGa", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20polo&price_to=15&order=newest_first"},
    {"name": "Ralph Lauren Polo (15)", "webhook": "https://discord.com/api/webhooks/1459986075668713503/ds3fVhyCvj68yBcuo1fxhvxUn3jdXGxZD_8X4vVYOYWrJ7rfTsmCNpL7WtFdn7hAM1UK", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20polo&price_to=15&order=newest_first"},
    {"name": "Ralph Lauren sweater (15)", "webhook": "https://discord.com/api/webhooks/1459986179268284447/Xak2iTOVtRmbGwtG5kBjOE35rSa0OnBckKyDNvI4ZkdqvnzoP8In9gcPZfUmDRQrpkYe", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20sweater&price_to=15&order=newest_first"},
    {"name": "Lacoste sweater (15)", "webhook": "https://discord.com/api/webhooks/1459971644113293512/1gNG07NG4JuirBZ0FlK_5OtINnzyW4CJM8QeSPcfJdOMp1Fyb81bV_2FLib0D7SJYIlP", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20sweater&price_to=15&order=newest_first"},
    {"name": "Pashanim (15)", "webhook": "https://discord.com/api/webhooks/1460274126315982914/m-Vj7rvBdQ0x-ksVoNw9L21IzYYMVDSvyzhfxszW7_DdHZLTzlj31w2RhuYkzlQtIpSW", "vinted_url": "https://www.vinted.de/catalog?search_text=pashanim&price_to=15&order=newest_first"},
    {"name": "Lacoste Polo L (15)", "webhook": "https://discord.com/api/webhooks/1460230213391614076/fwXUTreF8vrgHZei7QFGHkxd_6OgVz-Biq6-aF9Ur4kNRLj7CWWjSX0WEZ6UnrSmH3on", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20polo&price_to=15&size_id[]=3&order=newest_first"}
]

seen_items = set()

# =================================================================
# DRIVER SETUP (Optimiert für GitHub Actions)
# =================================================================
def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # Wichtig für Vinted-Erkennung:
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

driver = create_driver()

# =================================================================
# DISCORD BOT SETUP
# =================================================================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Bot eingeloggt als {bot.user.name}")
    if not sniper_loop.is_running():
        sniper_loop.start()

# =================================================================
# SNIPER HAUPTSCHLEIFE
# =================================================================
@tasks.loop(seconds=15)
async def sniper_loop():
    global driver
    for auftrag in SUCH_AUFTRÄGE:
        try:
            driver.get(auftrag['vinted_url'])
            await asyncio.sleep(3) # Dem Browser Zeit zum Laden geben
            
            # Alle Artikel im Grid finden
            items = driver.find_elements(By.XPATH, "//div[contains(@class, 'feed-grid__item')]")

            for item in items[:5]: # Prüfe die neuesten 5 Artikel pro Suche
                try:
                    url_elem = item.find_element(By.TAG_NAME, "a")
                    url = url_elem.get_attribute("href")
                    if not url or "items" not in url: continue
                    
                    item_id = url.split("/")[-1].split("-")[0]
                    if item_id in seen_items: continue
                    seen_items.add(item_id)

                    # Textanalyse (Preis, Größe extrahieren)
                    full_text_block = item.text
                    lines = [line.strip() for line in full_text_block.split('\n') if line.strip()]

                    artikel_preis = 0.0
                    groesse = "N/A"
                    
                    for line in lines:
                        # Preis-Parsing (Erster Preis im Block)
                        if "€" in line and artikel_preis == 0.0:
                            match = re.search(r"(\d+[,.]\d+|\d+)", line)
                            if match:
                                artikel_preis = float(match.group(1).replace(",", "."))
                        
                        # Größen-Abgleich
                        if any(s == line.upper() for s in VALID_SIZES):
                            groesse = line.upper()

                    # Profit-Berechnung basierend auf MARKET_DATA
                    marke_key = next((k for k in MARKET_DATA if k in auftrag['name'].lower()), None)
                    markt_wert = MARKET_DATA.get(marke_key, 0.0)
                    gesamt_kosten = artikel_preis + DEFAULT_SHIPPING
                    profit = markt_wert - gesamt_kosten if markt_wert > 0 else 0.0

                    # Webhook senden (Layout: Wunschbild)
                    webhook = DiscordWebhook(url=auftrag['webhook'], username=BOT_NAME)
                    embed = DiscordEmbed(title=f"📦 {auftrag['name']}", color='2ecc71', url=url)
                    
                    embed.add_embed_field(name='📏 GRÖSSE', value=f"**{groesse}**", inline=True)
                    embed.add_embed_field(name='🏷️ ARTIKEL', value=f"{artikel_preis}€", inline=True)
                    embed.add_embed_field(name='🚚 VERSAND', value=f"{DEFAULT_SHIPPING}€", inline=True)
                    embed.add_embed_field(name='💰 GESAMT', value=f"**{gesamt_kosten:.2f}€**", inline=True)
                    embed.add_embed_field(name='📈 PROFIT', value=f"**{profit:.2f}€**", inline=True)

                    # Versuche Bild zu laden
                    try:
                        img = item.find_element(By.TAG_NAME, "img").get_attribute("src")
                        if img: embed.set_image(url=img)
                    except: pass

                    webhook.add_embed(embed)
                    webhook.execute()
                    print(f"✅ Treffer: {auftrag['name']} - {artikel_preis}€")

                except Exception:
                    continue
            
            await asyncio.sleep(1) # Kurze Pause zwischen Suchanfragen

        except Exception as e:
            print(f"Fehler im Loop bei {auftrag['name']}: {e}")

if __name__ == "__main__":
    if BOT_TOKEN:
        bot.run(BOT_TOKEN)
    else:
        print("❌ ERROR: Kein DISCORD_BOT_TOKEN in den GitHub Secrets gefunden!")
