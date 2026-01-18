import time
import re
import os
import random
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
    "stussy": 65.0, "carhartt": 40.0, "stone island": 85.0,
    "pashanim": 40.0, "pasha": 40.0, "true religion": 60.0,
    "dg": 70.0, "armani": 50.0, "dickies": 45.0
}

VALID_SIZES = ["XXS", "XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL", 
               "34", "36", "38", "40", "42", "44", "46", "48", "50", 
               "W30", "W32", "W34", "W36", "ONE SIZE"]

SUCH_AUFTRÄGE = [
    {"name": "RL Sweater (25)", "webhook": "https://discord.com/api/webhooks/1459964198363725908/RjvrERJNQ-iaKShFmMhVHaVfcBN3Td8JfwwCsDc2pQMXWm7vcOu3iH4982wjVBQK9kEF", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20sweater&price_to=25&order=newest_first"},
    {"name": "Polo Ralph (50)", "webhook": "https://discord.com/api/webhooks/1460654828807258427/5paOEA0obeueKQo9B7b-6EBromCEAcg-NS682OK6FW1fGkS1cxlyNLIXE0a8OUqmNIiV", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20polo&price_from=25&price_to=50&order=newest_first"},
    {"name": "RL Sweater (50)", "webhook": "https://discord.com/api/webhooks/1460655000974786631/HMrBrLPgM9Eb_Egek7DuMN7IjgL-Q-AsQ6-hC1HvH3H5EJJi2yC76aohCgqt7JW-KU5y", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20sweater&price_from=25&price_to=50&order=newest_first"},
    {"name": "Polo Ralph (25)", "webhook": "https://discord.com/api/webhooks/1460654896767434815/TZuVMfoLzB8VMxEbyQqg_1iZ4E68MLOB8ri5gAWX6qO-DLZUf1NpcHEj4EMgANI1Y2kd", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20polo&price_to=25&order=newest_first"},
    {"name": "RL Polo (15)", "webhook": "https://discord.com/api/webhooks/1460655789302612140/wuDR9ww2JU33NBf1ZqSj2wBNkOzinlRpsHLrIfGoD1Dyrht_QBjgmULigYFGQvM8rKHx", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20polo&price_to=15&order=newest_first"},
    {"name": "Lacoste Polo (25)", "webhook": "https://discord.com/api/webhooks/1460655105178337434/qh7WM-izSDnT2OIxsXkh2ekJkhRlDif9fasNhIajw_pCPc0LHGEWVi5z2nQokplZ8Ci3", "vinted_url": "https://www.vinted.de/catalog?search_text=Lacoste%20polo&price_to=25&order=newest_first"},
    {"name": "Lacoste Sweater (50)", "webhook": "https://discord.com/api/webhooks/1460655300750344245/ZAxZomIwH_bF1a8fViRNtvFHs8HVJGabTqYNinlWKNkNTedOVl40Q46_8AkL4Co30StJ", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20sweater&price_from=25&price_to=50&order=newest_first"},
    {"name": "Lacoste Jacke (25)", "webhook": "https://discord.com/api/webhooks/1460655372812550144/3w3_80X3LTXfehz5daa0oemKdw6RcaxZz2VQingdaEgjcS5dGlttKBXUvWIbU-FLWIiN", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20jacke&price_to=25&order=newest_first"},
    {"name": "Anfänger Sweater (30)", "webhook": "https://discord.com/api/webhooks/1462059038693916889/U8p99aMuoSjBK8qdbR7_p0e9PurxZwBgHiiIBjeOVMIkB8r2ObD0q06M1w-zUqpOZJAQ", "vinted_url": "https://www.vinted.de/catalog?search_text=sweater&price_to=30&order=newest_first"},
    {"name": "Pashanim (15)", "webhook": "https://discord.com/api/webhooks/1460274126315982914/m-Vj7rvBdQ0x-ksVoNw9L21IzYYMVDSvyzhfxszW7_DdHZLTzlj31w2RhuYkzlQtIpSW", "vinted_url": "https://www.vinted.de/catalog?search_text=pashanim&price_to=15&order=newest_first"},
    {"name": "Lacoste Polo L (15)", "webhook": "https://discord.com/api/webhooks/1460230213391614076/fwXUTreF8vrgHZei7QFGHkxd_6OgVz-Biq6-aF9Ur4kNRLj7CWWjSX0WEZ6UnrSmH3on", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20polo&price_to=15&size_id[]=3&order=newest_first"}
]

def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    # Stealth-Modus gegen Cloudflare
    options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def start_bot():
    driver = create_driver()
    seen_items = set()
    print(f"🚀 SNIPER START - {len(SUCH_AUFTRÄGE)} AUFTRÄGE")

    start_time = time.time()
    while (time.time() - start_time) < 800: # Läuft ca. 13 Minuten
        for auftrag in SUCH_AUFTRÄGE:
            try:
                driver.get(auftrag['vinted_url'])
                
                # Cookie Banner Check
                try:
                    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))).click()
                except: pass

                # Warten auf Produkte
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'feed-grid__item')]")))
                items = driver.find_elements(By.XPATH, "//div[contains(@class, 'feed-grid__item')]")

                for item in items[:5]:
                    try:
                        url_elem = item.find_element(By.TAG_NAME, "a")
                        url = url_elem.get_attribute("href")
                        if not url or "items" not in url: continue
                        
                        item_id = url.split("/")[-1].split("-")[0]
                        if item_id in seen_items: continue
                        seen_items.add(item_id)

                        # DATEN EXTRAKTION (Robusterer Weg)
                        full_text = item.text
                        lines = [l.strip() for l in full_text.split('\n') if l.strip()]
                        
                        artikel_preis = 0.0
                        groesse = "N/A"

                        for line in lines:
                            # Preis finden
                            if "€" in line and "VERSAND" not in line.upper():
                                m = re.search(r"(\d+[.,]\d+)", line)
                                if m: artikel_preis = float(m.group(1).replace(",", "."))
                            # Größe finden
                            if line.upper() in VALID_SIZES:
                                groesse = line.upper()

                        if artikel_preis > 0:
                            fee = round(0.70 + (artikel_preis * 0.05), 2)
                            total = round(artikel_preis + fee + DEFAULT_SHIPPING, 2)
                            
                            marktwert = 30.0
                            for brand, val in MARKET_DATA.items():
                                if brand in url.lower(): marktwert = val; break
                            profit = round(marktwert - total, 2)

                            # DISCORD SENDEN
                            webhook = DiscordWebhook(url=auftrag['webhook'], username=BOT_NAME)
                            embed = DiscordEmbed(title=f"💎 {auftrag['name']}", color='2ecc71', url=url)
                            embed.add_embed_field(name='📏 GRÖSSE', value=f"**{groesse}**", inline=True)
                            embed.add_embed_field(name='💰 GESAMT', value=f"**{total}€**", inline=True)
                            embed.add_embed_field(name='📊 PROFIT', value=f"**{profit}€**", inline=True)
                            
                            try:
                                img = item.find_element(By.TAG_NAME, "img").get_attribute("src")
                                embed.set_image(url=img)
                            except: pass

                            webhook.add_embed(embed)
                            webhook.execute()
                            print(f"✅ GESENDET: {auftrag['name']} - {total}€")

                    except: continue
                time.sleep(random.uniform(2, 4)) # Menschliche Pause
            except Exception as e:
                print(f"⚠️ Fehler bei {auftrag['name']} (Wahrscheinlich Block oder Timeout)")
                continue

    driver.quit()

if __name__ == "__main__":
    start_bot()
