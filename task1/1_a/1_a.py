import os
import time
import csv
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
from PIL import Image
from io import BytesIO

# Configure Selenium WebDriver
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--log-level=3")  # Reduce logging verbosity
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent bot detection
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    chrome_driver_path = "D:\\Code\\ChromeDriver-134\\chromedriver-win64\\chromedriver.exe"  # Update path
    service = Service(chrome_driver_path)
    return webdriver.Chrome(service=service, options=chrome_options)

# Initialize driver
driver = setup_driver()

# Image categories to search
categories = [
    "Mountain", "River", "Desert", "Forest", "Waterfall",
    "Sunset", "Rainbow", "Galaxy", "Volcano", "Aurora",
    "Castle", "Bridge", "Train", "Airplane", "Car",
    "Bicycle", "Robot", "Drone", "Astronaut", "Satellite"
]

# Create image storage folder
image_dir = "images2"
os.makedirs(image_dir, exist_ok=True)

# CSV metadata file setup
metadata_file = "image_metadata.csv"
with open(metadata_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Category", "Filename", "URL", "Resolution"])  # Write CSV header

# Function to download images and store metadata
def download_image(url, folder, img_name, category):
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            resolution = f"{image.width}x{image.height}"
            file_path = os.path.join(folder, f"{img_name}.jpg")
            image.convert("RGB").save(file_path, "JPEG")  # Convert if not in RGB mode

            # Save metadata
            with open(metadata_file, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([category, f"{img_name}.jpg", url, resolution])
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")

# Function to fetch image URLs from Google Images
def fetch_image_urls(query, max_images=50):
    search_url = f"https://www.google.com/search?q={query}&tbm=isch"
    driver.get(search_url)
    time.sleep(2)  # Allow page to load

    urls = set()
    last_height = driver.execute_script("return document.body.scrollHeight")

    while len(urls) < max_images:
        images = driver.find_elements(By.CSS_SELECTOR, "img")
        
        for img in images:
            try:
                src = img.get_attribute("data-src") or img.get_attribute("src")
                if src and src.startswith("http") and src not in urls:
                    urls.add(src)
                if len(urls) >= max_images:
                    break
            except Exception:
                continue  # Ignore errors

        # Scroll down
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")

        # Break if no new content is loaded
        if new_height == last_height:
            break
        last_height = new_height

        # Try clicking "Show more results" if available
        try:
            show_more = driver.find_element(By.CSS_SELECTOR, "input[value='Show more results']")
            show_more.click()
            time.sleep(2)
        except:
            pass  # Continue scrolling if the button is not found

    return list(urls)[:max_images]  # Ensure we return exactly 50 images

# Main loop to fetch and download images for each category
for category in categories:
    print(f"📷 Downloading images for {category}...")
    category_folder = os.path.join(image_dir, category.replace(" ", "_"))
    os.makedirs(category_folder, exist_ok=True)

    retries = 0
    image_urls = fetch_image_urls(category, max_images=50)

    while len(image_urls) < 50 and retries < 3:
        print(f"🔄 Retrying {category}... Attempt {retries + 1}")
        time.sleep(5)
        image_urls = fetch_image_urls(category, max_images=50)
        retries += 1

    if len(image_urls) < 50:
        print(f"⚠️ Warning: Only {len(image_urls)} images found for {category}.")

    for idx, img_url in tqdm(enumerate(image_urls), total=len(image_urls), desc=f"Saving {category} images"):
        download_image(img_url, category_folder, f"{category}_{idx}", category)

# Close WebDriver
driver.quit()
print("✅ Image downloading complete! Metadata saved in 'image_metadata.csv'.")
