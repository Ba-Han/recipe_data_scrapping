import requests
import time
import pandas as pd
from bs4 import BeautifulSoup

def get_all_recipe_links(base_url):
    recipe_links = set()  # Store unique recipe links
    page = 1

    while True:
        url = f"{base_url}?page={page}" if page > 1 else base_url
        print(f"Fetching recipes from: {url}")

        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            print(f"Failed to fetch {url}. Stopping pagination.")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        found_links = set()

        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "https://15gram.be/recepten/" in href and "page" not in href and href not in recipe_links:
                recipe_links.add(href)
                found_links.add(href)

        if not found_links:
            print(f"No more recipes found on page {page}. Stopping pagination.")
            break

        page += 1
        time.sleep(1)

    return list(recipe_links)

# Function to scrape recipe details
def scrape_recipe(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch {url}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # 1. Product name (title)
        title = soup.find("h1", class_="text-center")
        title = title.get_text(strip=True) if title else "No title found"

        # 2. Short description
        short_description = soup.find("div", class_="large-push-2")
        short_description = short_description.get_text(strip=True) if short_description else "No short description found"

        # 3. Cook time
        cook_time = soup.find("span", class_="duration right")
        cook_time = cook_time.get_text(strip=True) if cook_time else "No cook time found"

        # 4. Servings
        servings = soup.find("span", class_="yield left")
        servings = servings.get_text(strip=True) if servings else "No servings found"

        # 5. Ingredients
        ingredient_items = soup.select("div.detail-ingr-block ul li")
        ingredients_list = []

        for li in ingredient_items:
            text = li.get_text(separator=" ", strip=True)
            if text:
                 ingredients_list.append(text)

        # Step 2: Combine into a single string (line by line)
        combined_ingredients = "\n".join(ingredients_list)

        # Step 2: Combine into a single string (line by line)
        combined_ingredients = "\n".join(ingredients_list)

       # 6. Instructions
        instruction_items = soup.find_all("li", attrs={"itemprop": "recipeInstructions"})
        instructions = []

        if instruction_items:
            for idx, item in enumerate(instruction_items, start=1):
                instruction_text = item.get_text(strip=True)
                instructions.append(f"{idx}. {instruction_text}")
        else:
            instructions.append("No instructions found")

        # Join all instructions into one string
        combined_instructions = "\n".join(instructions)


        # 7. Image URL - Extract the src from the img tag inside wprm-recipe-image div
        image_div = soup.find("div", class_="recipe-image-container")
        if image_div:
            # Look for the 'img' tag and try to extract the image URL
            img_tag = image_div.find("img")
            if img_tag:
                # First, try to get the image URL from 'data-lazy-src', then 'src' if necessary
                image_url = img_tag.get("data-lazy-src") or img_tag.get("src")

                if image_url:
                    # Check if the image URL is a data URI (placeholder), skip if true
                    if image_url.startswith("data:image"):
                        image_url = "No valid image found (data URI)"
                    # If the image URL is relative, prepend the base URL
                    elif not image_url.startswith("http"):
                        image_url = "https://15gram.be" + image_url
                else:
                    image_url = "No image URL found"
            else:
                image_url = "No img tag found"
        else:
            image_url = "No image div found"

        # 8. Product URL
        product_url = url  # The product URL is simply the current URL

        return {
            "ProductName": title,
            "Data_Source_URL": product_url,
            "ProductShortDescription (Summary)": short_description,
            "cook_time": cook_time,
            "image": image_url,
            "servings": servings,
            "Ingredients": combined_ingredients,
            "instructions": combined_instructions
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

# Main function to scrape recipes from multiple categories
def scrape_all_recipes(output_file="15gram_recipes.csv"):
    base_url = "https://15gram.be/recepten"
    all_recipes = []
    seen_titles = set()  # Set to store unique titles

    recipe_links = get_all_recipe_links(base_url)
    print(f"Found {len(recipe_links)} recipes in {base_url}")

    for idx, link in enumerate(recipe_links):
        print(f"Scraping {idx+1}/{len(recipe_links)}: {link}")
        recipe = scrape_recipe(link)
        if recipe:
            all_recipes.append(recipe)
        time.sleep(1)

    # Convert to DataFrame
    df = pd.DataFrame(all_recipes)

    # **Remove exact duplicate rows**
    df.drop_duplicates(subset=["ProductName", "Data_Source_URL"], keep="first", inplace=True)

    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"\n✅ Saved {len(df)} unique recipes to {output_file}")

# Run the scraper
scrape_all_recipes()
