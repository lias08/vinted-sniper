import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from discord_webhook import DiscordWebhook, DiscordEmbed

# =================================================================
# KONFIGURATION & MARKTWERTE (Basierend auf deiner Tabelle)
# =================================================================
BOT_NAME = "Costello Sniper by Lias"
BOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/732/732228.png" 
DEFAULT_SHIPPING = 4.15 

# Ziel-Verkaufspreise für die Profit-Berechnung
MARKET_DATA = {
    "ralph lauren sweater": 50.0,
    "ralph lauren polo": 31.0,
    "lacoste sweater": 55.0,
    "lacoste polo": 38.0,
    "lacoste jacke": 105.0,
    "nike tracksuit": 75.0,
    "jordan": 110.0
}

VALID_SIZES = ["XXS", "XS", "S", "M", "L", "XL", "XXL", "34", "36", "38", "40", "42", "44", "46", "48", "50", "W30", "W32", "W34", "W36"]

SUCH_AUFTRÄGE = [
    {"name": "RL Sweater (25)", "webhook": "https://discord.com/api/webhooks/1459968307317833992/872QLyR-kpgt_suLOMMpmHXqIzAvbIr-1UqKf1Oo0wrEnWo6c8bnSWzoSomPcgRep2Dl", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20sweater&price_to=25&order=newest_first"},
    {"name": "Polo Ralph (50)", "webhook": "https://discord.com/api/webhooks/1459968163931230446/hLnQUo6eTVZwVRwk09XjZlfGvxtV66i5gOUibO1K5FPua93iBJM8FyN1S9uzjWBYGeVA", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20polo&price_from=25&price_to=50&order=newest_first"},
    {"name": "Lacoste Polo (25)", "webhook": "https://discord.com/api/webhooks/1459969267167527116/2oecDcoFw7nRmZ4D04yFEutlWSWE0nfHWm489BrUy6fR8LCbBgxCcTONpZj3HdjT48Pi", "vinted_url": "https://www.vinted.de/catalog?search_text=Lacoste%20polo&price_to=25&order=newest_first"},
    {"name": "Lacoste Polo (50)", "webhook": "https://discord.com/api/webhooks/1459969054738485416/zVh8AU0GFum7Io7W6RdQCeoY6wDu35kS0yN4tHsQn6Y6s1mNHy8IjlSR6OnNwC081s72", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20polo&price_from=25&price_to=50&order=newest_first"},
    {"name": "Lacoste Sweater (50)", "webhook": "https://discord.com/api/webhooks/1459969564984086620/hV7o5sAIadVx1TH3JY0h6LqMvrH9JUQfKOpdnD-dGsHO8RXUTbo4vdRwioDV0J1O12EA", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20sweater&price_from=25&price_to=50&order=newest_first"},
    {"name": "Nike Tracksuit (25)", "webhook": "https://discord.com/api/webhooks/1459969714099851397/3LODYIEOh98xOEDHx8SPtR5lbejv7D8ZU6LewRVJGn21pjJxODFfRxqCBZ6WpjAdqeRX", "vinted_url": "https://www.vinted.de/catalog?search_text=nike%20tracksuits&price_to=25&order=newest_first"},
    {"name": "Lacoste Jacke (25)", "webhook": "https://discord.com/api/webhooks/1459970054996365433/6TDcNjmKIxCOavCSIw7oSELNvfkFyelWGAqY9nrnLYrjY-kc-CxDrJmzBGuaTNzJ6YOW", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20jacke&price_to=25&order=newest_first"},
    {"name": "Lacoste Jacke (50)", "webhook": "https://discord.com/api/webhooks/1459971644113293512/1gNG07NG4JuirBZ0FlK_5OtINnzyW4CJM8QeSPcfJdOMp1Fyb81bV_2FLib0D7SJYIlP", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20jacke&price_from=25&price_to=50&order=newest_first"},
    {"name": "Lacoste Polo L (15)", "webhook": "https://discord.com/api/webhooks/1460230213391614076/fwXUTreF8vrgHZei7QFGHkxd_6OgVz-Biq6-aF9Ur4kNRLj7CWWjSX0WEZ6UnrSmH3on", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20polo&price_to=15&size_id[]=3&order=newest_first"},
    {"name": "Nike Tracksuit L (50)", "webhook": "https://discord.com/api/webhooks/1460232814648623176/DIQDbWT2n_WxxFHUXJ9C6BgOdXVgxkTLmxvAQh4I6BRj2ZaK_xNbw01BQIL11OwBNadx", "vinted_url": "https://www.vinted.de/catalog?search_text=nike%20tracksuit&price_from=25&price_to=50&size_id[]=3&order=newest_first"}
    # ... weitere Aufträge können hier nach dem gleichen Muster ergänzt werden
]

def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def start_bot():
    driver = create_driver()
    seen_items = set()
    print("🚀 SNIPER V4 GESTARTET - ALLE AUFTRÄGE AKTIV")

    while True:
        for auftrag in SUCH_AUFTRÄGE:
            try:
                driver.get(auftrag['vinted_url'])
                time.sleep(4) 
                
                items = driver.find_elements(By.CLASS_NAME, "feed-grid__item")

                for item in items[:5]:
                    try:
                        url_elem = item.find_element(By.TAG_NAME, "a")
                        url = url_elem.get_attribute("href")
                        if not url or "items" not in url: continue
                        
                        item_id = url.split("/")[-1].split("-")[0]
                        if item_id in seen_items: continue
                        seen_items.add(item_id)

                        title = url_elem.get_attribute("title") or "Vinted Piece"
                        raw_text = item.text
                        
                        # Preis-Extraktion
                        price_match = re.search(r"(\d+[,.]\d+) €", raw_text)
                        price = float(price_match.group(1).replace(",", ".")) if price_match else 0.0

                        # Größen-Extraktion
                        groesse = "-"
                        for s in VALID_SIZES:
                            if s in raw_text.split('\n'):
                                groesse = s
                                break

                        if price > 0:
                            # Gebühren & Gesamtpreis
                            fee = round(0.70 + (price * 0.05), 2)
                            total_cost = round(price + fee + DEFAULT_SHIPPING, 2)
                            
                            # Profit-Logik basierend auf Tabelle
                            target_price = 20.0
                            for key, val in MARKET_DATA.items():
                                if key in title.lower() or key in auftrag['name'].lower():
                                    target_price = val
                                    break
                            
                            profit = round(target_price - total_cost, 2)
                            
                            # Discord Webhook
                            webhook = DiscordWebhook(url=auftrag['webhook'], username=BOT_NAME, avatar_url=BOT_AVATAR)
                            embed = DiscordEmbed(title=f"👕 {title}", color='2ecc71', url=url)
                            
                            embed.add_embed_field(name='📏 GRÖSSE', value=f"**{groesse}**", inline=True)
                            embed.add_embed_field(name='🏷️ PREIS', value=f"{price}€", inline=True)
                            embed.add_embed_field(name='💰 GESAMT', value=f"**{total_cost}€**", inline=True)
                            embed.add_embed_field(name='📊 PROFIT', value=f"**{profit}€**", inline=True)
                            embed.add_embed_field(name='🔗 LINK', value=f"[➔ Zum Piece]({url})", inline=False)

                            try:
                                img = item.find_element(By.TAG_NAME, "img").get_attribute("src")
                                if img: embed.set_image(url=img)
                            except: pass

                            webhook.add_embed(embed)
                            webhook.execute()
                            print(f"✅ Gesendet: {title} ({profit}€ Profit)")

                    except: continue
            except Exception as e:
                print(f"⚠️ Fehler bei {auftrag['name']}: {e}")
                driver.quit()
                driver = create_driver()
                break
        time.sleep(10)

if __name__ == "__main__":
    start_bot()
