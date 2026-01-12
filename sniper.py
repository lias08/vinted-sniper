import time
import re
import asyncio
import discord
from discord.ext import commands, tasks
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
# HIER DEINEN BOT TOKEN EINFÜGEN (Vom Discord Developer Portal)
BOT_TOKEN = "MTQ1OTgzNjUwNDM4OTE5Mzc3MA.GFPzSu.rU_Z-1xijPDGSY45BSevXnJtbIjw1C5qGxLoHw" 

BOT_NAME = "Costello Sniper by Lias"
DEFAULT_SHIPPING = 3.50 
PREFIX = "!" # Befehlszeichen für Discord

MARKET_DATA = {
    "ralph lauren": 45.0, "lacoste": 50.0, "nike": 35.0, 
    "stussy": 65.0, "carhartt": 40.0, "stone island": 85.0
}

VALID_SIZES = ["XXS", "XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL", 
               "34", "36", "38", "40", "42", "44", "46", "48", "50", 
               "W30", "W32", "W34", "W36"]

# Deine bestehende Liste (Initial-Daten)
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
    {"name": "Lacoste sweater (15)", "webhook": "https://discord.com/api/webhooks/1459971644113293512/1gNG07NG4JuirBZ0FlK_5OtINnzyW4CJM8QeSPcfJdOMp1Fyb81bV_2FLib0D7SJYIlP", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20sweater&price_to=15&order=newest_first"},
    {"name": "Pashanim (15)", "webhook": "https://discord.com/api/webhooks/1460274126315982914/m-Vj7rvBdQ0x-ksVoNw9L21IzYYMVDSvyzhfxszW7_DdHZLTzlj31w2RhuYkzlQtIpSW", "vinted_url": "https://www.vinted.de/catalog?search_text=pashanim&search_id=30242658961&price_to=15&currency=EUR&page=1&time=1768226668&search_by_image_uuid="},
    {"name": "Pasha (15)", "webhook": "https://discord.com/api/webhooks/1460274126315982914/m-Vj7rvBdQ0x-ksVoNw9L21IzYYMVDSvyzhfxszW7_DdHZLTzlj31w2RhuYkzlQtIpSW", "vinted_url": "https://www.vinted.de/catalog?search_text=pasha&search_id=30242686295&price_to=15&currency=EUR&page=1&time=1768226805&search_by_image_uuid="},
    {"name": "Pashanim (25)", "webhook": "https://discord.com/api/webhooks/1460274208675205120/2XgKnQE_aB3TH9jhvJwZ4SpcCN1Y00-xTjd7Dm6yTh3CXIffqGhSmUk8lynAGeAGr0cC", "vinted_url": "https://www.vinted.de/catalog?search_text=pashanim&search_id=30242658961&price_to=25&currency=EUR&page=1&time=1768226668&search_by_image_uuid="},
    {"name": "Pasha (25)", "webhook": "https://discord.com/api/webhooks/1460274208675205120/2XgKnQE_aB3TH9jhvJwZ4SpcCN1Y00-xTjd7Dm6yTh3CXIffqGhSmUk8lynAGeAGr0cC", "vinted_url": "https://www.vinted.de/catalog?search_text=pasha&search_id=30242686295&price_to=25&currency=EUR&page=1&time=1768226805&search_by_image_uuid="},
    {"name": "Pashanim (50)", "webhook": "https://discord.com/api/webhooks/1460274319858073764/gB6Rq-L02mymDD-FiQk7RpU4ZCJUeSI8lv7xYyEzWeIb_H2tHbY79TS62XMHhKdRpUsU", "vinted_url": "https://www.vinted.de/catalog?search_text=pashanim&search_id=30242658961&price_to=50&currency=EUR&page=1&time=1768226668&search_by_image_uuid="},
    {"name": "Pasha (50)", "webhook": "https://discord.com/api/webhooks/1460274319858073764/gB6Rq-L02mymDD-FiQk7RpU4ZCJUeSI8lv7xYyEzWeIb_H2tHbY79TS62XMHhKdRpUsU", "vinted_url": "https://www.vinted.de/catalog?search_text=pasha&search_id=30242686295&price_to=50&currency=EUR&page=1&time=1768226805&search_by_image_uuid="},
    {"name": "Pashanim (50)", "webhook": "https://discord.com/api/webhooks/1460274671911043164/iXA8iLmk8hBdEiuzfD0k8VvugYcV5IlWZHcw2aoOx06YyVifTu5GxZMndLpFNO6iVAiq", "vinted_url": "https://www.vinted.de/catalog?search_by_image_uuid=&search_text=pasha&page=1&search_id=30242831825&time=1768226959"},
    {"name": "Pasha (50)", "webhook": "https://discord.com/api/webhooks/1460274671911043164/iXA8iLmk8hBdEiuzfD0k8VvugYcV5IlWZHcw2aoOx06YyVifTu5GxZMndLpFNO6iVAiq", "vinted_url": "https://www.vinted.de/catalog?search_by_image_uuid=&search_text=pashanim&page=1&search_id=30242848685&time=1768227000"},
    {"name": "swaeater (20)", "webhook": "https://discord.com/api/webhooks/1460300613635014901/oHJZSQewPOjZR_VxxdxKsGTKenywTsQ4uI9IpMxhwOVKAjHuxrYSCEM3LT5G2OEh7mHj", "vinted_url": "https://www.vinted.de/catalog?search_text=sweater&search_id=30245465917&price_to=20&currency=EUR&page=1&time=1768233128&search_by_image_uuid=&brand_ids[]=304&brand_ids[]=677891&brand_ids[]=268734&brand_ids[]=5988006&brand_ids[]=7278799&brand_ids[]=7108764&brand_ids[]=7133888&brand_ids[]=88&brand_ids[]=4273&brand_ids[]=430791&brand_ids[]=442625&brand_ids[]=6962946"},
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

seen_items = set()

# =================================================================
# SETUP DRIVER
# =================================================================
def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=2560,1440")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver = create_driver()

# =================================================================
# DISCORD BOT EVENTS & BEFEHLE
# =================================================================
intents = discord.Intents.default()
intents.message_content = True # Wichtig für Befehle
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Bot eingeloggt als {bot.user.name}")
    print("🚀 Starte Sniper-Loop...")
    if not sniper_loop.is_running():
        sniper_loop.start()

# --- BEFEHL 1: Neuen Channel + Webhook + Suche erstellen ---
# Nutzung: !new "channel-name" "vinted-url"
@bot.command(name="new")
@commands.has_permissions(manage_channels=True, manage_webhooks=True)
async def new_search(ctx, channel_name: str, vinted_url: str):
    try:
        # 1. Channel erstellen
        guild = ctx.guild
        category = ctx.channel.category # Im selben Bereich erstellen wie der Befehl
        new_channel = await guild.create_text_channel(name=channel_name, category=category)
        
        # 2. Webhook erstellen
        webhook = await new_channel.create_webhook(name="Sniper-Hook")
        
        # 3. Zur Liste hinzufügen
        SUCH_AUFTRÄGE.append({
            "name": channel_name,
            "webhook": webhook.url,
            "vinted_url": vinted_url
        })
        
        await ctx.send(f"✅ Kanal {new_channel.mention} erstellt und Suche gestartet!")
        await new_channel.send(f"🔭 **Sniper aktiv** für: {vinted_url}")
        
    except Exception as e:
        await ctx.send(f"❌ Fehler: {e}")

# --- BEFEHL 2: Suche zum aktuellen Channel hinzufügen ---
# Nutzung: !add "Name der Suche" "vinted-url"
@bot.command(name="add")
@commands.has_permissions(manage_webhooks=True)
async def add_search(ctx, name: str, vinted_url: str):
    try:
        # Prüfen ob Webhook existiert, sonst erstellen
        webhooks = await ctx.channel.webhooks()
        if webhooks:
            webhook_url = webhooks[0].url
        else:
            webhook = await ctx.channel.create_webhook(name="Sniper-Hook")
            webhook_url = webhook.url
            
        SUCH_AUFTRÄGE.append({
            "name": name,
            "webhook": webhook_url,
            "vinted_url": vinted_url
        })
        
        await ctx.send(f"✅ Suche **{name}** zu diesem Kanal hinzugefügt!")
        
    except Exception as e:
        await ctx.send(f"❌ Fehler: {e}")

# =================================================================
# SNIPER LOOP (Läuft im Hintergrund)
# =================================================================
@tasks.loop(seconds=5) # Pause zwischen Durchläufen
async def sniper_loop():
    global driver
    # Wir iterieren durch alle Aufträge
    for auftrag in SUCH_AUFTRÄGE:
        try:
            # Selenium ist blockierend, daher müssen wir vorsichtig sein.
            # In einem perfekten Bot würde man das in einen Thread auslagern, 
            # aber für deine Zwecke reicht es so, solange die Vinted-Antwort schnell kommt.
            
            driver.get(auftrag['vinted_url'])
            
            # Kurzer Wait
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'feed-grid__item')]")))
            except:
                continue # Nächster Auftrag wenn nichts lädt

            items = driver.find_elements(By.XPATH, "//div[contains(@class, 'feed-grid__item')]")

            for item in items[:5]:
                try:
                    url_elem = item.find_element(By.TAG_NAME, "a")
                    url = url_elem.get_attribute("href")
                    if not url or "items" not in url: continue
                    
                    item_id = url.split("/")[-1].split("-")[0]
                    if item_id in seen_items: continue
                    seen_items.add(item_id)

                    # --- TEXTANALYSE (Deine Logik) ---
                    full_text_block = item.text
                    lines = [line.strip() for line in full_text_block.split('\n') if line.strip()]

                    artikel_preis = 0.0
                    groesse = "-"
                    versand_preis = DEFAULT_SHIPPING

                    # Preis
                    for line in lines:
                        if "€" in line and "VERSAND" not in line.upper():
                            match = re.search(r"(\d+[,.]\d+)", line)
                            if match:
                                artikel_preis = float(match.group(1).replace(",", "."))
                                break
                    
                    # Größe
                    for line in lines:
                        clean = line.upper().strip()
                        if clean in VALID_SIZES:
                            groesse = clean; break
                    
                    if groesse == "-":
                        full_upper = full_text_block.upper()
                        for s in VALID_SIZES:
                            if re.search(rf"(^|\s|/){s}($|\s|/)", full_upper):
                                groesse = s; break
                    
                    # Versand
                    for line in lines:
                        if "€" in line and "VERSAND" in line.upper():
                            match = re.search(r"(\d+[,.]\d+)", line)
                            if match:
                                versand_preis = float(match.group(1).replace(",", "."))
                                break

                    # Berechnung
                    fee = round(0.70 + (artikel_preis * 0.05), 2)
                    total = round(artikel_preis + fee + versand_preis, 2)
                    
                    marktwert = 20.0
                    for brand, val in MARKET_DATA.items():
                        if brand in url.lower(): marktwert = val; break
                    profit = round(marktwert - total, 2)

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
                        print(f"✅ Gesendet: {auftrag['name']} - {item_id}")

                except Exception as e:
                    continue
            
            # Kleiner Sleep um CPU zu schonen und Event Loop Luft zu geben
            await asyncio.sleep(1) 

        except Exception as e:
            print(f"Loop Fehler: {e}")
            try:
                driver.quit()
                driver = create_driver()
            except: pass

# Bot starten
if __name__ == "__main__":
    bot.run(BOT_TOKEN)
