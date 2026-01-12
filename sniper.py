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
VALID_SIZES = ["XXS", "XS", "S", "M", "L", "XL", "XXL", "34", "36", "38", "40", "42", "44", "46"]

SUCH_AUFTRÄGE = [
    {"name": "RL Sweater (25)", "webhook": "https://discord.com/api/webhooks/1459968307317833992/872QLyR-kpgt_suLOMMpmHXqIzAvbIr-1UqKf1Oo0wrEnWo6c8bnSWzoSomPcgRep2Dl", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20sweater&price_to=25&order=newest_first"},
    # ... (Füge hier deine anderen URLs ein)
]

def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--page-load-strategy=eager") 
    options.add_argument("window-size=1200,800")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def start_bot():
    driver = create_driver()
    seen_items = set()
    print("🚀 Sniper gestartet - Detail-Layout aktiv")

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

                        # 1. GRÖSSE
                        groesse = "-"
                        for s in VALID_SIZES:
                            if re.search(rf'\b{s}\b', item_text_upper):
                                groesse = s; break

                        # 2. PREISE (Artikel, Versand, Gebühr)
                        p_match = re.search(r"(\d+[\d,.]*)\s*€", raw_text)
                        artikel_preis = float(p_match.group(1).replace(",", ".")) if p_match else 0.0
                        
                        versand_preis = DEFAULT_SHIPPING
                        ship_match = re.search(r"(\d+[,.]\d+)\s*€\s*VERSAND", item_text_upper)
                        if ship_match:
                            versand_preis = float(ship_match.group(1).replace(",", "."))
                        
                        vinted_fee = round(0.70 + (artikel_preis * 0.05), 2)
                        gesamt_preis = round(artikel_preis + vinted_fee + versand_preis, 2)

                        # 3. PROFIT
                        marktwert = 20.0
                        for brand, val in MARKET_DATA.items():
                            if brand in url.lower(): marktwert = val; break
                        profit = round(marktwert - gesamt_preis, 2)

                        # 4. DISCORD EMBED (Layout wie gewünscht)
                        webhook = DiscordWebhook(url=auftrag['webhook'], username=BOT_NAME)
                        embed = DiscordEmbed(title=f"📦 {auftrag['name']}", color='2ecc71', url=url)
                        
                        embed.add_embed_field(name='📏 GRÖSSE', value=f"{groesse}", inline=True)
                        embed.add_embed_field(name='🏷️ ARTIKEL', value=f"{artikel_preis}€", inline=True)
                        embed.add_embed_field(name='🚚 VERSAND', value=f"{versand_preis}€", inline=True)
                        embed.add_embed_field(name='💰 GESAMT', value=f"**{gesamt_preis}€**", inline=True)
                        embed.add_embed_field(name='📊 PROFIT', value=f"**{profit}€**", inline=True)

                        try:
                            img = item.find_element(By.TAG_NAME, "img").get_attribute("src")
                            if img: embed.set_image(url=img)
                        except: pass

                        webhook.add_embed(embed)
                        webhook.execute()
                    except: continue
            except:
                driver.quit()
                driver = create_driver()
                break
        time.sleep(0.1)

if __name__ == "__main__":
    start_bot()
