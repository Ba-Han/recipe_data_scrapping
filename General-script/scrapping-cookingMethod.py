!pip install spacy
!python -m spacy download en_core_web_sm
 
////////////scraping Cooking information//////////////////
 
import pandas as pd
from bs4 import BeautifulSoup
import spacy
 
# Load spaCy English NLP model
nlp = spacy.load("en_core_web_sm")
 
# Function to generate meaningful ProductName
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
    return "Cooking Step"  # This will be used to filter out later
 
# Global StepId counter
step_counter = 1
output_data = []
 
# Load your Excel file
input_file = "AbeulasCounter_Recipe_PIM_Final_Formatted (1).xlsx"  # Update if needed
df = pd.read_excel(input_file)
 
# Iterate through each recipe row
for _, row in df.iterrows():
    recipe_id = row.get('ProductNumber')
    html = row.get('Cooking_instructionsMethod', '')
   
    if pd.isna(html):
        continue
 
    # Parse HTML for steps
    soup = BeautifulSoup(str(html), 'html.parser')
    steps = soup.find_all('li')
 
    for step in steps:
        full_text = step.get_text(strip=True)
        product_name = generate_product_name(full_text)
 
        # Skip if product name is not meaningful
        if product_name == "Cooking Step":
            continue
 
        step_id = f"IS{step_counter:05d}"
        step_counter += 1
 
        # Add to output
        output_data.append({
            "RecipeID": recipe_id,
            "StepId": step_id,
            "ProductName": product_name,
            "ProudctShorDescription": full_text,
            "Image": "",
            "Video": ""
        })
 
# Convert to DataFrame and export to Excel
output_df = pd.DataFrame(output_data)
output_df.to_excel("final_cooking_steps_nlp_filtered.xlsx", index=False)
 
print("✅ Final cooking steps exported with meaningful ProductNames.")