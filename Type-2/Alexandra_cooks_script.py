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
            if "https://alexandracooks.com/" in href and "category" not in href and href not in recipe_links:
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

        # 1. Product name (title)
        title = soup.find("h2", class_="tasty-recipes-title")
        title = title.get_text(strip=True) if title else "No title found"

        # 2. Short description
        short_description = soup.find("div", class_="tasty-recipes-description-body")
        short_description = short_description.get_text(strip=True) if short_description else "No short description found"

        # 3. Prep time
        prep_time = soup.find("span", class_="tasty-recipes-prep-time")
        prep_time = prep_time.get_text(strip=True) if prep_time else "No prep time found"
        # 4. Cook time
        cook_time = soup.find("span", class_="tasty-recipes-cook-time")
        cook_time = cook_time.get_text(strip=True) if cook_time else "No cook time found"

        # 5. Total time
        total_time = soup.find("span", class_="tasty-recipes-total-time")
        total_time = total_time.get_text(strip=True) if total_time else "No total time found"

        # 6. Servings
        servings = soup.find("span", class_="tasty-recipes-yield")
        servings = servings.get_text(strip=True) if servings else "No servings found"

        # 7. Diet
        diet = soup.find("span", class_="tasty-recipes-diet")
        diet = diet.get_text(strip=True) if diet else "No diet found"

        # 8. category
        category = soup.find("span", class_="tasty-recipes-category")
        category = category.get_text(strip=True) if category else "No category found"

        # 6. method
        method = soup.find("span", class_="tasty-recipes-method")
        method = method.get_text(strip=True) if method else "No method found"

        # 9. cuisine
        cuisine = soup.find("span", class_="tasty-recipes-cuisine")
        cuisine = cuisine.get_text(strip=True) if cuisine else "No cuisine found"

        # 10. Ingredients
        ingredient_items = soup.select("div.tasty-recipes-ingredients ul li")
        ingredients_list = []
        for li in ingredient_items:
            text = li.get_text(separator=" ", strip=True)
            if text:
                ingredients_list.append(text)

        # Step 2: Combine into a single string (line by line)
        combined_ingredients = "\n".join(ingredients_list)

       # 11. Instructions
        instruction_items = soup.find_all("li", id=re.compile(r"instruction-step-\d+"))

        instructions = []

        if instruction_items:
            for item in instruction_items:
                match = re.search(r"instruction-step-(\d+)", item.get("id"))
                step_number = match.group(1) if match else "?"
                instruction_text = item.get_text(strip=True)
                instructions.append(f"{step_number}. {instruction_text}")
        else:
            instructions.append("No instructions found")

        # Join all instructions into one string, separated by newlines or spaces
        combined_instructions = "\n".join(instructions)  # or use " " if you prefer one-line

        # 12. Instruction Video
        video_div = soup.find("div", class_="tasty-recipe-video-embed")
        video_url = None

        if video_div:
            iframe = video_div.find("iframe")
            if iframe and iframe.has_attr("src"):
                video_url = iframe["src"]
            else:
                video_url = "No video URL found"
        else:
            video_url = "No video section found"

        # 13. Image URL - Extract the src from the img tag inside wprm-recipe-image div
        image_div = soup.find("div", class_="tasty-recipes-image")
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
                        image_url = "https://alexandracooks.com" + image_url
                else:
                    image_url = "No image URL found"
            else:
                image_url = "No img tag found"
        else:
            image_url = "No image div found"

        # 12. Product URL
        product_url = url  # The product URL is simply the current URL

        return {
            "ProductName": title,
            "Data_Source_URL": product_url,
            "ProductShortDescription (Summary)": short_description,
            "Cuisine_Type": cuisine,
            "Meal_Type": method,
            "Type_of_Diet": diet,
            "cook_time": cook_time,
            "prep_time": prep_time,
            "image_url": image_url,
            "servings": servings,
            "total_time": total_time,
            "Ingredients": combined_ingredients,
            "instructions": combined_instructions,
            "Video": video_url
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

# Main function to scrape recipes from multiple categories
def scrape_by_category(categories, output_file="alexandracooks_recipes.csv"):
    base_url = "https://alexandracooks.com/category/recipe/"
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
    df.drop_duplicates(subset=["ProductName", "Data_Source_URL"], keep="first", inplace=True)

    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"\n✅ Saved {len(df)} unique recipes to {output_file}")

# Updated categories to scrape
categories_to_scrape = [
    "sauces", "salads", "jams-spreads", "breakfast", "side-dish", "dinner", "appetizers", "lunch", "soup", "desserts", "bread",
    "drinks" ]

# Run the scraper
scrape_by_category(categories_to_scrape, output_file="alexandracooks_recipes.csv")
