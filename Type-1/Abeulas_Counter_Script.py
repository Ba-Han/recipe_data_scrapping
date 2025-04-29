import requests
import time
import pandas as pd
from bs4 import BeautifulSoup
from recipe_scrapers import scrape_me

# Function to get all recipe links from a category (Handles Pagination)
def get_category_recipe_links(category_url):
    recipe_links = set()
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
            if "https://abuelascounter.com/" in href and "category" not in href and href not in recipe_links:
                recipe_links.add(href)
                found_links.add(href)
 
        if not found_links:
            print(f"No more recipes found on page {page}. Stopping pagination.")
            break  
 
        page += 1  
        time.sleep(1)  
 
    return list(recipe_links)
 # Function to extract description if `recipe_scrapers` fails
def get_recipe_description(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return "N/A"
 
        soup = BeautifulSoup(response.text, "html.parser")
        description_meta = soup.find("meta", attrs={"name": "description"})
        if description_meta and "content" in description_meta.attrs:
            return description_meta["content"]
 
        return "N/A"
    except:
        return "N/A"
 
# Function to scrape recipe details with better error handling
def scrape_recipe(url):
    try:
        scraper = scrape_me(url)

        description = scraper.description() if hasattr(scraper, 'description') and scraper.description() else get_recipe_description(url)
 
        return {
            "title": scraper.title(),
            "description": description if description else "N/A",
            "ingredients": "\n".join(scraper.ingredients()),
            "instructions": scraper.instructions(),
            "prep_time": scraper.prep_time() if scraper.prep_time() else "N/A",
            "cook_time": scraper.cook_time() if scraper.cook_time() else "N/A",
            "total_time": scraper.total_time() if scraper.total_time() else "N/A",
            "yields": scraper.yields() if scraper.yields() else "N/A",
            "image": scraper.image() if scraper.image() else "N/A",
            "host": scraper.host(),
            "url": url
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None
 
# Main function to scrape recipes from multiple categories
def scrape_abuelas_counter_by_category(categories, output_file="abuelas_recipes.csv"):
    base_url = "https://abuelascounter.com/category/"
    all_recipes = []
 
    for category in categories:
        category_url = f"{base_url}{category}"
        print(f"\nScraping category: {category} ({category_url})")
 
        recipe_links = get_category_recipe_links(category_url)
        print(f"Found {len(recipe_links)} recipes in {category}")
 
        for idx, recipe_url in enumerate(recipe_links):
            print(f"Scraping {idx+1}/{len(recipe_links)}: {recipe_url}")
            recipe_data = scrape_recipe(recipe_url)
            if recipe_data:
                recipe_data["category"] = category  
                all_recipes.append(recipe_data)
            time.sleep(1)  
 
    # Save data to CSV
    df = pd.DataFrame(all_recipes)
    df.to_csv(output_file, index=False)
    print(f"\n✅ Saved {len(all_recipes)} recipes to {output_file}")
 
# Updated categories to scrape
categories_to_scrape = [
    "healthy-recipes", "appetizers", "cocktail", "desserts", "entree", 
    "sauces", "sides", "soups"
]  
 
# Run the scraper for the specified categories
scrape_abuelas_counter_by_category(categories_to_scrape, output_file="abuelas_recipes.csv")
