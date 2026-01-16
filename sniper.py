import time
import re
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from discord_webhook import DiscordWebhook, DiscordEmbed

# =================================================================
# KONFIGURATION
# =================================================================
BOT_NAME = "Costello Sniper"
DEFAULT_SHIPPING = 4.50

# Marktwerte für Profit-Berechnung (Anpassen nach Bedarf)
MARKET_DATA = {
    "ralph": 40.0, "lacoste": 45.0, "nike": 35.0, "pasha": 45.0, "sweater": 30.0
}

SUCH_AUFTRÄGE = [
    # --- RALPH LAUREN ---
    {"name": "RL Sweater (25)", "webhook": "https://discord.com/api/webhooks/1459964198363725908/RjvrERJNQ-iaKShFmMhVHaVfcBN3Td8JfwwCsDc2pQMXWm7vcOu3iH4982wjVBQK9kEF", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20sweater&price_to=25&order=newest_first"},
    {"name": "Polo Ralph (50)", "webhook": "https://discord.com/api/webhooks/1460654828807258427/5paOEA0obeueKQo9B7b-6EBromCEAcg-NS682OK6FW1fGkS1cxlyNLIXE0a8OUqmNIiV", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20polo&price_from=25&price_to=50&order=newest_first"},
    {"name": "RL Sweater (50)", "webhook": "https://discord.com/api/webhooks/1460655000974786631/HMrBrLPgM9Eb_Egek7DuMN7IjgL-Q-AsQ6-hC1HvH3H5EJJi2yC76aohCgqt7JW-KU5y", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20sweater&price_from=25&price_to=50&order=newest_first"},
    {"name": "Polo Ralph (25)", "webhook": "https://discord.com/api/webhooks/1460654896767434815/TZuVMfoLzB8VMxEbyQqg_1iZ4E68MLOB8ri5gAWX6qO-DLZUf1NpcHEj4EMgANI1Y2kd", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20polo&price_to=25&order=newest_first"},
    {"name": "RL Polo (15)", "webhook": "https://discord.com/api/webhooks/1460655789302612140/wuDR9ww2JU33NBf1ZqSj2wBNkOzinlRpsHLrIfGoD1Dyrht_QBjgmULigYFGQvM8rKHx", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20polo&price_to=15&order=newest_first"},
    {"name": "RL Sweater (15)", "webhook": "https://discord.com/api/webhooks/1460655889454465034/FMY9RdPmHrggia1Cgm9KCHQ9AzBiQILGLtzgneqfBKZ5wBvS6ax63DqqaKmwcRNhcCv9", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20sweater&price_to=15&order=newest_first"},
    
    # --- LACOSTE ---
    {"name": "Lacoste Polo (25)", "webhook": "https://discord.com/api/webhooks/1460655105178337434/qh7WM-izSDnT2OIxsXkh2ekJkhRlDif9fasNhIajw_pCPc0LHGEWVi5z2nQokplZ8Ci3", "vinted_url": "https://www.vinted.de/catalog?search_text=Lacoste%20polo&price_to=25&order=newest_first"},
    {"name": "Lacoste Polo (50)", "webhook": "https://discord.com/api/webhooks/1460654610673963071/xga-4p1sxuk4E-gbhkFwvjhMnkr8Yat2HYlv72P_vGQdWsc48wQz6-4HKSEOuTSFOYS_", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20polo&price_from=25&price_to=50&order=newest_first"},
    {"name": "Lacoste Sweater (50)", "webhook": "https://discord.com/api/webhooks/1460655300750344245/ZAxZomIwH_bF1a8fViRNtvFHs8HVJGabTqYNinlWKNkNTedOVl40Q46_8AkL4Co30StJ", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20sweater&price_from=25&price_to=50&order=newest_first"},
    {"name": "Lacoste Sweater (25)", "webhook": "https://discord.com/api/webhooks/1460655246857605161/0fFJiGCCC4YBdBr5OoXPTy8w8RTMFtqQVWWS4s1B-T8XSU9MTnarPcIpItBAVC7uYhWY", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20sweater&price_to=25&order=newest_first"},
    {"name": "Lacoste Jacke (25)", "webhook": "https://discord.com/api/webhooks/1460655372812550144/3w3_80X3LTXfehz5daa0oemKdw6RcaxZz2VQingdaEgjcS5dGlttKBXUvWIbU-FLWIiN", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20jacke&price_to=25&order=newest_first"},
    {"name": "Lacoste Jacke (50)", "webhook": "https://discord.com/api/webhooks/1460655442140201123/y_Wv96Joot0wsP4i8IOc5t9y2B9a7nQEwGlMT163rMJ82ZAzGjexx9ykHxR2_vTlSa-g", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20jacke&price_from=25&price_to=50&order=newest_first"},
    {"name": "Lacoste Jacke (15)", "webhook": "https://discord.com/api/webhooks/1460655726908412035/N1j4pWdDIm6NV9wEIV1G2X2Fao-7ZQUU4ueVP1Fw-l3rNOXsOMgojLy0X_fpl4M3iZw1", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20jacke&price_to=15&order=newest_first"},
    {"name": "Lacoste Polo (15)", "webhook": "https://discord.com/api/webhooks/1460655671186952387/HRk5xVjzhV1GJ-3RWJS4NC75e0YGY-fyXOMlaFG5Bg7UfQtvVdCqtEVtwWlPmTZn0Har", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20polo&price_to=15&order=newest_first"},
    {"name": "Lacoste Sweater (15)", "webhook": "https://discord.com/api/webhooks/1459985865437614100/bZBHyPC-QGzbxiFqkWtq4eTAhkLmXln6r2f3wcgse1jgU3KhwnqOAmKdsjUQ1Inr1U4r", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20sweater&price_to=15&order=newest_first"},
    
    # --- NIKE ---
    {"name": "Nike Tracksuit (25)", "webhook": "https://discord.com/api/webhooks/1460655532418269306/OYFbbaCBOCIjHBUKTjoHdB60UpA8CX0rb5627Gm4G_MlJfNMmlrM8H8jI14fHY3QqxI6", "vinted_url": "https://www.vinted.de/catalog?search_text=nike%20tracksuits&price_to=25&order=newest_first"},
    {"name": "Nike Tracksuit (50)", "webhook": "https://discord.com/api/webhooks/1459969817581715466/l_HmH5J_SDR_FE-m_aoWIKU7x2Qh2FJ3FgBRldPpWwBhrFmMjS6U-DsdLTbLzaWJrboO", "vinted_url": "https://www.vinted.de/catalog?search_text=nike%20track%20suit&price_from=25&price_to=50&order=newest_first"},

    # --- PASHANIM / SPECIAL ---
    {"name": "Pashanim (15)", "webhook": "https://discord.com/api/webhooks/1460274126315982914/m-Vj7rvBdQ0x-ksVoNw9L21IzYYMVDSvyzhfxszW7_DdHZLTzlj31w2RhuYkzlQtIpSW", "vinted_url": "https://www.vinted.de/catalog?search_text=pashanim&price_to=15&order=newest_first"},
    {"name": "Pasha (15)", "webhook": "https://discord.com/api/webhooks/1460274126315982914/m-Vj7rvBdQ0x-ksVoNw9L21IzYYMVDSvyzhfxszW7_DdHZLTzlj31w2RhuYkzlQtIpSW", "vinted_url": "https://www.vinted.de/catalog?search_text=pasha&price_to=15&order=newest_first"},
    {"name": "Pashanim (25)", "webhook": "https://discord.com/api/webhooks/1460274208675205120/2XgKnQE_aB3TH9jhvJwZ4SpcCN1Y00-xTjd7Dm6yTh3CXIffqGhSmUk8lynAGeAGr0cC", "vinted_url": "https://www.vinted.de/catalog?search_text=pashanim&price_to=25&order=newest_first"},
    {"name": "Pasha (25)", "webhook": "https://discord.com/api/webhooks/1460274208675205120/2XgKnQE_aB3TH9jhvJwZ4SpcCN1Y00-xTjd7Dm6yTh3CXIffqGhSmUk8lynAGeAGr0cC", "vinted_url": "https://www.vinted.de/catalog?search_text=pasha&price_to=25&order=newest_first"},
    {"name": "Pashanim (50)", "webhook": "https://discord.com/api/webhooks/1460274319858073764/gB6Rq-L02mymDD-FiQk7RpU4ZCJUeSI8lv7xYyEzWeIb_H2tHbY79TS62XMHhKdRpUsU", "vinted_url": "https://www.vinted.de/catalog?search_text=pashanim&price_to=50&order=newest_first"},
    {"name": "Pasha (50)", "webhook": "https://discord.com/api/webhooks/1460274319858073764/gB6Rq-L02mymDD-FiQk7RpU4ZCJUeSI8lv7xYyEzWeIb_H2tHbY79TS62XMHhKdRpUsU", "vinted_url": "https://www.vinted.de/catalog?search_text=pasha&price_to=50&order=newest_first"},
    {"name": "Sweater (20)", "webhook": "https://discord.com/api/webhooks/1460300613635014901/oHJZSQewPOjZR_VxxdxKsGTKenywTsQ4uI9IpMxhwOVKAjHuxrYSCEM3LT5G2OEh7mHj", "vinted_url": "https://www.vinted.de/catalog?search_text=sweater&price_to=20&brand_ids[]=304&brand_ids[]=677891&brand_ids[]=268734&brand_ids[]=5988006&brand_ids[]=7278799&brand_ids[]=7108764&brand_ids[]=7133888&brand_ids[]=88&brand_ids[]=4273&brand_ids[]=430791&brand_ids[]=442625&brand_ids[]=6962946"},
]

def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def process_item(item_url, auftrag, main_driver):
    """Extrahiert Daten aus dem HTML-Quelltext (maximaler Speed)"""
    try:
        main_driver.execute_script(f"window.open('{item_url}', '_blank');")
        main_driver.switch_to.window(main_driver.window_handles[-1])
        time.sleep(1.5) # Kurze Ladezeit
        
        html = main_driver.page_source
        
        # Meta-Tags auslesen
        p_match = re.search(r'property="product:price:amount" content="(\d+\.?\d*)"', html)
        preis = float(p_match.group(1)) if p_match else 0.0
        
        i_match = re.search(r'property="og:image" content="(.*?)"', html)
        img_url = i_match.group(1) if i_match else ""

        # Versand & Größe
        v_match = re.search(r'(?:Versand|Shipping).*?(\d+[,.]\d{2})', html)
        versand = float(v_match.group(1).replace(",", ".")) if v_match else DEFAULT_SHIPPING
        
        groesse = "N/A"
        for s in ["XXS", "XS", "S", "M", "L", "XL", "XXL"]:
            if f'content="{s}"' in html or f'>{s}<' in html:
                groesse = s
                break

        if preis > 0:
            # Berechnungen
            gebuehr = round(0.70 + (preis * 0.05), 2)
            total = round(preis + gebuehr + versand, 2)
            
            marktwert = 35.0
            for k, v in MARKET_DATA.items():
                if k in auftrag['name'].lower(): marktwert = v
            profit = round(marktwert - total, 2)

            # Discord Embed (Overlay exakt nach Vorlage)
            webhook = DiscordWebhook(url=auftrag['webhook'], username=BOT_NAME)
            color = '2ecc71' if profit > 0 else 'e74c3c'
            
            embed = DiscordEmbed(title=f"📦 {auftrag['name']}", color=color, url=item_url)
            embed.add_embed_field(name='📏 Größe', value=f"**{groesse}**", inline=True)
            embed.add_embed_field(name='💰 Preis', value=f"{preis}€", inline=True)
            embed.add_embed_field(name='🚚 Versand', value=f"{versand}€", inline=True)
            embed.add_embed_field(name='💳 TOTAL', value=f"**{total}€**", inline=True)
            embed.add_embed_field(name='📈 Profit', value=f"**{profit}€**", inline=True)
            
            if img_url: embed.set_image(url=img_url)
            webhook.add_embed(embed)
            webhook.execute()
            print(f"🔥 HIT: {auftrag['name']} | {preis}€")

    except Exception as e:
        print(f"Fehler bei Item {item_url}: {e}")
    finally:
        if len(main_driver.window_handles) > 1:
            main_driver.close()
            main_driver.switch_to.window(main_driver.window_handles[0])

def scan_task(auftrag):
    driver = create_driver()
    seen_items = set()
    print(f"✅ Scanning: {auftrag['name']}")
    
    while True:
        try:
            driver.get(auftrag['vinted_url'])
            # Hole nur die obersten 3 Artikel
            items = driver.find_elements(By.XPATH, "//div[contains(@class, 'feed-grid__item')]//a")[:3]
            
            for item in items:
                url = item.get_attribute("href")
                if url and "/items/" in url:
                    item_id = url.split("/")[-1].split("-")[0]
                    if item_id not in seen_items:
                        seen_items.add(item_id)
                        process_item(url, auftrag, driver)
            
            time.sleep(2) # Kurze Pause vor nächstem Scan
        except Exception as e:
            print(f"Scanner Fehler ({auftrag['name']}): {e}")
            time.sleep(5)

def start_bot():
    print(f"🚀 {BOT_NAME} GESTARTET")
    for a in SUCH_AUFTRÄGE:
        threading.Thread(target=scan_task, args=(a,), daemon=True).start()
        time.sleep(1) # Staffelstart der Browser
    
    while True:
        time.sleep(10)

if __name__ == "__main__":
    start_bot()
