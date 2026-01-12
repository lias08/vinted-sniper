import time
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from discord_webhook import DiscordWebhook, DiscordEmbed

# =================================================================
# KONFIGURATION
# =================================================================
BOT_NAME = "Costello Sniper by Lias"
DEFAULT_SHIPPING = 3.50 

MARKET_DATA = {
    "ralph lauren": 45.0, "lacoste": 50.0, "nike": 35.0, 
    "stussy": 65.0, "carhartt": 40.0, "stone island": 85.0
}
# Liste erweitert um gängige Formate
VALID_SIZES = ["XXS", "XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL", 
               "34", "36", "38", "40", "42", "44", "46", "48", "50", 
               "W30", "W32", "W34", "W36"]

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
    {"name": "Lacoste sweater (15)", "webhook": "https://discord.com/api/webhooks/1459971644113293512/1gNG07NG4JuirBZ0FlK_5OtINnzyW4CJM8QeSPcfJdOMp1Fyb81bV_2FLib0D7SJYIlP", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20sweater&price_to=15&order=newest_first"}
]

def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Extrem große Auflösung erzwingen, damit Texte nicht überlappen
    options.add_argument("window-size=2560,1440")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def start_bot():
    driver = create_driver()
    seen_items = set()
    print("🚀 SNIPER V4 - FINAL FIX GESTARTET")

    while True:
        for auftrag in SUCH_AUFTRÄGE:
            try:
                driver.get(auftrag['vinted_url'])
                # Längeres Warten auf Vinted Server
                WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'feed-grid__item')]")))
                items = driver.find_elements(By.XPATH, "//div[contains(@class, 'feed-grid__item')]")

                for item in items[:5]:
                    try:
                        url_elem = item.find_element(By.TAG_NAME, "a")
                        url = url_elem.get_attribute("href")
                        if not url or "items" not in url: continue
                        item_id = url.split("/")[-1].split("-")[0]
                        
                        if item_id in seen_items: continue
                        seen_items.add(item_id)

                        # --- AGGRESSIVE TEXTANALYSE ---
                        # Wir holen uns den gesamten Textblock und zerlegen ihn
                        full_text_block = item.text
                        lines = [line.strip() for line in full_text_block.split('\n') if line.strip()]

                        # Debugging-Ausgabe in die Konsole (für GitHub Logs)
                        print(f"--- Prüfe Item {item_id} ---")
                        print(f"Gefundene Textzeilen: {lines}")

                        artikel_preis = 0.0
                        groesse = "-"
                        versand_preis = DEFAULT_SHIPPING

                        # 1. PREIS FINDEN (Die Zeile mit € aber ohne VERSAND)
                        for line in lines:
                            if "€" in line and "VERSAND" not in line.upper():
                                # Regex sucht nach "Zahl,Zahl"
                                match = re.search(r"(\d+[,.]\d+)", line)
                                if match:
                                    artikel_preis = float(match.group(1).replace(",", "."))
                                    print(f"-> Preis gefunden: {artikel_preis}")
                                    break # Erster Treffer ist meist der richtige

                        # 2. GRÖSSE FINDEN
                        # Strategie A: Exakte Übereinstimmung einer Zeile
                        for line in lines:
                            clean = line.upper().strip()
                            if clean in VALID_SIZES:
                                groesse = clean; break
                        # Strategie B: Wortsuche im gesamten Block (falls Größe mit Marke zusammenklebt)
                        if groesse == "-":
                            full_upper = full_text_block.upper()
                            for s in VALID_SIZES:
                                # Sucht nach Größe umgeben von Leerzeichen oder Slash (z.B. " L " oder "/L")
                                if re.search(rf"(^|\s|/){s}($|\s|/)", full_upper):
                                    groesse = s; break
                        print(f"-> Größe gefunden: {groesse}")

                        # 3. VERSAND FINDEN
                        for line in lines:
                            if "€" in line and "VERSAND" in line.upper():
                                match = re.search(r"(\d+[,.]\d+)", line)
                                if match:
                                    versand_preis = float(match.group(1).replace(",", "."))
                                    break

                        # --- BERECHNUNG & SENDEN ---
                        fee = round(0.70 + (artikel_preis * 0.05), 2)
                        total = round(artikel_preis + fee + versand_preis, 2)
                        
                        marktwert = 20.0
                        for brand, val in MARKET_DATA.items():
                            if brand in url.lower(): marktwert = val; break
                        profit = round(marktwert - total, 2)

                        # Nur senden wenn wir einen Preis haben (verhindert 0.0€ Posts bei Ladefehlern)
                        if artikel_preis > 0:
                            webhook = DiscordWebhook(url=auftrag['webhook'], username=BOT_NAME)
                            embed = DiscordEmbed(title=f"📦 {auftrag['name']}", color='2ecc71', url=url)
                            
                            embed.add_embed_field(name='📏 GRÖSSE', value=f"**{groesse}**", inline=True)
                            embed.add_embed_field(name='🏷️ ARTIKEL', value=f"{artikel_preis}€", inline=True)
                            embed.add_embed_field(name='🚚 VERSAND', value=f"{versand_preis}€", inline=True)
                            embed.add_embed_field(name='💰 GESAMT', value=f"**{total}€**", inline=True)
                            embed.add_embed_field(name='📊 PROFIT', value=f"**{profit}€**", inline=True)

                            try:
                                img = item.find_element(By.TAG_NAME, "img").get_attribute("src")
                                if img: embed.set_image(url=img)
                            except: pass

                            webhook.add_embed(embed)
                            webhook.execute()
                            print("✅ Erfolgreich gesendet!")
                        else:
                            print("⚠️ Artikel übersprungen (Preis konnte nicht ermittelt werden)")

                    except Exception as e:
                        print(f"Fehler beim Item: {e}")
                        continue
            except Exception as e:
                print(f"Kritischer Browser-Fehler: {e}")
                driver.quit()
                driver = create_driver()
                break
        time.sleep(5) # Stabilitätspause

if __name__ == "__main__":
    start_bot()
