import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import time
from recipe_scrapers import scrape_me
 
BASE_URL = "https://barefeetinthekitchen.com/"
HEADERS = {"User-Agent": "Mozilla/5.0"}
 
CATEGORIES = [
    "appetizers", "breakfast", "lunch", "dinner", "side-dishes", 
    "snacks", "desserts", "drinks"
]
 
def get_category_links(category):
    print(f"\n📦 Collecting recipe links for category: {category}")
    links = set()
    page = 1
    while True:
        url = f"{BASE_URL}category/{category}/page/{page}/"
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code != 200:
                print(f"❌ Failed to access page {page}. Stopping.")
                break
            soup = BeautifulSoup(res.text, "html.parser")
            articles = soup.find_all("article")
            if not articles:
                break
            print(f"✅ Page {page}: {len(articles)} articles scanned", end=", ")
            count_before = len(links)
            for a in articles:
                link_tag = a.find("a", href=True)
                if link_tag:
                    full_url = urljoin(BASE_URL, link_tag["href"])
                    links.add(full_url)
            print(f"{len(links)} total links.")
            page += 1
            time.sleep(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    print(f"🔗 Total links found for {category}: {len(links)}")
    return list(links)
 
def fallback_scraper(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
 
        title = soup.find("h1", class_="entry-title").text.strip() if soup.find("h1", class_="entry-title") else ""
        description = soup.find("div", class_="wprm-recipe-summary").text.strip() if soup.find("div", class_="wprm-recipe-summary") else ""
        ingredients = "\n".join([li.text.strip() for li in soup.select(".wprm-recipe-ingredient")])
        instructions = "\n".join([step.text.strip() for step in soup.select(".wprm-recipe-instruction-text")])
        image_tag = soup.find("img", class_="attachment-ao-standard")
        image_url = image_tag["src"] if image_tag else ""
 
        total_time = soup.find("span", class_="wprm-recipe-total_time").text.strip() if soup.find("span", class_="wprm-recipe-total_time") else ""
        yields = soup.find("span", class_="wprm-recipe-servings").text.strip() if soup.find("span", class_="wprm-recipe-servings") else ""
 
        return {
            "title": title,
            "description": description,
            "ingredients": ingredients,
            "instructions": instructions,
            "image_url": image_url,
            "total_time": total_time,
            "yields": yields
        }
    except Exception as e:
        print(f"❌ Fallback failed for {url}: {e}")
        return None
 
def extract_recipe_data(url, category):
    print(f"🔍 Scraping: {url}")
    try:
        scraper = scrape_me(url)
        return {
            "title": scraper.title(),
            "description": scraper.description() if hasattr(scraper, "description") else "",
            "ingredients": "\n".join(scraper.ingredients()),
            "instructions": scraper.instructions(),
            "image_url": scraper.image(),
            "total_time": scraper.total_time(),
            "yields": scraper.yields(),
            "category": category,
            "url": url
        }
    except Exception as e:
        print(f"⚠️ Failed to scrape {url} with recipe_scrapers: {e}")
        fallback = fallback_scraper(url)
        if fallback:
            print(f"🔁 Fallback succeeded for {url}")
            fallback.update({
                "category": category,
                "url": url
            })
            return fallback
        else:
            print(f"❌ Fallback also failed for {url}")
            return None
 
def main():
    all_recipes = []
    for category in CATEGORIES:
        links = get_category_links(category)
        for link in links:
            recipe = extract_recipe_data(link, category)
            if recipe:
                all_recipes.append(recipe)
            time.sleep(0.5)
 
    df = pd.DataFrame(all_recipes)
    df.to_csv("barefeet_in_the_kitchen_recipes.csv", index=False)
    print(f"\n✅ Done! Total recipes saved: {len(df)}")
 
main()
