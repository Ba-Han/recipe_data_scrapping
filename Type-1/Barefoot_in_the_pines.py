import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
 
# Rotating User-Agent List to Avoid Blocking
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/537.36"
]
 
# Recipe Categories to Scrape
CATEGORIES = [
    "breakfast", "dinner", "desserts", "snacks", "side-dishes", "spring"
]
 
def extract_recipe_details(recipe_url, category):
    """Extracts recipe details from a valid recipe page."""
    recipe_data = {
        "title": "", "description": "", "prep_time": "", "cook_time": "", "total_time": "",
        "servings": "", "ingredients": "", "instructions": "", "cuisine": "",
        "meal_type": category, "image_url": "", "url": recipe_url
    }

    try:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        response = requests.get(recipe_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract Title
        title_tag = soup.find("h1", class_="post-title")
        if title_tag:
            recipe_data["title"] = title_tag.text.strip()

        # Extract Description
        description_tag = soup.find("div", class_="wprm-recipe-summary")
        if description_tag:
            recipe_data["description"] = description_tag.text.strip()

        # Extract Image URL
        image_tag = soup.find("img", class_="wp-post-image")
        if image_tag:
            recipe_data["image_url"] = image_tag.get("src", "")

        # Extract Times & Servings
        meta_items = soup.select(".wprm-recipe-time, .wprm-recipe-servings")
        for item in meta_items:
            text = item.text.strip()
            if "Prep Time" in text:
                recipe_data["prep_time"] = text.replace("Prep Time:", "").strip()
            elif "Cook Time" in text:
                recipe_data["cook_time"] = text.replace("Cook Time:", "").strip()
            elif "Total Time" in text:
                recipe_data["total_time"] = text.replace("Total Time:", "").strip()
            elif "Servings" in text:
                recipe_data["servings"] = text.replace("Servings:", "").strip()

        # Extract Ingredients
        ingredients_tag = soup.select(".wprm-recipe-ingredient")
        recipe_data["ingredients"] = "\n".join([li.text.strip() for li in ingredients_tag])

        # Extract Instructions
        instructions_tag = soup.select(".wprm-recipe-instruction-text")
        recipe_data["instructions"] = "\n".join([li.text.strip() for li in instructions_tag])

        # Extract Cuisine (Tags)
        tags = soup.find_all("a", rel="category tag")
        if tags:
            recipe_data["cuisine"] = ", ".join([tag.text.strip() for tag in tags])

    except Exception as e:
        print(f"❌ Error scraping {recipe_url}: {e}")

    return recipe_data
 
def scrape_recipe_links(base_url, category):
    """Extracts all recipe links for a specific category from the main site."""
    print(f"🚀 Fetching recipe links for {category}...")
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    recipe_links = set()
    page = 1

    while True:
        try:
            url = f"{base_url}/category/{category}/page/{page}/" if page > 1 else f"{base_url}/category/{category}/"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"❌ Failed to access page {page} of {category}. Stopping.")
                break

            soup = BeautifulSoup(response.content, "html.parser")
            links = [a["href"] for a in soup.select("article a") if a.has_attr("href") and "/" in a["href"]]

            if not links:
                break  # Stop when no more links are found

            recipe_links.update(links)
            print(f"✅ Page {page}: {len(links)} recipes found.")
            page += 1
            time.sleep(random.uniform(1, 3))  # Avoid rapid requests
        except Exception as e:
            print(f"❌ Error accessing page {page} of {category}: {e}")
            break

    print(f"✅ Total {len(recipe_links)} recipe links found for {category}.")
    return list(recipe_links)
 
# Run the scraper
base_url = "https://barefootinthepines.com"
all_recipes = []
 
for category in CATEGORIES:
    recipe_urls = scrape_recipe_links(base_url, category)

    for url in recipe_urls:
        recipe_data = extract_recipe_details(url, category)
        all_recipes.append(recipe_data)
 
df = pd.DataFrame(all_recipes)
 
# Save to CSV
df.to_csv("barefoot_in_the_pines_recipes_by_category.csv", index=False)
print("✅ Done! Data saved to barefoot_in_the_pines_recipes_by_category.csv")
