import requests
import csv
import time
import pandas as pd
from bs4 import BeautifulSoup
from recipe_scrapers import scrape_me
 
# Function to get all recipe category URLs from AllRecipes homepage
def get_all_categories(base_url="https://www.allrecipes.com"):
    category_links = []
 
    print("Fetching all recipe categories...")
    response = requests.get(base_url)
    if response.status_code != 200:
        print("Failed to fetch categories.")
        return category_links
 
    soup = BeautifulSoup(response.text, "html.parser")
 
    # Find all links to categories
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "/recipes/" in href and base_url in href:
            category_links.append(href)
 
    return list(set(category_links))  # Remove duplicates
 
# Function to get all recipe links from a category page
def get_recipe_links(category_url, num_pages=1):
    recipe_links = []
 
    for page in range(1, num_pages + 1):
        url = f"{category_url}?page={page}"
        print(f"Scraping category page: {url}")
 
        response = requests.get(url)
        if response.status_code != 200:
            print("Failed to fetch:", url)
            continue
 
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/recipe/" in href and "allrecipes.com" in href:
                recipe_links.append(href)
 
    return list(set(recipe_links))  # Remove duplicates
 
# Function to format time into '1 hr 45 mins' instead of raw minutes
def convert_minutes_to_time(minutes):
    if not minutes or minutes <= 0:
        return "Not available"
 
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0 and mins > 0:
        return f"{hours} hr {mins} mins"
    elif hours > 0:
        return f"{hours} hr"
    else:
        return f"{mins} mins"
 
# Function to scrape recipe details including multiple serving sizes
def scrape_recipe(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch {url}")
            return None
 
        soup = BeautifulSoup(response.text, "html.parser")
 
        # Initialize scraper using recipe_scrapers
        scraper = scrape_me(url)
 
        # Get the title
        title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "No title found"
 
        # Extract Prep Time, Cook Time, Additional Time, Total Time, and Servings
        time_data = {}
        time_labels = ["Prep Time", "Cook Time", "Additional Time", "Total Time", "Servings"]
 
        # Normalize labels to avoid spacing & casing issues
        time_labels_normalized = {label.lower(): label for label in time_labels}
 
        time_items = soup.find_all("div", class_="mm-recipes-details__item")
 
        for item in time_items:
            label = item.find("div", class_="mm-recipes-details__label")
            value = item.find("div", class_="mm-recipes-details__value")
 
            if label and value:
                label_text = " ".join(label.get_text(strip=True).split()).lower()  # Remove extra spaces, normalize case
                value_text = value.get_text(strip=True)
 
                print(f"Found label: '{label_text}' with value: '{value_text}'")  # Debugging line
 
                if label_text in time_labels_normalized:
                    original_label = time_labels_normalized[label_text]
                    time_data[original_label] = value_text  # Store value with original label format
 
        # Check for missing prep time and use scraper's value if needed
        prep_time_formatted = convert_minutes_to_time(scraper.prep_time()) if scraper.prep_time() else time_data.get("Prep Time", "Not available")
 
        # Extract servings and ingredients based on serving sizes
        serving_sizes = {"1x": "1", "2x": "2", "4x": "4"}
        ingredients_data = {}
 
        for label, value in serving_sizes.items():
            serving_size_input = soup.find("input", {"value": value})
            if serving_size_input:
                serving_size_input["checked"] = "checked"  # Simulate selection
 
            # Extract ingredients for this serving size
            ingredients_list = soup.find_all("li", class_="mm-recipes-structured-ingredients__list-item")
            ingredients = [item.get_text(strip=True) for item in ingredients_list]
            ingredients_data[label] = ingredients
 
        # Convert times to readable format
        cook_time_formatted = convert_minutes_to_time(scraper.cook_time()) if scraper.cook_time() else time_data.get("Cook Time", "Not available")
        additional_time_formatted = convert_minutes_to_time(scraper.total_time() - scraper.prep_time() - scraper.cook_time()) if scraper.total_time() else time_data.get("Additional Time", "Not available")
        total_time_formatted = convert_minutes_to_time(scraper.total_time()) if scraper.total_time() else time_data.get("Total Time", "Not available")
 
        # Extract nutrition facts from the HTML
        nutrition_facts = {}
        nutrition_table = soup.find("table", class_="mm-recipes-nutrition-facts-summary__table")
        if nutrition_table:
            rows = nutrition_table.find_all("tr")
            for row in rows:
                columns = row.find_all("td")
                if len(columns) == 2:
                    nutrient_name = columns[1].get_text(strip=True)
                    nutrient_value = columns[0].get_text(strip=True)
                    nutrition_facts[nutrient_name] = nutrient_value
 
        # Extract daily value percentages for nutrition facts
        daily_values = {}
        nutrition_label_table = soup.find("table", class_="mm-recipes-nutrition-facts-label__table")
        if nutrition_label_table:
            rows = nutrition_label_table.find_all("tr")
            for row in rows:
                columns = row.find_all("td")
                if len(columns) == 2:
                    nutrient_name = columns[0].get_text(strip=True)
                    daily_value = columns[1].get_text(strip=True)
                    if "%" in daily_value:  # Ensure it's a daily value percentage
                        daily_values[nutrient_name] = daily_value
 
        return {
            "title": title,
            "ingredients_1x": "\n".join(ingredients_data.get("1x", [])),
            "ingredients_2x": "\n".join(ingredients_data.get("2x", [])),
            "ingredients_4x": "\n".join(ingredients_data.get("4x", [])),
            "instructions": "\n".join(scraper.instructions().split("\n")),
            "prep_time": prep_time_formatted,
            "cook_time": cook_time_formatted,
            "additional_time": additional_time_formatted,
            "total_time": total_time_formatted,
            "yields": scraper.yields(),
            "image": scraper.image(),
            "host": scraper.host(),
            "servings": time_data.get("Servings", "Not available"),
            "nutrition_facts": nutrition_facts,  # Include nutrition facts
            "daily_values": daily_values,  # Include daily values
            "url": url
        }
 
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None
 
# Main function to scrape and save recipes
def scrape_allrecipes(num_pages_per_category=1, output_file="newallrecipes.csv"):
    print("Step 1: Getting all recipe categories...")
    category_links = get_all_categories()
 
    print(f"Found {len(category_links)} categories. Scraping recipes from each category...")
 
    all_recipes = []
 
    for idx, category_url in enumerate(category_links):
        print(f"\nScraping category {idx+1}/{len(category_links)}: {category_url}")
 
        recipe_links = get_recipe_links(category_url, num_pages=num_pages_per_category)
 
        for recipe_idx, recipe_url in enumerate(recipe_links):
            print(f"Scraping recipe {recipe_idx+1}/{len(recipe_links)}: {recipe_url}")
            recipe_data = scrape_recipe(recipe_url)
            if recipe_data:
                all_recipes.append(recipe_data)
            time.sleep(1)  # Avoid server overload
 
    # Save data to CSV
    df = pd.DataFrame(all_recipes)
    df.to_csv(output_file, index=False)
    print(f"\n✅ Saved {len(all_recipes)} recipes to {output_file}")
 
# Run the scraper to capture all recipes
scrape_allrecipes(num_pages_per_category=2, output_file="newallrecipes.csv")