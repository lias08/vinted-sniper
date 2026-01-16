import time
import re
import threading
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
BOT_NAME = "Costello Ultimate"
DEFAULT_SHIPPING = 4.99 # Sicherheits-Fallback

MARKET_DATA = {
    "ralph lauren": 45.0, "lacoste": 50.0, "nike": 35.0, 
    "stussy": 65.0, "carhartt": 40.0, "stone island": 85.0,
    "pashanim": 40.0, "pasha": 40.0, "sweater": 30.0
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

    # --- GRÖSSE L SPEZIAL ---
    {"name": "Lacoste Polo L (15)", "webhook": "https://discord.com/api/webhooks/1460230213391614076/fwXUTreF8vrgHZei7QFGHkxd_6OgVz-Biq6-aF9Ur4kNRLj7CWWjSX0WEZ6UnrSmH3on", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20polo&price_to=15&size_id[]=3&order=newest_first"},
    {"name": "Lacoste Polo L (25)", "webhook": "https://discord.com/api/webhooks/1460231377122492524/V0yRgLRQRgW3VEf-STsQmWl2xvZNyGWGUDMz5U5RdkTNS9XSo-7QlwLWQrXw3NOx8CML", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20polo&price_from=15&price_to=25&size_id[]=3&order=newest_first"},
    {"name": "Lacoste Polo L (50)", "webhook": "https://discord.com/api/webhooks/1460231479534555137/d5fjuAP9n0lHbbKj4wciZCoz2YE8M379nptE_DykdD8Ap2R1HCTXCo-aNA51yowhOXvJ", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20polo&price_from=25&price_to=50&size_id[]=3&order=newest_first"},
    {"name": "Lacoste Sweater L (15)", "webhook": "https://discord.com/api/webhooks/1460231609063313546/f37W4z19t4zHUnxHaUNhoJr9Eie6gXC39utCuzIh0hN-t-KOhHPSRBly02eJgr81niX-", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20sweater&price_to=15&size_id[]=3&order=newest_first"},
    {"name": "Lacoste Sweater L (25)", "webhook": "https://discord.com/api/webhooks/1460231853557420136/_ya8gGOf6ufguOWY0FegBYLhH4r5_5AJTM39YmSxJaVzK7_KHAsScptlY2L1jCvKXqIH", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20sweater&price_from=15&price_to=25&size_id[]=3&order=newest_first"},
    {"name": "Lacoste Sweater L (50)", "webhook": "https://discord.com/api/webhooks/1460231900864970764/jL0Xb9SnS2ckRkuEO2eF0u9i-euMbM1XPUow4D_BNkizA7nuyUzXG0x2FDbQXXJdjx9R", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20sweater&price_from=25&price_to=50&size_id[]=3&order=newest_first"},
    {"name": "Lacoste Jacke L (15)", "webhook": "https://discord.com/api/webhooks/1460231948281708604/tgzyns8kkKcUvFZsjpdlg-1Np7l71rmOVjPxehg1QyQQQQH9dIZ6u2HCmQgd271dS_Wz", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20jacke&price_to=15&size_id[]=3&order=newest_first"},
    {"name": "Lacoste Jacke L (25)", "webhook": "https://discord.com/api/webhooks/1460231996499431579/rXsMfS4mhbG_Xgl2Bhv7R1vld0-ykVRkIAJpPXx6rdQ-F4mrMIHCW3q00xoXq9RMtf76", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20jacke&price_from=15&price_to=25&size_id[]=3&order=newest_first"},
    {"name": "Lacoste Jacke L (50)", "webhook": "https://discord.com/api/webhooks/1460232045434372197/jD1UrmqGjHYDIksQ-btzVmp426O3Js8PwApMRfrkKqw7dx-uXBCK7lVb4IDlI18crCl3", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20jacke&price_from=25&price_to=50&size_id[]=3&order=newest_first"},
    {"name": "RL Polo L (15)", "webhook": "https://discord.com/api/webhooks/1460232479578525697/oGUDeFr969o5ozHrvUck5D1pHYhSE64H_odbLGUlwaA-59_K3wLaaP6BEYzu87uhQ4lI", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20polo&price_to=15&size_id[]=3&order=newest_first"},
    {"name": "RL Polo L (25)", "webhook": "https://discord.com/api/webhooks/1460232531051024579/NKEGevZyMp39nYhDAB3i0DxByNmNt1py6kwW7uveYM6xYugRgjXUeSZQOzQnIAh7E8C0", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20polo&price_from=15&price_to=25&size_id[]=3&order=newest_first"},
    {"name": "RL Polo L (50)", "webhook": "https://discord.com/api/webhooks/1460232568862539941/ZY7G88K9iIgD9JFiupi5DHwF4aWGfQbqzt-s9RGGgXvRVPZwvhf1uNqf3lS9C_HYwOVC", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20polo&price_from=25&price_to=50&size_id[]=3&order=newest_first"},
    {"name": "RL Sweater L (15)", "webhook": "https://discord.com/api/webhooks/1460232606904750220/undtlDXfK0wvbyFl69prPUPyk1zFJ1RpaN4k6_GAApHnfueJVDS8T8HlxypKwP-_st5s", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20sweater&price_to=15&size_id[]=3&order=newest_first"},
    {"name": "RL Sweater L (25)", "webhook": "https://discord.com/api/webhooks/1460232651884462164/7C0gmbftXzYURKMZ6E-zdmMiIRlLxz2955885cF7FtXaezzanBq-cOaRQxP6FDzX3xX7", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20sweater&price_from=15&price_to=25&size_id[]=3&order=newest_first"},
    {"name": "RL Sweater L (50)", "webhook": "https://discord.com/api/webhooks/1460232690681774140/EGdCPW-iS-vzcvVpRE39hCl8ic8y7mG-_Baz0NGmvwNWEo8oBpGQwLMJ3pNEaEML4Wwd", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20sweater&price_from=25&price_to=50&size_id[]=3&order=newest_first"},
    {"name": "Nike Tracksuit L (15)", "webhook": "https://discord.com/api/webhooks/1460232732285206693/CYIxaI-nko9V5nN-vtJfFAIzaf9JEf8cQ-EXJxu1Bi2tu-LoWbLS3tQE3QgQz9MT6n7I", "vinted_url": "https://www.vinted.de/catalog?search_text=nike%20tracksuit&price_to=15&size_id[]=3&order=newest_first"},
    {"name": "Nike Tracksuit L (25)", "webhook": "https://discord.com/api/webhooks/1460232773230006434/h9R2bRmJ65D5mOG94EXsYNiS2tF-H9swArAXMpVAbnaEJ26zRA8CiINTxEa7V7a1vSoY", "vinted_url": "https://www.vinted.de/catalog?search_text=nike%20tracksuit&price_from=15&price_to=25&size_id[]=3&order=newest_first"},
    {"name": "Nike Tracksuit L (50)", "webhook": "https://discord.com/api/webhooks/1460232814648623176/DIQDbWT2n_WxxFHUXJ9C6BgOdXVgxkTLmxvAQh4I6BRj2ZaK_xNbw01BQIL11OwBNadx", "vinted_url": "https://www.vinted.de/catalog?search_text=nike%20tracksuit&price_from=25&price_to=50&size_id[]=3&order=newest_first"}
]

def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    # WICHTIG: User-Agent setzen, damit Vinted uns nicht sofort blockt
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def extract_price_from_meta(driver):
    """Liest den Preis aus den versteckten Meta-Daten, nicht vom Bildschirm"""
    try:
        # Versuch 1: Meta Product Price
        elem = driver.find_element(By.XPATH, "//meta[@property='product:price:amount']")
        return float(elem.get_attribute("content"))
    except:
        pass
        
    try:
        # Versuch 2: JSON Script Data (Regex im HTML Quelltext)
        html = driver.page_source
        match = re.search(r'"price_numeric":\s*"(\d+[.,]?\d*)"', html)
        if match:
            return float(match.group(1).replace(",", "."))
    except:
        pass

    # Fallback: Body Text Suche
    try:
        text = driver.find_element(By.TAG_NAME, "body").text
        # Suche nach "15,00 €" Muster
        match = re.search(r'(\d+[,.]\d{2})\s?€', text)
        if match:
             return float(match.group(1).replace(",", "."))
    except:
        pass
        
    return 0.0

def extract_shipping(driver):
    """Versucht Versandkosten intelligent zu finden"""
    try:
        # Suche nach Texten, die "Versand" enthalten und eine Zahl haben
        body_text = driver.find_element(By.TAG_NAME, "body").text
        # Suche nach Zeilen wie "Versand ab 3,99 €" oder "Versand: 2.50 €"
        matches = re.findall(r'(?:Versand|Shipping).*?(\d+[,.]\d{2})', body_text, re.IGNORECASE)
        if matches:
            # Nimm den ersten gefundenen Wert
            return float(matches[0].replace(",", "."))
    except: pass
    
    return DEFAULT_SHIPPING

def scan_task(auftrag):
    driver = create_driver()
    seen_items = set()
    print(f"🔍 Starte: {auftrag['name']}")

    while True:
        try:
            driver.get(auftrag['vinted_url'])
            # Warte kurz, dass Feed lädt
            time.sleep(3) 
            
            items = driver.find_elements(By.XPATH, "//div[contains(@class, 'feed-grid__item')]//a")
            # Filtere leere Links raus
            valid_items = [i.get_attribute("href") for i in items if i.get_attribute("href") and "/items/" in i.get_attribute("href")]

            # Nur die ersten 3 prüfen (Speed!)
            for url in valid_items[:3]:
                item_id = url.split("/")[-1].split("-")[0]
                if item_id in seen_items: continue
                seen_items.add(item_id)

                print(f"👀 Prüfe Details: {url}")
                try:
                    driver.get(url)
                    time.sleep(2) # Seite laden lassen
                    
                    # --- DATEN AUSLESEN (Neue Methode) ---
                    preis = extract_price_from_meta(driver)
                    
                    if preis == 0.0:
                        print(f"❌ Kein Preis gefunden für {url} (Vinted Block?)")
                        continue

                    versand = extract_shipping(driver)
                    
                    # Größe aus Titel/Beschreibung raten
                    page_title = driver.title
                    groesse = "N/A"
                    for s in ["XXS", "XS", "S", "M", "L", "XL", "XXL", "3XL"]:
                        if f" {s} " in page_title or f"/{s} " in page_title:
                            groesse = s
                            break
                    
                    # Rechnung
                    gebuehr = round(0.70 + (preis * 0.05), 2)
                    total = round(preis + gebuehr + versand, 2)
                    
                    marktwert = 25.0
                    for brand, val in MARKET_DATA.items():
                        if brand.lower() in auftrag['name'].lower():
                            marktwert = val
                            break
                    
                    profit = round(marktwert - total, 2)
                    
                    # Bild
                    img_url = ""
                    try:
                        # Meta Image ist meist höher aufgelöst
                        img_elem = driver.find_element(By.XPATH, "//meta[@property='og:image']")
                        img_url = img_elem.get_attribute("content")
                    except: pass

                    # Discord
                    webhook = DiscordWebhook(url=auftrag['webhook'], username=BOT_NAME)
                    color = '2ecc71' if profit > 5 else 'e74c3c'
                    
                    embed = DiscordEmbed(title=f"📦 {auftrag['name']}", color=color, url=url)
                    embed.add_embed_field(name='📏 Größe', value=f"**{groesse}**", inline=True)
                    embed.add_embed_field(name='💰 Preis', value=f"{preis}€", inline=True)
                    embed.add_embed_field(name='🚚 Versand', value=f"{versand}€", inline=True)
                    embed.add_embed_field(name='💳 TOTAL', value=f"**{total}€**", inline=True)
                    embed.add_embed_field(name='📈 Profit', value=f"**{profit}€**", inline=True)
                    
                    if img_url: embed.set_image(url=img_url)

                    webhook.add_embed(embed)
                    webhook.execute()
                    print(f"✅ Gesendet: {preis}€")

                except Exception as e:
                    print(f"Fehler bei Einzel-Item: {e}")
                    continue

        except Exception as e:
            print(f"⚠️ Haupt-Loop Fehler in {auftrag['name']}: {e}")
            try: driver.quit()
            except: pass
            driver = create_driver()
            time.sleep(10)

def start_bot():
    print("🔥 COSTELLO META-SNIPER GESTARTET")
    threads = []
    for a in SUCH_AUFTRÄGE:
        t = threading.Thread(target=scan_task, args=(a,))
        t.daemon = True
        t.start()
        threads.append(t)
        time.sleep(2) 

    while True:
        time.sleep(10)

if __name__ == "__main__":
    start_bot()
