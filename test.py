import time
import random
import os
import shutil
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from PIL import Image
import imagehash

# Function to check for duplicate images using average hash
def is_duplicate(img_path, hash_dict):
    try:
        img = Image.open(img_path)
        img_hash = imagehash.average_hash(img)
    except Exception as e:
        print(f"Error processing image {img_path}: {e}")
        return True
    if img_hash in hash_dict:
        return True
    hash_dict[img_hash] = img_path
    return False

# Helper function to download an image from URL
def download_image(url, path):
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return False

# Alternative approach using Selenium for Google Images scraping
def download_car_images_selenium(make, model, num_images=100, save_path='scraped_dataset'):
    orientations = ['front', 'side', 'back']
    years = [2016, 2018, 2020, 2022, 2024, 2025]
    
    final_folder = os.path.join(save_path, f"{make.lower()}_{model.lower()}")
    os.makedirs(final_folder, exist_ok=True)
    hash_dict = {}

    # Set up headless Chrome with a randomized User-Agent
    chrome_options = Options()
    chromedriver_path = './chromedriver.exe'  # Adjust the path as needed
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)  
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    
    # Initialize the webdriver (make sure chromedriver is installed and in your PATH)
    driver = webdriver.Chrome(options=chrome_options)

    for orientation in orientations:
        for year in years:
            query = f"{make} {model} {year} {orientation} view car -sidemirror -accessories -interior"
            print(f"\nSearching for images with query: {query}")
            
            # Navigate to Google Images
            search_url = "https://www.google.com/imghp?hl=en"
            driver.get(search_url)
            time.sleep(random.uniform(2, 4))
            
            # Optional: Accept cookies if prompted
            try:
                agree_button = driver.find_element(By.XPATH, '//button[text()="I agree"]')
                agree_button.click()
                time.sleep(2)
            except Exception:
                pass
            
            # Enter the search query and submit the form
            search_box = driver.find_element(By.NAME, "q")
            search_box.clear()
            search_box.send_keys(query)
            search_box.submit()
            time.sleep(random.uniform(2, 4))
            
            # Scroll to load enough thumbnails
            img_count = 0
            last_height = driver.execute_script("return document.body.scrollHeight")
            while img_count < num_images:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2, 4))
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    try:
                        # Click "Show more results" if available
                        driver.find_element(By.CSS_SELECTOR, ".mye4qd").click()
                    except Exception:
                        print("No more images available.")
                        break
                last_height = new_height
                thumbnails = driver.find_elements(By.CSS_SELECTOR, "img.Q4LuWd")
                img_count = len(thumbnails)
                print(f"Found {img_count} thumbnails...")

            # Download images by clicking on thumbnails
            downloaded = 0
            for thumbnail in thumbnails:
                if downloaded >= num_images:
                    break
                try:
                    thumbnail.click()
                    time.sleep(random.uniform(1, 2))
                    images = driver.find_elements(By.CSS_SELECTOR, "img.n3VNCb")
                    for image in images:
                        src = image.get_attribute("src")
                        if src and "http" in src:
                            file_name = f"{orientation}_{year}_{downloaded}.jpg"
                            file_path = os.path.join(final_folder, file_name)
                            if download_image(src, file_path):
                                if not is_duplicate(file_path, hash_dict):
                                    downloaded += 1
                                    print(f"Downloaded {downloaded} images")
                                else:
                                    os.remove(file_path)
                            break
                except Exception as e:
                    print(f"Error processing thumbnail: {e}")
                    continue
            # Wait before moving to the next query
            time.sleep(random.uniform(5, 15))
    
    driver.quit()
    print(f"\nDownload complete for {make} {model}!\n")

# Example Car Dataset
car_data = {
    "Toyota": ["Vios", "Innova"],
    "Mitsubishi": ["Mirage", "Montero Sport"],
    "Ford": ["Ranger", "Mustang"]
}

# Run the downloader using the Selenium approach
for make, models in car_data.items():
    for model in models:
        download_car_images_selenium(make, model, num_images=40, save_path='scraped_dataset')
