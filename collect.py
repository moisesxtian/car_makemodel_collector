from icrawler.builtin import GoogleImageCrawler
from PIL import Image
import imagehash
import os
import shutil
import time

def is_duplicate(img_path, hash_dict):
    """
    Check if the image at img_path is a duplicate based on average hash.
    If duplicate, return True; otherwise, add the hash to hash_dict and return False.
    """
    try:
        img = Image.open(img_path)
        img_hash = imagehash.average_hash(img)
    except Exception as e:
        print(f"Error processing image {img_path}: {e}")
        return True  # Skip images that cannot be processed
    if img_hash in hash_dict:
        return True
    hash_dict[img_hash] = img_path
    return False

def compress_image(img_path, max_size_kb=100):
    """
    Compress the image at img_path to ensure its size is under max_size_kb.
    """
    try:
        img = Image.open(img_path)
        img_format = img.format  # Preserve the original image format
        quality = 95  # Start with high quality
        while True:
            img.save(img_path, format=img_format, quality=quality, optimize=True)
            if os.path.getsize(img_path) <= max_size_kb * 1024 or quality <= 10:
                break
            quality -= 5
    except Exception as e:
        print(f"Error compressing image {img_path}: {e}")

def download_car_images(make, model, num_images=17, save_path='scraped_dataset'):
    orientations = ['front', 'side', 'back']
    years = [2016, 2018, 2020, 2022, 2024, 2025]

    final_folder = os.path.join(save_path, f"{make.lower()}_{model.lower()}")
    os.makedirs(final_folder, exist_ok=True)

    hash_dict = {}

    for orientation in orientations:
        for year in years:
            query = f"{make} {model} {year} {orientation} view car -sidemirror -accessories -interior"
            print(f"\nDownloading {num_images} images for '{query}'...")

            temp_dir = os.path.join(save_path, 'temp')
            os.makedirs(temp_dir, exist_ok=True)

            crawler = GoogleImageCrawler(
                storage={'root_dir': temp_dir},
                feeder_threads=1,
                parser_threads=1,
                downloader_threads=1  # Set to 1 to control download rate
            )

            try:
                crawler.crawl(
                    keyword=query,
                    max_num=num_images,
                    min_size=(500, 500)
                )
            except Exception as e:
                print(f"Error while crawling images for '{query}': {e}")
                shutil.rmtree(temp_dir)
                continue  # Skip to the next query

            downloaded_files = [f for f in os.listdir(temp_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]

            if not downloaded_files:
                print(f"No images found for '{query}'. Skipping...")
                shutil.rmtree(temp_dir)
                continue  # Skip to the next query

            for file in downloaded_files:
                src_path = os.path.join(temp_dir, file)
                if not is_duplicate(src_path, hash_dict):
                    compress_image(src_path)  # Compress the image
                    dst_path = os.path.join(final_folder, f"{orientation}_{year}_{file}")
                    shutil.move(src_path, dst_path)
                else:
                    os.remove(src_path)
            
            shutil.rmtree(temp_dir)
            time.sleep(3)  # Implement a delay between requests to avoid rate limiting

    print(f"\nDownload complete for {make} {model}!\n")

# Car dataset (example subset; extend as needed)
car_data = {
    "Lexus": ["LS", "LX", "GX"],
    
    "BMW": ["X1", "X3", "X5", "X7", "3 Series", "5 Series", "7 Series", "Z4", "M4"],
    # Add more makes and models as needed
}

# Run the downloader for each car make and model.
for make, models in car_data.items():
    for model in models:
        download_car_images(make, model, num_images=20, save_path='scraped_dataset_2')
