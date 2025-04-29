!pip install pandas openpyxl requests
 
////////////download image folder with excel.xlsx file//////////////
import os
import requests
import re
import pandas as pd
 
# Define the folder to save images
save_folder = "recipe_images"
os.makedirs(save_folder, exist_ok=True)
 
# Path to the Excel file
excel_file_path = "/content/scrapping_alexandracooks_recipes.xlsx"
 
# Log file for errors
log_file_path = "download_errors_recipes.log"
 
# Function to check if a URL is valid and points to an image
def is_valid_image_url(url):
    if not isinstance(url, str) or not re.match(r'https?://\S+', url):
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
 
# Read the Excel file
df = pd.read_excel(excel_file_path)
 
# Iterate through each row
for index, row in df.iterrows():
    recipe_name = str(row["ProductNumber"]).strip()
    image_url = str(row["image"]).strip()
 
    if is_valid_image_url(image_url):
        download_image(recipe_name, image_url)
    else:
        log_error(recipe_name, image_url, "Invalid image URL")
 
print("Download complete! Errors are logged in 'download_errors_recipes.log'.")