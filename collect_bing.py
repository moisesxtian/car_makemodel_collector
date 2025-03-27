from bing_image_downloader import downloader
from PIL import Image
import imagehash
import os
import shutil


car_data = {
    "Toyota": ["RAV4", "HiAce", "Land Cruiser", "LiteAce", "Raize", "GR Yaris", "GR Supra", "Alphard", "Coaster", "Corolla Cross", 
               "Veloz", "Yaris Cross", "Tamaraw"],
    "Mitsubishi": ["Mirage", "Mirage G4", "Montero Sport", "Strada", "Xpander", "L300", "Outlander PHEV", "Adventure"],
    
    "Ford": ["Ranger", "Everest", "Explorer", "Mustang", "Territory", "EcoSport", "F-150", "Transit"],
    
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
    
    "BAIC": ["MZ40", "M60", "X55", "BJ40"],
    
    "JAC": ["S3", "S4", "S7", "X200"],
    
    "Jetour": ["X70", "Dashing", "Ice Cream EV"],
    
    "Maxus": ["G50", "G10", "D60", "T60", "V80"],
    
    "Volkswagen": ["Santana", "Lavida", "Lamando", "T-Cross", "Multivan Kombi"],
    
    "Peugeot": ["3008", "5008", "2008", "Traveller"],
    
    "Lexus": ["RX", "NX", "UX", "IS", "ES", "LS", "LX", "GX"],
    
    "BMW": ["X1", "X3", "X5", "X7", "3 Series", "5 Series", "7 Series", "Z4", "M4"],
    
    "Mercedes-Benz": ["A-Class", "C-Class", "E-Class", "S-Class", "GLA", "GLC", "GLE", "Vito"],
    
    "Audi": ["A3", "A4", "A6", "Q3", "Q5", "Q7", "Q8"],
    
    "Porsche": ["Macan", "Cayenne", "911", "Panamera", "Taycan"],
    
    "Tesla": ["Model 3", "Model S", "Model X", "Model Y"]
}
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

def compress_image(image_path, target_size_kb=100, initial_quality=85, min_quality=10, quality_step=5):
    """
    Compress the image at image_path to ensure its size does not exceed target_size_kb.
    The function adjusts the quality iteratively to achieve the desired file size.
    """
    try:
        # Open the image
        img = Image.open(image_path)
        # Get the original image size in KB
        original_size_kb = os.path.getsize(image_path) / 1024
        # If the image is already within the target size, no need to compress
        if original_size_kb <= target_size_kb:
            print(f"{image_path} is already under {target_size_kb} KB")
            return
        # Initialize variables
        quality = initial_quality
        compressed = False
        while quality >= min_quality and not compressed:
            # Save the image with the current quality setting
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            # Check the size of the compressed image
            compressed_size_kb = os.path.getsize(image_path) / 1024
            if compressed_size_kb <= target_size_kb:
                compressed = True
                print(f"Compressed {image_path} to {compressed_size_kb:.2f} KB with quality={quality}")
            else:
                # Reduce quality for the next iteration
                quality -= quality_step
        if not compressed:
            print(f"Could not compress {image_path} to under {target_size_kb} KB; minimum quality reached.")
    except Exception as e:
        print(f"Error compressing image {image_path}: {e}")

def download_car_images(make, model, num_images=100, save_path='scraped_dataset'):
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

            downloader.download(query, limit=num_images, output_dir=temp_dir, adult_filter_off=True, force_replace=False, timeout=60, verbose=True)

            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file.lower().endswith(('.jpg', '.png', '.jpeg')):
                        src_path = os.path.join(root, file)
                        if not is_duplicate(src_path, hash_dict):
                            dst_path = os.path.join(final_folder, f"{orientation}_{year}_{file}")
                            shutil.move(src_path, dst_path)
                            compress_image(dst_path)  # Compress the image after moving
                        else:
                            os.remove(src_path)
            shutil.rmtree(temp_dir)

    print(f"\nDownload complete for {make} {model}!\n")
for make, models in car_data.items():
    for model in models:
        download_car_images(make, model, num_images=40, save_path='scraped_dataset')

