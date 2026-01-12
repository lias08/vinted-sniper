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
BOT_NAME = "Costello Sniper"
# HIER DEINE BILD-URL FÜR DAS PROFILBILD EINTRAGEN
BOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/732/732228.png" 

DEFAULT_SHIPPING = 3.50 

MARKET_DATA = {
    "ralph lauren": 45.0, "lacoste": 50.0, "nike": 35.0, 
    "stussy": 65.0, "carhartt": 40.0, "stone island": 85.0
}

VALID_SIZES = ["XXS", "XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL", 
               "34", "36", "38", "40", "42", "44", "46", "48", "50", 
               "W30", "W32", "W34", "W36"]

# Beispiel-Auftrag (Ersetze DEIN_WEBHOOK_URL mit deinem Link!)
SUCH_AUFTRÄGE = [
    {"name": "RL Sweater (25)", "webhook": "https://discord.com/api/webhooks/...", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20sweater&price_to=25&order=newest_first"},
]

def create_driver():
    options = Options()
    # WICHTIG: Manchmal blockt Headless. Wenn er nichts schickt, ändere headless=new zu False zum Testen.
    options.add_argument("--headless=new") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled") # Versteckt Bot-Status
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def start_bot():
    print("🛰️ INITIALISIERE BROWSER...")
    driver = create_driver()
    seen_items = set()
    
    # Test beim Start
    print("🧪 SENDE TEST-SIGNAL AN DISCORD...")
    test_webhook = DiscordWebhook(url=SUCH_AUFTRÄGE[0]['webhook'], content="🚀 **Bot gestartet und bereit!**", username=BOT_NAME, avatar_url=BOT_AVATAR)
    test_webhook.execute()

    while True:
        for auftrag in SUCH_AUFTRÄGE:
            try:
                print(f"🔍 Suche läuft: {auftrag['name']}")
                driver.get(auftrag['vinted_url'])
                
                # Prüfen auf Cloudflare oder Bot-Sperre
                if "cloudflare" in driver.page_source.lower() or "px-captcha" in driver.page_source.lower():
                    print("❌ BOT GEBLOCKT (CAPTCHA). Warte 2 Minuten...")
                    time.sleep(120)
                    continue

                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'feed-grid__item')]")))
                items = driver.find_elements(By.XPATH, "//div[contains(@class, 'feed-grid__item')]")

                for item in items[:5]:
                    try:
                        url_elem = item.find_element(By.TAG_NAME, "a")
                        url = url_elem.get_attribute("href")
                        produkt_name = url_elem.get_attribute("title") or "Vinted Piece"

                        if not url or "items" not in url: continue
                        item_id = url.split("/")[-1].split("-")[0]
                        
                        if item_id in seen_items: continue
                        seen_items.add(item_id)

                        # Extraktion
                        lines = [l.strip() for l in item.text.split('\n') if l.strip()]
                        
                        artikel_preis = 0.0
                        groesse = "-"
                        for line in lines:
                            if "€" in line and "VERSAND" not in line.upper():
                                m = re.search(r"(\d+[,.]\d+)", line)
                                if m: artikel_preis = float(m.group(1).replace(",", ".")); break
                        
                        for line in lines:
                            if line.upper() in VALID_SIZES: groesse = line.upper(); break

                        # Senden
                        if artikel_preis > 0:
                            webhook = DiscordWebhook(url=auftrag['webhook'], username=BOT_NAME, avatar_url=BOT_AVATAR)
                            embed = DiscordEmbed(title=f"👕 {produkt_name}", color='2ecc71', url=url)
                            embed.add_embed_field(name='📏 GRÖSSE', value=f"**{groesse}**", inline=True)
                            embed.add_embed_field(name='💰 PREIS', value=f"**{artikel_preis}€**", inline=True)
                            embed.add_embed_field(name='🔗 LINK', value=f"[➔ Zum Piece]({url})", inline=False)
                            
                            try:
                                img = item.find_element(By.TAG_NAME, "img").get_attribute("src")
                                if img: embed.set_image(url=img)
                            except: pass

                            webhook.add_embed(embed)
                            webhook.execute()
                            print(f"✅ Item gefunden & gesendet: {item_id}")

                    except Exception: continue
            
            except Exception as e:
                print(f"⚠️ Fehler in der Schleife: {e}")
                driver.quit()
                time.sleep(5)
                driver = create_driver()
                break
        
        time.sleep(15) # Wichtig: Längere Pause, um nicht gebannt zu werden!

if __name__ == "__main__":
    start_bot()
