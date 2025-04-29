///////////////////scrapping cookingInstructionMethod included with video url from the excel//////////////
import pandas as pd
from bs4 import BeautifulSoup
import spacy
 
# Load spaCy English NLP model
nlp = spacy.load("en_core_web_sm")
 
# Function to generate a meaningful ProductName
def generate_product_name(text):
    doc = nlp(text)
    verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]
    nouns = [token.text for token in doc if token.pos_ in ["NOUN", "PROPN"]]
    if verbs and nouns:
        return f"{verbs[0].capitalize()} {nouns[0].capitalize()}"
    elif nouns:
        return nouns[0].capitalize()
    elif verbs:
        return verbs[0].capitalize()
    return "Cooking Step"
 
# Load your Excel file
input_file = "alexandracooks_recipes_final_html (1).xlsx"
df = pd.read_excel(input_file)
 
# STEP 1: Create a map of RecipeID (ProductNumber) to video URL
video_map = df.set_index("ProductNumber")["Video"].fillna("").to_dict()
 
# STEP 2: Process each row and generate steps
step_counter = 1
output_data = []
 
for _, row in df.iterrows():
    recipe_id = row.get("ProductNumber")
    html = row.get("Cooking_instructionsMethod", "")
 
    if pd.isna(html):
        continue
 
    soup = BeautifulSoup(str(html), "html.parser")
    steps = soup.find_all("li")
 
    for step in steps:
        full_text = step.get_text(strip=True)
        product_name = generate_product_name(full_text)
 
        if product_name == "Cooking Step":
            continue
 
        step_id = f"IS{step_counter:05d}"
        step_counter += 1
 
        output_data.append({
            "RecipeID": recipe_id,
            "StepId": step_id,
            "ProductName": product_name,
            "ProudctShorDescription": full_text,
            "Image": "",
            "Video": video_map.get(recipe_id, "")
        })
 
# Export result to Excel
output_df = pd.DataFrame(output_data)
output_df.to_excel("final_cooking_steps_with_video.xlsx", index=False)
 
print("✅ Done! Video URLs mapped by RecipeID where available.")