/////////////downloaded image script with .csv file////////////////////
import os
import csv
import requests
import chardet
import re
 
# Define the folder to save images
save_folder = "jamieoliver_recipe_images"
os.makedirs(save_folder, exist_ok=True)
 
# Path to the CSV file
csv_file_path = "/content/jamieoliver_recipes.csv"  # Updated to use the uploaded file
 
# Log file for errors
log_file_path = "download_errors_jamieoliver_recipes.log"
 
# Detect encoding of the CSV file
def detect_encoding(file_path):
    with open(file_path, "rb") as f:
        raw_data = f.read(10000)  # Read a sample of the file
        result = chardet.detect(raw_data)
        return result["encoding"]
 
# Function to check if a URL is valid and points to an image
def is_valid_image_url(url):
    if not re.match(r'https?://\S+', url):
        return False
    return url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'))
 
# Function to download and save images
def download_image(recipe_name, image_url):
    headers = {"User-Agent": "Mozilla/5.0"}  # Mimic a browser request
    try:
        response = requests.get(image_url, headers=headers, stream=True, timeout=10)
        if response.status_code == 200:
            # Create a valid filename
            filename = f"{recipe_name}.jpg".replace("/", "_").replace(" ", "_")
            image_path = os.path.join(save_folder, filename)
 
            with open(image_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"Downloaded: {recipe_name}")
        else:
            log_error(recipe_name, image_url, f"HTTP {response.status_code}")
    except Exception as e:
        log_error(recipe_name, image_url, str(e))
 
# Function to log errors
def log_error(recipe_name, image_url, error_message):
    with open(log_file_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{recipe_name} -> {image_url} : {error_message}\n")
    print(f"Failed to download: {recipe_name} - {error_message}")
 
# Detect encoding
detected_encoding = detect_encoding(csv_file_path)
print(f"Detected Encoding: {detected_encoding}")
 
# Read CSV and process each row
with open(csv_file_path, newline="", encoding=detected_encoding, errors="replace") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        recipe_name = row["product_number"].strip()
        image_url = row["image_url"].strip()
 
        if is_valid_image_url(image_url):
            download_image(recipe_name, image_url)
        else:
            log_error(recipe_name, image_url, "Invalid image URL")
 
print("Download complete! Errors are logged in 'download_errors_jamieoliver_recipes.log'.")
 