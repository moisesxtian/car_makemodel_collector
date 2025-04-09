import os
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from bing_image_downloader import downloader
from PIL import Image
import imagehash

# Car dataset
car_data = {
    "Tesla": ["Roadster", "Cybertruck", ""],
}

# Faster hashing for duplicate detection
def is_duplicate(img_path, hash_dict):
    """ Check if an image is a duplicate based on difference hash (dhash). """
    try:
        img = Image.open(img_path)
        img_hash = imagehash.dhash(img)  # Faster than average_hash()
        img.close()
    except Exception:
        return True  # Skip processing if there's an error

    if img_hash in hash_dict:
        return True  # It's a duplicate
    hash_dict[img_hash] = img_path  # Add to the set of unique hashes
    return False

# Optimized image compression
def compress_image(image_path, target_size_kb=100, initial_quality=85):
    """ Compress image while maintaining quality, but skip if it's close to target size. """
    try:
        img = Image.open(image_path).convert("RGB")
        file_size_kb = os.path.getsize(image_path) / 1024

        if file_size_kb <= target_size_kb + 20:  # Skip if it's already close to target
            return
        
        quality = initial_quality
        while quality > 10:
            img.save(image_path, "JPEG", quality=quality, optimize=True)
            if os.path.getsize(image_path) / 1024 <= target_size_kb:
                break
            quality -= 5  # Reduce quality iteratively
        
        img.close()
    except Exception:
        pass

# Function to process and move images in parallel
def process_image(src_path, dst_path, hash_dict):
    """ Move image if it's unique, otherwise delete it. Compress after moving. """
    if not is_duplicate(src_path, hash_dict):
        shutil.move(src_path, dst_path)
        compress_image(dst_path)
    else:
        os.remove(src_path)

# Optimized image scraping function
def download_car_images(make, model, num_images=20, save_path="scraped_dataset"):
    """ Download and process car images for a given make and model. """
    orientations = ["Back", "Rear", "for sale"]
    years = [2018, 2022, 2025]  # Reduced to 3 years for speedup
    
    final_folder = os.path.join(save_path, f"{make.lower()}_{model.lower()}")
    os.makedirs(final_folder, exist_ok=True)
    
    hash_dict = {}
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        for orientation in orientations:
            for year in years:
                query = f"{make} {model} {year} {orientation} view car for -sidemirror -accessories -interior"
                temp_dir = os.path.join(save_path, "temp")
                os.makedirs(temp_dir, exist_ok=True)

                try:
                    downloader.download(query, limit=num_images, output_dir=temp_dir, adult_filter_off=True, 
                                        force_replace=False, timeout=30, verbose=False)
                except Exception as e:
                    print(f"Error downloading images for {query}: {e}")
                    continue
                
                futures = []
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        if file.lower().endswith((".jpg", ".png", ".jpeg")):
                            src_path = os.path.join(root, file)
                            dst_path = os.path.join(final_folder, f"{orientation}_{year}_{file}")
                            futures.append(executor.submit(process_image, src_path, dst_path, hash_dict))

                # Wait for all threads to finish
                for future in futures:
                    future.result()
                
                # Clean up temporary folder
                shutil.rmtree(temp_dir, ignore_errors=True)

    print(f"\n✅ Download complete for {make} {model}!\n")

# Run the optimized scraper
for make, models in car_data.items():
    for model in models:
        download_car_images(make, model, num_images=30, save_path="scraped_dataset")
