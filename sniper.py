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

# Liste erweitert um gängige Formate

VALID_SIZES = ["XXS", "XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL", 

               "34", "36", "38", "40", "42", "44", "46", "48", "50", 

               "W30", "W32", "W34", "W36"]



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

    # --- LACOSTE POLOS (Größe L) ---

    {"name": "Lacoste Polo L (15)", "webhook": "https://discord.com/api/webhooks/1460230213391614076/fwXUTreF8vrgHZei7QFGHkxd_6OgVz-Biq6-aF9Ur4kNRLj7CWWjSX0WEZ6UnrSmH3on", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20polo&price_to=15&size_id[]=3&order=newest_first"},

    {"name": "Lacoste Polo L (25)", "webhook": "https://discord.com/api/webhooks/1460231377122492524/V0yRgLRQRgW3VEf-STsQmWl2xvZNyGWGUDMz5U5RdkTNS9XSo-7QlwLWQrXw3NOx8CML", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20polo&price_from=15&price_to=25&size_id[]=3&order=newest_first"},

    {"name": "Lacoste Polo L (50)", "webhook": "https://discord.com/api/webhooks/1460231479534555137/d5fjuAP9n0lHbbKj4wciZCoz2YE8M379nptE_DykdD8Ap2R1HCTXCo-aNA51yowhOXvJ", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20polo&price_from=25&price_to=50&size_id[]=3&order=newest_first"},



    # --- LACOSTE SWEATER (Größe L) ---

    {"name": "Lacoste Sweater L (15)", "webhook": "https://discord.com/api/webhooks/1460231609063313546/f37W4z19t4zHUnxHaUNhoJr9Eie6gXC39utCuzIh0hN-t-KOhHPSRBly02eJgr81niX-", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20sweater&price_to=15&size_id[]=3&order=newest_first"},

    {"name": "Lacoste Sweater L (25)", "webhook": "https://discord.com/api/webhooks/1460231853557420136/_ya8gGOf6ufguOWY0FegBYLhH4r5_5AJTM39YmSxJaVzK7_KHAsScptlY2L1jCvKXqIH", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20sweater&price_from=15&price_to=25&size_id[]=3&order=newest_first"},

    {"name": "Lacoste Sweater L (50)", "webhook": "https://discord.com/api/webhooks/1460231900864970764/jL0Xb9SnS2ckRkuEO2eF0u9i-euMbM1XPUow4D_BNkizA7nuyUzXG0x2FDbQXXJdjx9R", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20sweater&price_from=25&price_to=50&size_id[]=3&order=newest_first"},



    # --- LACOSTE JACKEN (Größe L) ---

    {"name": "Lacoste Jacke L (15)", "webhook": "https://discord.com/api/webhooks/1460231948281708604/tgzyns8kkKcUvFZsjpdlg-1Np7l71rmOVjPxehg1QyQQQQH9dIZ6u2HCmQgd271dS_Wz", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20jacke&price_to=15&size_id[]=3&order=newest_first"},

    {"name": "Lacoste Jacke L (25)", "webhook": "https://discord.com/api/webhooks/1460231996499431579/rXsMfS4mhbG_Xgl2Bhv7R1vld0-ykVRkIAJpPXx6rdQ-F4mrMIHCW3q00xoXq9RMtf76", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20jacke&price_from=15&price_to=25&size_id[]=3&order=newest_first"},

    {"name": "Lacoste Jacke L (50)", "webhook": "https://discord.com/api/webhooks/1460232045434372197/jD1UrmqGjHYDIksQ-btzVmp426O3Js8PwApMRfrkKqw7dx-uXBCK7lVb4IDlI18crCl3", "vinted_url": "https://www.vinted.de/catalog?search_text=lacoste%20jacke&price_from=25&price_to=50&size_id[]=3&order=newest_first"},



    # --- RALPH LAUREN POLOS (Größe L) ---

    {"name": "RL Polo L (15)", "webhook": "https://discord.com/api/webhooks/1460232479578525697/oGUDeFr969o5ozHrvUck5D1pHYhSE64H_odbLGUlwaA-59_K3wLaaP6BEYzu87uhQ4lI", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20polo&price_to=15&size_id[]=3&order=newest_first"},

    {"name": "RL Polo L (25)", "webhook": "https://discord.com/api/webhooks/1460232531051024579/NKEGevZyMp39nYhDAB3i0DxByNmNt1py6kwW7uveYM6xYugRgjXUeSZQOzQnIAh7E8C0", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20polo&price_from=15&price_to=25&size_id[]=3&order=newest_first"},

    {"name": "RL Polo L (50)", "webhook": "https://discord.com/api/webhooks/1460232568862539941/ZY7G88K9iIgD9JFiupi5DHwF4aWGfQbqzt-s9RGGgXvRVPZwvhf1uNqf3lS9C_HYwOVC", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20polo&price_from=25&price_to=50&size_id[]=3&order=newest_first"},



    # --- RALPH LAUREN SWEATER (Größe L) ---

    {"name": "RL Sweater L (15)", "webhook": "https://discord.com/api/webhooks/1460232606904750220/undtlDXfK0wvbyFl69prPUPyk1zFJ1RpaN4k6_GAApHnfueJVDS8T8HlxypKwP-_st5s", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20sweater&price_to=15&size_id[]=3&order=newest_first"},

    {"name": "RL Sweater L (25)", "webhook": "https://discord.com/api/webhooks/1460232651884462164/7C0gmbftXzYURKMZ6E-zdmMiIRlLxz2955885cF7FtXaezzanBq-cOaRQxP6FDzX3xX7", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20sweater&price_from=15&price_to=25&size_id[]=3&order=newest_first"},

    {"name": "RL Sweater L (50)", "webhook": "https://discord.com/api/webhooks/1460232690681774140/EGdCPW-iS-vzcvVpRE39hCl8ic8y7mG-_Baz0NGmvwNWEo8oBpGQwLMJ3pNEaEML4Wwd", "vinted_url": "https://www.vinted.de/catalog?search_text=ralph%20lauren%20sweater&price_from=25&price_to=50&size_id[]=3&order=newest_first"},



    # --- NIKE TRACKSUITS (Größe L) ---

    {"name": "Nike Tracksuit L (15)", "webhook": "https://discord.com/api/webhooks/1460232732285206693/CYIxaI-nko9V5nN-vtJfFAIzaf9JEf8cQ-EXJxu1Bi2tu-LoWbLS3tQE3QgQz9MT6n7I", "vinted_url": "https://www.vinted.de/catalog?search_text=nike%20tracksuit&price_to=15&size_id[]=3&order=newest_first"},

    {"name": "Nike Tracksuit L (25)", "webhook": "https://discord.com/api/webhooks/1460232773230006434/h9R2bRmJ65D5mOG94EXsYNiS2tF-H9swArAXMpVAbnaEJ26zRA8CiINTxEa7V7a1vSoY", "vinted_url": "https://www.vinted.de/catalog?search_text=nike%20tracksuit&price_from=15&price_to=25&size_id[]=3&order=newest_first"},

    {"name": "Nike Tracksuit L (50)", "webhook": "https://discord.com/api/webhooks/1460232814648623176/DIQDbWT2n_WxxFHUXJ9C6BgOdXVgxkTLmxvAQh4I6BRj2ZaK_xNbw01BQIL11OwBNadx", "vinted_url": "https://www.vinted.de/catalog?search_text=nike%20tracksuit&price_from=25&price_to=50&size_id[]=3&order=newest_first"}

]



def create_driver():

    options = Options()

    options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")

    options.add_argument("--disable-dev-shm-usage")

    # Extrem große Auflösung erzwingen, damit Texte nicht überlappen

    options.add_argument("window-size=2560,1440")

    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)



def start_bot():

    driver = create_driver()

    seen_items = set()

    print("🚀 SNIPER V4 - FINAL FIX GESTARTET")



    while True:

        for auftrag in SUCH_AUFTRÄGE:

            try:

                driver.get(auftrag['vinted_url'])

                # Längeres Warten auf Vinted Server

                WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'feed-grid__item')]")))

                items = driver.find_elements(By.XPATH, "//div[contains(@class, 'feed-grid__item')]")



                for item in items[:5]:

                    try:

                        url_elem = item.find_element(By.TAG_NAME, "a")

                        url = url_elem.get_attribute("href")

                        if not url or "items" not in url: continue

                        item_id = url.split("/")[-1].split("-")[0]

                        

                        if item_id in seen_items: continue

                        seen_items.add(item_id)



                        # --- AGGRESSIVE TEXTANALYSE ---

                        # Wir holen uns den gesamten Textblock und zerlegen ihn

                        full_text_block = item.text

                        lines = [line.strip() for line in full_text_block.split('\n') if line.strip()]



                        # Debugging-Ausgabe in die Konsole (für GitHub Logs)

                        print(f"--- Prüfe Item {item_id} ---")

                        print(f"Gefundene Textzeilen: {lines}")



                        artikel_preis = 0.0

                        groesse = "-"

                        versand_preis = DEFAULT_SHIPPING



                        # 1. PREIS FINDEN (Die Zeile mit € aber ohne VERSAND)

                        for line in lines:

                            if "€" in line and "VERSAND" not in line.upper():

                                # Regex sucht nach "Zahl,Zahl"

                                match = re.search(r"(\d+[,.]\d+)", line)

                                if match:

                                    artikel_preis = float(match.group(1).replace(",", "."))

                                    print(f"-> Preis gefunden: {artikel_preis}")

                                    break # Erster Treffer ist meist der richtige



                        # 2. GRÖSSE FINDEN

                        # Strategie A: Exakte Übereinstimmung einer Zeile

                        for line in lines:

                            clean = line.upper().strip()

                            if clean in VALID_SIZES:

                                groesse = clean; break

                        # Strategie B: Wortsuche im gesamten Block (falls Größe mit Marke zusammenklebt)

                        if groesse == "-":

                            full_upper = full_text_block.upper()

                            for s in VALID_SIZES:

                                # Sucht nach Größe umgeben von Leerzeichen oder Slash (z.B. " L " oder "/L")

                                if re.search(rf"(^|\s|/){s}($|\s|/)", full_upper):

                                    groesse = s; break

                        print(f"-> Größe gefunden: {groesse}")



                        # 3. VERSAND FINDEN

                        for line in lines:

                            if "€" in line and "VERSAND" in line.upper():

                                match = re.search(r"(\d+[,.]\d+)", line)

                                if match:

                                    versand_preis = float(match.group(1).replace(",", "."))

                                    break



                        # --- BERECHNUNG & SENDEN ---

                        fee = round(0.70 + (artikel_preis * 0.05), 2)

                        total = round(artikel_preis + fee + versand_preis, 2)

                        

                        marktwert = 20.0

                        for brand, val in MARKET_DATA.items():

                            if brand in url.lower(): marktwert = val; break

                        profit = round(marktwert - total, 2)



                        # Nur senden wenn wir einen Preis haben (verhindert 0.0€ Posts bei Ladefehlern)

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

                            print("✅ Erfolgreich gesendet!")

                        else:

                            print("⚠️ Artikel übersprungen (Preis konnte nicht ermittelt werden)")



                    except Exception as e:

                        print(f"Fehler beim Item: {e}")

                        continue

            except Exception as e:

                print(f"Kritischer Browser-Fehler: {e}")

                driver.quit()

                driver = create_driver()

                break

        time.sleep(5) # Stabilitätspause



if __name__ == "__main__":

    start_bot()
