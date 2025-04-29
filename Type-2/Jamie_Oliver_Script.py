import requests
import time
import pandas as pd
from bs4 import BeautifulSoup
 
# Function to get all category links
def get_category_links(base_url):
    category_links = set()
    print(f"Fetching categories from: {base_url}")
   
    response = requests.get(base_url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        print("Failed to fetch categories. Stopping.")
        return list(category_links)
 
    soup = BeautifulSoup(response.text, "html.parser")
 
    # Find all category links (categories are under "/recipes/")
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "/recipes/" in href and not href.endswith("recipes/"):
            full_url = f"https://www.jamieoliver.com{href}" if not href.startswith("http") else href
            category_links.add(full_url)
 
    print(f"✅ Found {len(category_links)} category links.")
    return list(category_links)
 
# Function to get all recipe links from a category page
def get_recipe_links_from_category(category_url):
    recipe_links = set()
    print(f"Fetching recipes from: {category_url}")
 
    response = requests.get(category_url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        print(f"Failed to fetch {category_url}")
        return list(recipe_links)
 
    soup = BeautifulSoup(response.text, "html.parser")
 
    # Look for recipe links
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "/recipes/" in href and "recipe" in href:
            full_url = f"https://www.jamieoliver.com{href}" if not href.startswith("http") else href
            recipe_links.add(full_url)
 
    print(f"✅ Found {len(recipe_links)} recipes in {category_url}.")
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
 
        # Extract recipe title
        title = soup.find("h1", class_='detail-panel__page-title')
        title = title.get_text(strip=True) if title else "No title found"
 
        # Duplicate Check
        if title in seen_titles:
            print(f"Skipping duplicate recipe: {title}")
            return None
        seen_titles.add(title)
 
        # Extract cooking time, difficulty, and servings
        recipe_facts = soup.find_all("h6", class_="type-subtitle-sm line-clamp-2")
        facts_data = [fact.get_text(strip=True) for fact in recipe_facts]
        facts_text = "\n".join(facts_data)
 
        # Extract ingredients
        ingredients_div = soup.find("div", class_="ingredients-rich-text")
        ingredients = [p.get_text(strip=True) for p in ingredients_div.find_all("p", class_="type-body")] if ingredients_div else []
        ingredients_text = "\n".join(ingredients)
 
        # Extract method steps
        method_div = soup.find("div", class_="rich-text astro-erqtmm5j rich-text--justify-center rich-text--align-left")
        method_steps = []
        if method_div:
            ol_tag = method_div.find("ol")
            method_steps = [f"{index+1}. {li.get_text(strip=True)}" for index, li in enumerate(ol_tag.find_all("li"))] if ol_tag else []
 
        method_text = "\n".join(method_steps)
 
        # Extract image URL from meta tag
        image_url = soup.find("meta", property="og:image")
        image_url = image_url["content"] if image_url else "No image URL found"
 
        # Product URL
        product_url = url
 
        # Extract all nutrition information
        nutrition_cards = soup.find_all('div', class_='nutrition--card')
        nutrition_data = []
        for card in nutrition_cards:
            nutrition_title = card.find('p', class_='type-body-sm pb-6 capitalize astro-oujdv6rb')
            percentage = card.find('p', class_='type-highlight-sm relative astro-oujdv6rb')
            nutrition_data.append({
                'Nutrition': nutrition_title.get_text(strip=True) if nutrition_title else "",
                'Percentage': percentage.get_text(strip=True) if percentage else ""
            })
 
        return {
            "product_name": title,
            "time_serves_data": facts_text,
            "ingredients": ingredients_text,
            "method": method_text,
            "image_url": image_url,
            "product_url": product_url,
            "nutrition_data": nutrition_data
        }
 
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None
 
# Main function to scrape all recipes
def scrape_jamieoliver(output_file="jamieoliver_recipes.csv"):
    base_url = "https://www.jamieoliver.com/recipes/"
    all_recipes = []
    seen_titles = set()
 
    # Get all category links
    category_links = get_category_links(base_url)
 
    # Collect all recipe links from each category
    recipe_links = set()
    for category_url in category_links:
        category_recipe_links = get_recipe_links_from_category(category_url)
        recipe_links.update(category_recipe_links)
        time.sleep(1)  # To avoid overwhelming the server
 
    print(f"\n✅ Total recipes found: {len(recipe_links)}")
 
    # Scrape recipe details
    for idx, recipe_url in enumerate(recipe_links):
        print(f"Scraping {idx+1}/{len(recipe_links)}: {recipe_url}")
        recipe_data = scrape_recipe(recipe_url, seen_titles)
        if recipe_data:
            all_recipes.append(recipe_data)
        time.sleep(1)
 
    # Save to CSV
    df = pd.DataFrame(all_recipes)
    df.drop_duplicates(subset=["product_name", "product_url"], keep="first", inplace=True)
    df.to_csv(output_file, index=False)
    print(f"\n✅ Saved {len(df)} unique recipes to {output_file}")
 
# Run the scraper
scrape_jamieoliver(output_file="jamieoliver_recipes.csv")
