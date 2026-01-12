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
DEFAULT_SHIPPING = 4.15 # Angepasst an dein Bild (+4.15 €)

MARKET_DATA = {
    "ralph lauren": 45.0, "lacoste": 50.0, "nike": 35.0, 
    "stussy": 65.0, "carhartt": 40.0, "stone island": 85.0,
    "jordan": 120.0
}

VALID_SIZES = ["XXS", "XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL", 
               "34", "36", "38", "40", "42", "44", "46", "48", "50", 
               "W30", "W32", "W34", "W36", "47"]

SUCH_AUFTRÄGE = [
    {"name": "RL Sweater (25)", "webhook": "DEIN_WEBHOOK", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20sweater&price_to=25&order=newest_first"},
    # ... Deine restlichen Aufträge hier einfügen
]

def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=2560,1440")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def start_bot():
    driver = create_driver()
    seen_items = set()
    print("🚀 SNIPER V4 - MODERN OVERLAY LOOK GESTARTET")

    while True:
        for auftrag in SUCH_AUFTRÄGE:
            try:
                driver.get(auftrag['vinted_url'])
                WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'feed-grid__item')]")))
                items = driver.find_elements(By.XPATH, "//div[contains(@class, 'feed-grid__item')]")

                for item in items[:5]:
                    try:
                        url_elem = item.find_element(By.TAG_NAME, "a")
                        url = url_elem.get_attribute("href")
                        if not url or "items" not in url: continue
                        
                        voller_titel = url_elem.get_attribute("title") or "Artikel"
                        item_id = url.split("/")[-1].split("-")[0]
                        if item_id in seen_items: continue
                        seen_items.add(item_id)

                        full_text_block = item.text
                        lines = [line.strip() for line in full_text_block.split('\n') if line.strip()]

                        artikel_preis = 0.0
                        groesse = "-"
                        brand = "Unbekannt"

                        # --- DATEN-EXTRAKTION ---
                        for line in lines:
                            if "€" in line and "VERSAND" not in line.upper():
                                match = re.search(r"(\d+[,.]\d+)", line)
                                if match:
                                    artikel_preis = float(match.group(1).replace(",", "."))
                                    break
                        
                        for line in lines:
                            if line.upper() in VALID_SIZES:
                                groesse = line.upper()
                                break
                        
                        for b in MARKET_DATA.keys():
                            if b in voller_titel.lower() or b in url.lower():
                                brand = b.capitalize()
                                break

                        # --- BERECHNUNG ---
                        total = round(artikel_preis + 0.70 + (artikel_preis * 0.05) + DEFAULT_SHIPPING, 2)
                        marktwert = MARKET_DATA.get(brand.lower(), 40.0)
                        profit = round(marktwert - total, 2)

                        # --- DISCORD MODERN OVERLAY DESIGN ---
                        if artikel_preis > 0:
                            webhook = DiscordWebhook(url=auftrag['webhook'], username=BOT_NAME)
                            
                            # Haupt-Embed (Schwarzer Hintergrund durch Discord Dark Mode)
                            embed = DiscordEmbed(
                                title=f"🇫🇷 {voller_titel} | {total} €", 
                                description=f"✨ **Zustand:** Sehr gut\n🕒 **Veröffentlicht:** vor 1 Minute",
                                color='2f3136', # Dunkelgrau für dezenten Look
                                url=url
                            )
                            
                            # Fields mit Icons wie im Bild
                            embed.add_embed_field(name='💰 Price', value=f"**{artikel_preis} €** (+ {DEFAULT_SHIPPING} €)", inline=True)
                            embed.add_embed_field(name='🏷️ Brand', value=f"{brand}", inline=True)
                            embed.add_embed_field(name='📏 Size', value=f"{groesse}", inline=True)
                            
                            # Profit Field hervorgehoben
                            embed.add_embed_field(name='📈 Estimated Profit', value=f"**{profit} €**", inline=False)

                            # Bild-Logik (Setzt das Bild groß unten rein, wie bei Vinted Bots üblich)
                            try:
                                img = item.find_element(By.TAG_NAME, "img").get_attribute("src")
                                if img: embed.set_image(url=img)
                            except: pass

                            # Footer für Bot Info
                            embed.set_footer(text=f"🚀 {BOT_NAME} | 🏷️ {brand.lower()} | 💲 {total} €")

                            webhook.add_embed(embed)
                            webhook.execute()
                            print(f"✅ {voller_titel} gesendet!")

                    except Exception as e:
                        continue
            except Exception as e:
                driver.quit()
                driver = create_driver()
                break
        time.sleep(1)

if __name__ == "__main__":
    start_bot()
