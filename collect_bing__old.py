from bing_image_downloader import downloader
from PIL import Image
import imagehash
import os
import shutil


car_data = {
    "Ford": ["Territory", "EcoSport", "F-150", "Transit"],
    
    "Honda": ["City", "Civic", "BR-V", "CR-V", "HR-V", "Accord", "Jazz", "Brio", "Mobilio", "Pilot", "Odyssey"],
    
    "Nissan": ["Almera", "Navara", "Terra", "Patrol", "X-Trail", "Juke", "GT-R", "Leaf", "Kicks e-POWER", "Livina", 
               "Urvan", "Sylphy", "Sentra", "Frontier"],
    
    "Hyundai": ["Accent", "Tucson", "Santa Fe", "Starex", "Kona", "Venue", "Palisade", "Ioniq", "Stargazer", "Stargazer X", 
                "Creta", "Elantra", "Porter", "Grand Starex"],
    
    "Mazda": ["Mazda2", "Mazda3", "CX-3", "CX-30", "CX-5", "CX-8", "CX-9", "MX-5", "BT-50", "CX-60", "CX-90"],
    
    "Suzuki": ["Alto", "Celerio", "Swift", "Dzire", "Ertiga", "Vitara", "Jimny", "S-Presso", "XL7", "Carry", "APV", "Ciaz"],
    
    "Chevrolet": ["Spark", "Sail", "Trax", "Trailblazer", "Colorado", "Suburban", "Camaro", "Tahoe", "Captiva", "Orlando"],
    
    "Kia": ["Picanto", "Rio", "Soluto", "Seltos", "Sportage", "Sorento", "Carnival", "Stonic", "K2500", "Sonet", "EV6"],
    
    "Isuzu": ["D-Max", "mu-X", "Traviz", "N-Series", "F-Series", "C&E-Series", "Crosswind"],
    
    "Subaru": ["Impreza", "XV", "Forester", "Outback", "WRX", "BRZ", "Evoltis"],
    
    "Foton": ["Gratour", "Thunder", "Toplander", "Toano", "View TransVan", "Harabas", "GTL"],
    
    "Chery": ["Tiggo 2", "Tiggo 5X", "Tiggo 7 Pro", "Tiggo 8 Pro", "Arrizo 5", "Arrizo 6"],
    
    "Geely": ["Coolray", "Azkarra", "Okavango", "Emgrand", "Monjaro"],
    
    "MG": ["MG 3", "MG 5", "MG 6", "ZS", "HS", "RX5", "One"],
}

def is_duplicate(img_path, hash_dict):
    """
    Check if the image at img_path is a duplicate based on average hash.
    If duplicate, return True; otherwise, add the hash to hash_dict and return False.
    """
    try:
        img = Image.open(img_path)
        img_hash = imagehash.average_hash(img)
        img.close()
    except Exception as e:
        print(f"Error processing image {img_path}: {e}")
        return True  # Skip images that cannot be processed
    
    if img_hash in hash_dict:
        return True
    hash_dict[img_hash] = img_path
    return False

def compress_image(image_path, target_size_kb=100, initial_quality=85, min_quality=10, quality_step=5):
    """
    Compress the image at image_path to ensure its size does not exceed target_size_kb.
    The function adjusts the quality iteratively to achieve the desired file size.
    """
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")  # Ensure compatibility with JPEG format
        original_size_kb = os.path.getsize(image_path) / 1024
        
        if original_size_kb <= target_size_kb:
            print(f"{image_path} is already under {target_size_kb} KB")
            return
        
        quality = initial_quality
        while quality >= min_quality:
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            compressed_size_kb = os.path.getsize(image_path) / 1024
            if compressed_size_kb <= target_size_kb:
                print(f"Compressed {image_path} to {compressed_size_kb:.2f} KB with quality={quality}")
                break
            quality -= quality_step
        
        img.close()
        
    except Exception as e:
        print(f"Error compressing image {image_path}: {e}")

def download_car_images(make, model, num_images=17, save_path='scraped_dataset'):
    orientations = ['front', 'side', 'back']
    years = [2016, 2018, 2020, 2022, 2024, 2025]
    
    final_folder = os.path.join(save_path, f"{make.lower()}_{model.lower()}")
    os.makedirs(final_folder, exist_ok=True)
    
    hash_dict = {}
    
    for orientation in orientations:
        for year in years:
            query = f"{make} {model} {year} {orientation} view car -sidemirror -accessories -interior"
            temp_dir = os.path.join(save_path, 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            try:
                downloader.download(query, limit=num_images, output_dir=temp_dir, adult_filter_off=True, force_replace=False, timeout=60, verbose=True)
            except Exception as e:
                print(f"Error downloading images for {query}: {e}")
                continue
            
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file.lower().endswith(('.jpg', '.png', '.jpeg')):
                        src_path = os.path.join(root, file)
                        dst_path = os.path.join(final_folder, f"{orientation}_{year}_{file}")
                        
                        if not is_duplicate(src_path, hash_dict):
                            shutil.move(src_path, dst_path)
                            compress_image(dst_path)  # Compress the image after moving
                        else:
                            os.remove(src_path)
            
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    print(f"\nDownload complete for {make} {model}!\n")
for make, models in car_data.items():
    for model in models:
        download_car_images(make, model, num_images=40, save_path='scraped_dataset')

