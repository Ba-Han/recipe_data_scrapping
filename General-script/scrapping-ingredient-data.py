!pip install pandas beautifulsoup4 openpyxl
 
////////////scraping ingredient information//////////////////
from bs4 import BeautifulSoup
import pandas as pd
import re
 
# Load the Excel file
input_file = "AbeulasCounter_Recipe_PIM_Final_Formatted (1).xlsx"
df = pd.read_excel(input_file)
 
output_data = []
ingredient_counter = 1
 
# Regex patterns to match various number formats, including "to" in amount
amount_patterns = [
    r"^\s*(\d+\s*[-–−]\s*\d+)\s*([a-zA-Z]+)?",                            # e.g. 2-4 or 2 – 4
    r"^\s*(\d+\s*to\s*\d+)\s*([a-zA-Z]+)?",                               # e.g. 12 to 15
    r"^\s*([¼½¾⅓⅔⅛⅜⅝⅞]\s*to\s*[¼½¾⅓⅔⅛⅜⅝⅞])\s*([a-zA-Z]+)?",           # e.g. ¼ to ½
    r"^\s*([¼½¾⅓⅔⅛⅜⅝⅞])\s*([a-zA-Z]+)?",                                 # e.g. ½ tsp
    r"^\s*(\d+\s\d+/\d+)\s*([a-zA-Z]+)?",                                  # e.g. 1 1/2 tsp
    r"^\s*(\d+/\d+)\s*([a-zA-Z]+)?",                                       # e.g. 1/4 tsp
    r"^\s*(\d+(?:\.\d+)?)\s*([a-zA-Z]+)?",                                 # e.g. 2.5 tsp
    r"^\s*(\d+\s[¼½¾⅓⅔⅛⅜⅝⅞])\s*([a-zA-Z]+)?",                             # e.g. 1 ½ tsp
    r"^\s*(\d+)\s*([a-zA-Z]+)?",                                           # e.g. 2 tsp
]
 
 
for index, row in df.iterrows():
    product_number = row.get("ProductNumber")
    html_content = row.get("Ingredients (Long Description)")
 
    if pd.isna(product_number) or pd.isna(html_content):
        continue
 
    soup = BeautifulSoup(html_content, 'html.parser')
    ingredients = soup.find_all('li')
 
    for item in ingredients:
        text = item.get_text().strip()
 
        # Normalize special dashes to "to"
        clean_text = re.sub(r"\s*[–−]\s*", " to ", text)
 
        amount = ""
        uom = ""
        product_name = clean_text
 
        for pat in amount_patterns:
            match = re.match(pat, clean_text)
            if match:
                groups = match.groups()
                amount = groups[0].strip()
                uom = groups[1] if len(groups) > 1 and groups[1] else ""
                product_name = clean_text.replace(match.group(0), "").strip(" ,")
                break
 
        ingredient_id = f"IN{ingredient_counter:04d}"
        ingredient_counter += 1
 
        output_data.append({
            "RecipeID": product_number,
            "IngredientId": ingredient_id,
            "ProductName": product_name,
            "UOM": uom,
            "Amount": amount,
            "Image": ""
        })
 
# Export to Excel
output_df = pd.DataFrame(output_data)
output_df.to_excel("scrapping_ingredients_info_new.xlsx", index=False)
 
print("✅ Done! File saved as 'scrapping_ingredients_info_new.xlsx'")