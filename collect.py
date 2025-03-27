from icrawler.builtin import GoogleImageCrawler
from PIL import Image
import imagehash
import os
import shutil

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

def download_car_images(make, model, num_images=40, save_path='scrape_dataset_2'):
    orientations = ['front', 'side', 'back']
    # List of years to vary the query
    years = [2020, 2021, 2022, 2023]
    
    final_folder = os.path.join(save_path, f"{make.lower()}_{model.lower()}")
    os.makedirs(final_folder, exist_ok=True)

    # Use a dictionary to store image hashes to remove duplicates within this model
    hash_dict = {}

    for orientation in orientations:
        for year in years:
            # Refine query with the year; add extra keywords and exclusions for relevance.
            query = f"{make} {model} {year} {orientation} view car -toy -drawing -cartoon"
            print(f"\nDownloading {num_images} images for '{query}'...")

            # Create a temporary directory for downloading images for this query.
            temp_dir = os.path.join(save_path, 'temp')
            os.makedirs(temp_dir, exist_ok=True)

            crawler = GoogleImageCrawler(
                storage={'root_dir': temp_dir},
                feeder_threads=1,
                parser_threads=1,
                downloader_threads=4
            )
            crawler.crawl(
                keyword=query, 
                max_num=num_images, 
                min_size=(500, 500)
            )

            # Process the downloaded images.
            for file in os.listdir(temp_dir):
                if file.lower().endswith(('.jpg', '.png', '.jpeg')):
                    src_path = os.path.join(temp_dir, file)
                    if not is_duplicate(src_path, hash_dict):
                        # Append orientation and year to the filename.
                        dst_path = os.path.join(final_folder, f"{orientation}_{year}_{file}")
                        shutil.move(src_path, dst_path)
                    else:
                        os.remove(src_path)
            # Remove the temporary folder after processing each query.
            shutil.rmtree(temp_dir)
    print(f"\nDownload complete for {make} {model}!\n")

# Car dataset (example subset; extend as needed)
car_data = {
    "Toyota": ["Vios", "Innova", "Hilux", "Fortuner", "Wigo", "Corolla Altis", "Avanza", "Rush", "Camry", "RAV4", "HiAce", "Land Cruiser", "LiteAce", "Raize", "GR Yaris", "GR Supra", "Alphard", "Coaster", "Corolla Cross", "Veloz", "Yaris Cross"],
    "Mitsubishi": ["Mirage", "Mirage G4", "Montero Sport", "Strada", "Xpander", "L300", "Outlander PHEV"],
    "Ford": ["Ranger", "Everest", "Explorer", "Mustang", "Territory"],
    "Honda": ["City", "Civic", "BR-V", "CR-V", "HR-V", "Accord", "Jazz", "Brio", "Mobilio"],
    "Nissan": ["Almera", "Navara", "Terra", "Patrol", "X-Trail", "Juke", "GT-R", "Leaf", "Kicks e-POWER", "Livina", "Urvan"],
    "Hyundai": ["Accent", "Tucson", "Santa Fe", "Starex", "Kona", "Venue", "Palisade", "Ioniq", "Stargazer", "Stargazer X"],
    "Mazda": ["Mazda2", "Mazda3", "CX-3", "CX-30", "CX-5", "CX-8", "CX-9", "MX-5", "BT-50"],
    "Suzuki": ["Alto", "Celerio", "Swift", "Dzire", "Ertiga", "Vitara", "Jimny", "S-Presso", "XL7", "Carry"],
    "Chevrolet": ["Spark", "Sail", "Trax", "Trailblazer", "Colorado", "Suburban", "Camaro", "Tahoe"],
    "Kia": ["Picanto", "Rio", "Soluto", "Seltos", "Sportage", "Sorento", "Carnival", "Stonic", "K2500"],
    "Isuzu": ["D-Max", "mu-X", "Traviz", "N-Series", "F-Series", "C&E-Series"],
    "Subaru": ["Impreza", "XV", "Forester", "Outback", "WRX", "BRZ"]
}

# Run the downloader for each car make and model.
for make, models in car_data.items():
    for model in models:
        download_car_images(make, model, num_images=40, save_path='scraped_dataset')
