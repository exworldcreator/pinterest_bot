import os
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import aiohttp

load_dotenv()

my_gmail = os.getenv("MY_GMAIL")
my_password = os.getenv("MY_PASSWORD")

async def login_to_pinterest(page):
    await page.goto('https://www.pinterest.com/login/')

    await page.fill('input[name="id"]', my_gmail)
    await page.fill('input[name="password"]', my_password)
    
    await page.click('button[type="submit"]')
    
    print("Successfully logged in to Pinterest")

async def collect_images(page, num_images=5):
    images = []

    await page.wait_for_selector('img[srcset]')

    image_elements = await page.query_selector_all('img[srcset]')

    for i, img in enumerate(image_elements[:num_images]):
        src = await img.get_attribute('src')
        if src:
            images.append(src)
        if i == num_images - 1:
            break

    print(f"Collected {len(images)} images.")
    return images

async def download_image(images):
    folder = 'downloaded_images'
        
    if not os.path.exists(folder):
        os.makedirs(folder)
        print('Downloaded folder created')
 
    async with aiohttp.ClientSession() as session:
        for i, img_url in enumerate(images):
            try:
                async with session.get(img_url) as response:
                    if response.status == 200:
                        extension = img_url.split('.')[-1]
                        image_name = f"image_{i + 1}.{extension}"
                        
                        image_path = os.path.join(folder, image_name)
                        with open(image_path, 'wb') as file:
                            file.write(await response.read())
                        print(f"File '{image_name}' successfully saved")
                    else:
                        print(f"Failed to download image from {img_url}")
            except Exception as e:
                print(f"Error downloading image {img_url}: {e}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await login_to_pinterest(page)

        images = await collect_images(page, num_images=10)
        
        await download_image(images)

        await browser.close()
