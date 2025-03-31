import csv
import random
import time
import signal
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio

all_urls = []

def save_to_csv(data, filename="phishing_urls.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['url'])  
        for url in data:
            writer.writerow([url])

def stop_gracefully(signum, frame):
    print("\nПрограмма завершена. Сохранение данных...")
    save_to_csv(all_urls)
    exit(0)

async def bypass_cloudflare(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  
            args=['--no-sandbox', '--disable-setuid-sandbox'] 
        )
        page = await browser.new_page()

        try:
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
            })

            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_load_state('load', timeout=60000)

            await page.mouse.wheel(0, 1000)  
            time.sleep(random.uniform(2, 5))  
            page_content = await page.content()
            await browser.close()
            print(f"Загружена страница: {url}")
            return page_content
        except Exception as e:
            print(f"Ошибка при загрузке страницы: {e}")
            await browser.close()
            return None

def extract_phishing_ids(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a', href=True)
    phishing_ids = []
    for link in links:
        href = link['href']
        if 'phish_detail.php?phish_id=' in href:
            phishing_ids.append(href.split('=')[-1])
    return phishing_ids

async def get_phishing_url(phish_id):
    phish_url = f"https://phishtank.org/phish_detail.php?phish_id={phish_id}"
    page_content = await bypass_cloudflare(phish_url)
    if page_content:
        soup = BeautifulSoup(page_content, 'html.parser')
        full_url_tag = soup.find('a', {'target': '_blank'})
        if full_url_tag:
            return full_url_tag.get('href')
    return None

async def scrape_all_pages(start_url):
    base_url = "https://phishtank.org/phish_search.php"
    page_url = start_url

    while page_url:
        page_content = await bypass_cloudflare(page_url)
        if page_content:
            phishing_ids = extract_phishing_ids(page_content)

            for phish_id in phishing_ids:
                full_url = await get_phishing_url(phish_id)
                if full_url:
                    all_urls.append(full_url)

            soup = BeautifulSoup(page_content, 'html.parser')
            next_page = soup.find('a', string='Older >') 
            if next_page:
                relative_url = next_page['href']
                if relative_url.startswith('?'):
                    page_url = f"{base_url}{relative_url}"
                else:
                    page_url = relative_url
            else:
                print("Все страницы обработаны.")
                break
        else:
            print("Ошибка загрузки страницы. Завершаю парсинг.")
            break

        time.sleep(random.randint(1, 3)) 

if __name__ == "__main__":
    signal.signal(signal.SIGINT, stop_gracefully)

    try:
        start_url = input("Введите ссылку первой страницы: ")
        asyncio.run(scrape_all_pages(start_url))

        if all_urls:
            save_to_csv(all_urls)
            print("Данные сохранены в файл phishing_urls.csv")
        else:
            print("Не найдено фишинговых ссылок.")
    except KeyboardInterrupt:
        print("\nПарсинг остановлен.")
        print("Данные сохранены в промежуточный файл.")
