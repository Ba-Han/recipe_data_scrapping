import requests
import time
import pandas as pd
from bs4 import BeautifulSoup
from recipe_scrapers import scrape_me
 
# Function to get all recipe links from a category (Handles Pagination)
def get_category_recipe_links(category_url):
    recipe_links = set()  # Store unique recipe links
    page = 1  
 
    while True:
        url = f"{category_url}/page/{page}/" if page > 1 else category_url
        print(f"Fetching recipes from: {url}")
 
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            print(f"Failed to fetch {url}. Stopping pagination.")
            break  
 
        soup = BeautifulSoup(response.text, "html.parser")
        found_links = set()
 
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "https://addapinch.com/" in href and "category" not in href and href not in recipe_links:
                recipe_links.add(href)
                found_links.add(href)
 
        if not found_links:
            print(f"No more recipes found on page {page}. Stopping pagination.")
            break  
 
        page += 1  
        time.sleep(1)  
 
    return list(recipe_links)
 
# Function to scrape recipe details
def scrape_recipe(url, seen_titles):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch {url}")
            return None
 
        soup = BeautifulSoup(response.text, "html.parser")
 
        # Extract recipe details
        title = soup.find("h1")
        title = title.get_text(strip=True) if title else "No title found"
 
        # **Duplicate Check**: If title is already scraped, skip it
        if title in seen_titles:
            print(f"Skipping duplicate recipe: {title}")
            return None
        seen_titles.add(title)  # Add to seen titles set
 
        short_description = soup.find("div", class_="wprm-recipe-summary wprm-block-text-normal")
        short_description = short_description.get_text(strip=True) if short_description else "No short description found"
 
        prep_time = soup.find("span", class_="wprm-recipe-prep_time")
        prep_time = prep_time.get_text(strip=True) if prep_time else "No prep time found"
 
        cook_time = soup.find("span", class_="wprm-recipe-cook_time")
        cook_time = cook_time.get_text(strip=True) if cook_time else "No cook time found"
 
        total_time = soup.find("span", class_="wprm-recipe-total_time")
        total_time = total_time.get_text(strip=True) if total_time else "No total time found"
 
        servings = soup.find("span", class_="wprm-recipe-servings")
        servings = servings.get_text(strip=True) if servings else "No servings found"
 
        ingredients = soup.find_all("li", class_="wprm-recipe-ingredient")
        ingredients = [ingredient.get_text(strip=True) for ingredient in ingredients] if ingredients else ["No ingredients found"]
 
        instructions = soup.find_all("li", class_="wprm-recipe-instruction")
        instructions = [step.find("div", class_="wprm-recipe-instruction-text").get_text(strip=True) for step in instructions] if instructions else ["No instructions found"]
 
        notes = soup.find("div", class_="wprm-recipe-notes")
        notes = notes.get_text(strip=True) if notes else "No notes found"
 
        nutrition = soup.find("div", class_="wprm-nutrition-label-container-simple")
        nutrition = nutrition.get_text(strip=True) if nutrition else "No nutrition information found"
 
        # Image URL
        image_div = soup.find("div", class_="wprm-recipe-image")
        if image_div:
            img_tag = image_div.find("img")
            if img_tag:
                image_url = img_tag.get("data-lazy-src") or img_tag.get("src")
                if image_url and not image_url.startswith("http"):
                    image_url = "https://addapinch.com" + image_url
            else:
                image_url = "No img tag found"
        else:
            image_url = "No image div found"
 
        return {
            "product_name": title,
            "short_description": short_description,
            "prep_time": prep_time,
            "cook_time": cook_time,
            "total_time": total_time,
            "servings": servings,
            "ingredients": ingredients,
            "instructions": instructions,
            "notes": notes,
            "nutrition": nutrition,
            "image_url": image_url,
            "product_url": url
        }
 
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None
 
# Main function to scrape recipes from multiple categories
def scrape_addapinch_by_category(categories, output_file="addapinch_recipes.csv"):
    base_url = "https://addapinch.com/category/all-recipes/"
    all_recipes = []
    seen_titles = set()  # Set to store unique titles
 
    for category in categories:
        category_url = f"{base_url}{category}"
        print(f"\nScraping category: {category} ({category_url})")
 
        recipe_links = get_category_recipe_links(category_url)
        print(f"Found {len(recipe_links)} recipes in {category}")
 
        for idx, recipe_url in enumerate(recipe_links):
            print(f"Scraping {idx+1}/{len(recipe_links)}: {recipe_url}")
            recipe_data = scrape_recipe(recipe_url, seen_titles)
            if recipe_data:
                recipe_data["category"] = category  
                all_recipes.append(recipe_data)
            time.sleep(1)  
 
    # Convert to DataFrame
    df = pd.DataFrame(all_recipes)
 
    # **Remove exact duplicate rows**
    df.drop_duplicates(subset=["product_name", "product_url"], keep="first", inplace=True)
 
    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"\n✅ Saved {len(df)} unique recipes to {output_file}")
 


# Updated categories to scrape
categories_to_scrape = [
    "christmas", "new-year", "valentines-day", "easter", "mothers-day", "fathers-day", "july-4th", "halloween", "birthday", "thanksgiving", "shower",
    "main-course", "desserts", "appetizers", "breakfast", "sides",
    "lunch", "salad-soup-and-salad", "bread", "snacks", "soups-and-stews"
]  
 
# Run the scraper
scrape_addapinch_by_category(categories_to_scrape, output_file="addapinch_recipes.csv")
