import time
import re
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
# MARKEN-DATEN & PREISE (Aus deinen Screenshots)
# =================================================================
BOT_NAME = "Costello Sniper"
DEFAULT_SHIPPING = 3.50 

# Hier alle Aufträge basierend auf deinen Bildern
SUCH_AUFTRÄGE = [
    # JEANS
    {"name": "True Religion Jeans", "max_price": 25, "url": "https://www.vinted.de/catalog?search_text=true%20religion%20jeans&price_to=25&order=newest_first", "webhook": "DEIN_WEBHOOK_HIER"},
    {"name": "D&G Jeans", "max_price": 40, "url": "https://www.vinted.de/catalog?search_text=dolce%20gabbana%20jeans&price_to=40&order=newest_first", "webhook": "DEIN_WEBHOOK_HIER"},
    {"name": "Armani Jeans", "max_price": 30, "url": "https://www.vinted.de/catalog?search_text=armani%20jeans&price_to=30&order=newest_first", "webhook": "DEIN_WEBHOOK_HIER"},
    {"name": "Dickies Pants", "max_price": 25, "url": "https://www.vinted.de/catalog?search_text=dickies%20pants&price_to=25&order=newest_first", "webhook": "DEIN_WEBHOOK_HIER"},
    
    # STONE ISLAND
    {"name": "Stone Island Sweater", "max_price": 60, "url": "https://www.vinted.de/catalog?search_text=stone%20island%20sweater&price_to=60&order=newest_first", "webhook": "DEIN_WEBHOOK_HIER"},
    {"name": "Stone Island Zipper", "max_price": 75, "url": "https://www.vinted.de/catalog?search_text=stone%20island%20zipper&price_to=75&order=newest_first", "webhook": "DEIN_WEBHOOK_HIER"},
    
    # CARHARTT
    {"name": "Carhartt Sweater", "max_price": 20, "url": "https://www.vinted.de/catalog?search_text=carhartt%20sweater&price_to=20&order=newest_first", "webhook": "DEIN_WEBHOOK_HIER"},
    {"name": "Carhartt Jeansjacke", "max_price": 30, "url": "https://www.vinted.de/catalog?search_text=carhartt%20jeansjacke&price_to=30&order=newest_first", "webhook": "DEIN_WEBHOOK_HIER"},
    
    # RALPH LAUREN
    {"name": "RL Polo", "max_price": 7, "url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20polo&price_to=7&order=newest_first", "webhook": "DEIN_WEBHOOK_HIER"},
    {"name": "RL Pullover", "max_price": 15, "url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20pullover&price_to=15&order=newest_first", "webhook": "DEIN_WEBHOOK_HIER"},
    
    # ADIDAS
    {"name": "Adidas Trikot", "max_price": 20, "url": "https://www.vinted.de/catalog?search_text=adidas%20trikot&price_to=20&order=newest_first", "webhook": "DEIN_WEBHOOK_HIER"},
    {"name": "Adidas Tracksuit", "max_price": 40, "url": "https://www.vinted.de/catalog?search_text=adidas%20tracksuit&price_to=40&order=newest_first", "webhook": "DEIN_WEBHOOK_HIER"},

    # LACOSTE
    {"name": "Lacoste All", "max_price": 20, "url": "https://www.vinted.de/catalog?search_text=lacoste&price_to=20&order=newest_first", "webhook": "DEIN_WEBHOOK_HIER"},
    
    # NIKE
    {"name": "Nike Trikot", "max_price": 25, "url": "https://www.vinted.de/catalog?search_text=nike%20trikot&price_to=25&order=newest_first", "webhook": "DEIN_WEBHOOK_HIER"},
    {"name": "Nike Puffer", "max_price": 40, "url": "https://www.vinted.de/catalog?search_text=nike%20puffer&price_to=40&order=newest_first", "webhook": "DEIN_WEBHOOK_HIER"}
]

# Füge hier deine tatsächlichen Webhooks ein oder nutze einen globalen für alle
GLOBAL_WEBHOOK = "HIER_DEINEN_HAUPT_WEBHOOK_EINTRAGEN"

def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    # Stealth User-Agent
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def start_bot():
    driver = create_driver()
    seen_items = set()
    
    # Mische die Aufträge, damit nicht immer die gleichen zuerst geprüft werden (vermeidet Blocks)
    random.shuffle(SUCH_AUFTRÄGE)

    print(f"🚀 Sniper aktiv auf {len(SUCH_AUFTRÄGE)} Suchen.")

    start_time = time.time()
    while (time.time() - start_time) < 300: # 5 Minuten pro Run, um GitHub-Abbruch zu vermeiden
        for auftrag in SUCH_AUFTRÄGE:
            try:
                driver.get(auftrag['url'])
                time.sleep(random.uniform(3, 6)) # Zufällige Pause

                # Check auf Cloudflare/Block
                if "Access Denied" in driver.page_source or "cloudflare" in driver.page_source.lower():
                    print(f"❌ Blockiert bei {auftrag['name']}. Überspringe...")
                    continue

                # Cookie-Banner weg (falls vorhanden)
                try:
                    driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
                except: pass

                # Suche nach Artikeln
                items = driver.find_elements(By.XPATH, "//div[contains(@class, 'feed-grid__item')]")
                
                for item in items[:3]: # Nur die neuesten 3
                    try:
                        url = item.find_element(By.TAG_NAME, "a").get_attribute("href")
                        item_id = url.split("/")[-1].split("-")[0]

                        if item_id in seen_items: continue
                        seen_items.add(item_id)

                        # Preis auslesen
                        raw_text = item.text
                        price_match = re.search(r"(\d+[.,]\d+) €", raw_text)
                        if not price_match: continue
                        
                        current_price = float(price_match.group(1).replace(",", "."))
                        
                        # Discord senden
                        webhook_url = auftrag['webhook'] if "http" in auftrag['webhook'] else GLOBAL_WEBHOOK
                        webhook = DiscordWebhook(url=webhook_url, username=BOT_NAME)
                        
                        embed = DiscordEmbed(title=f"✨ {auftrag['name']} gefunden!", color='03b2f8', url=url)
                        embed.add_embed_field(name='💰 Preis', value=f"**{current_price}€**", inline=True)
                        
                        try:
                            img = item.find_element(By.TAG_NAME, "img").get_attribute("src")
                            embed.set_image(url=img)
                        except: pass

                        webhook.add_embed(embed)
                        webhook.execute()
                        print(f"✅ Snipe gesendet: {auftrag['name']} für {current_price}€")

                    except: continue

            except Exception as e:
                print(f"Fehler bei {auftrag['name']}: {e}")
                continue

    driver.quit()

if __name__ == "__main__":
    start_bot()
