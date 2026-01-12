import time
import sys
import re
import os
import subprocess
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
BOT_NAME = "Costello Sniper"
DEFAULT_SHIPPING = 3.50  # Fallback, falls kein Versandpreis gefunden wird

MARKET_DATA = {
    "ralph lauren": 45.0, "lacoste": 50.0, "nike": 35.0, 
    "adidas": 30.0, "stussy": 65.0, "carhartt": 40.0, "stone island": 85.0
}
VALID_SIZES = ["XXS", "XS", "S", "M", "L", "XL", "XXL", "34", "36", "38", "40", "42", "44", "46"]

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
    {"name": "Polo Ralph (25)", "webhook": "https://discord.com/api/webhooks/1459968897259409716/Uhl_qhTtU04X8mUAv6Api_yFrWeV6UgN1bUE-TjImFmOj59agkwiqtqk-bFliUBQG6oX", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20polo&price_to=25&order=newest_first"},
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
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1200,800")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def start_bot():
    if os.name == 'nt': subprocess.run("taskkill /f /im chrome.exe /t", capture_output=True, shell=True)
    driver = create_driver()
    seen_items = set()
    print("🚀 Sniper gestartet | Markierung für Versand < 2.00€ aktiv")

    while True:
        for auftrag in SUCH_AUFTRÄGE:
            try:
                driver.get(auftrag['vinted_url'])
                WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.feed-grid__item")))
                items = driver.find_elements(By.CSS_SELECTOR, "div.feed-grid__item")
                
                for item in items[:3]:
                    try:
                        link_elem = item.find_element(By.TAG_NAME, "a")
                        url = link_elem.get_attribute("href")
                        item_id = url.split("/")[-1].split("-")[0]
                        
                        if item_id in seen_items: continue
                        seen_items.add(item_id)

                        raw_text = item.text
                        item_text_upper = raw_text.upper()
                        
                        # 1. VERSAND ERKENNUNG
                        # Sucht nach Mustern wie "1,95 €" oder "1.95 €" im Text unter dem Preis
                        aktuelle_shipping = DEFAULT_SHIPPING
                        ship_match = re.search(r"(\d+[,.]\d+)\s*€\s*VERSAND", item_text_upper)
                        if ship_match:
                            aktuelle_shipping = float(ship_match.group(1).replace(",", "."))

                        is_cheap_shipping = aktuelle_shipping <= 2.00

                        # 2. GRÖSSEN-ERKENNUNG
                        groesse = "-"
                        for s in VALID_SIZES:
                            if re.search(rf'\b{s}\b', item_text_upper):
                                groesse = s; break

                        # 3. PREISE EXTRAHIEREN
                        p_match = re.search(r"(\d+[\d,.]*)\s*€", raw_text)
                        artikel_preis = float(p_match.group(1).replace(",", ".")) if p_match else 0.0
                        vinted_fee = round(0.70 + (artikel_preis * 0.05), 2)
                        gesamt_preis = round(artikel_preis + vinted_fee + aktuelle_shipping, 2)

                        # 4. PROFIT AI
                        marktwert = 20.0
                        for brand, val in MARKET_DATA.items():
                            if brand in url.lower(): marktwert = val; break
                        profit = round(marktwert - gesamt_preis, 2)

                        # 5. DISCORD SENDEN
                        webhook = DiscordWebhook(url=auftrag['webhook'], username=BOT_NAME)
                        
                        # Markierung im Content, falls Versand billig ist
                        content = ""
                        if is_cheap_shipping:
                            content = "🚚 **BILLIGER VERSAND GEFUNDEN!**"
                        
                        if groesse == "L" and gesamt_preis <= 18.0:
                            content += " 🚨 @everyone **TOP DEAL (GRÖSSE L)!**"
                        
                        if content:
                            webhook.set_content(content)

                        # Farbe ändern auf Gold/Gelb bei billigem Versand
                        embed_color = 'f1c40f' if is_cheap_shipping else '2ecc71'
                        
                        embed = DiscordEmbed(title=f"📦 {auftrag['name']}", color=embed_color, url=url)
                        embed.add_embed_field(name='📏 GRÖSSE', value=f"**{groesse}**", inline=True)
                        embed.add_embed_field(name='🏷️ ARTIKEL', value=f"{artikel_preis}€", inline=True)
                        embed.add_embed_field(name='🚚 VERSAND', value=f"**{aktuelle_shipping}€**" + (" ✅" if is_cheap_shipping else ""), inline=True)
                        embed.add_embed_field(name='💰 GESAMT', value=f"**{gesamt_preis}€**", inline=True)
                        embed.add_embed_field(name='📊 PROFIT', value=f"**+{profit}€**", inline=True)
                        
                        try:
                            img = item.find_element(By.TAG_NAME, "img").get_attribute("src")
                            if img: embed.set_image(url=img)
                        except: pass
                        
                        webhook.add_embed(embed)
                        webhook.execute()

                    except Exception: continue
            except Exception:
                driver.quit()
                driver = create_driver()
                break

        time.sleep(0.5)

if __name__ == "__main__":
    start_bot()
