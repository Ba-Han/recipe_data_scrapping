!pip install recipe-scrapers requests beautifulsoup4 pandas
!pip install googletrans==4.0.0-rc1

import pandas as pd
from googletrans import Translator

# Load your CSV file
input_file = "15gram_recipes.csv"   # Make sure this CSV is in the same folder as your script
output_file = "15gram_recipes_translated.csv"

# Initialize Translator
translator = Translator()

# Load the CSV
df = pd.read_csv(input_file)

# Columns you want to translate
columns_to_translate = [
    "ProductName",
    "ProductShortDescription (Summary)",
    "servings",
    "Ingredients",
    "instructions"
]

# Function to translate text
def translate_text(text):
    try:
        if pd.notna(text):  # Only translate if it's not NaN
            translated = translator.translate(str(text), src='nl', dest='en')  # from Dutch (nl) to English (en)
            return translated.text
        else:
            return text
    except Exception as e:
        print(f"Translation failed: {e}")
        return text

# Translate each column
for col in columns_to_translate:
    if col in df.columns:
        print(f"Translating column: {col}...")
        df[col] = df[col].apply(translate_text)
    else:
        print(f"Column {col} not found!")

# Save the translated CSV
df.to_csv(output_file, index=False)
print(f"\n✅ Translation complete! File saved as: {output_file}")
