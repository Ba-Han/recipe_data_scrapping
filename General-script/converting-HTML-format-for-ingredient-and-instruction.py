//////////////Converting into HTML format/////////////////
import pandas as pd
import html
import re
 
# Load the Excel file with all text as strings to preserve formatting
df = pd.read_excel('/content/scrapping_alexandracooks_recipes.xlsx', dtype=str)
 
# Updated ingredient splitter (only split on newlines)
def split_ingredients(text):
    if pd.isna(text):
        return []
    return [line.strip() for line in text.split('\n') if line.strip()]
 
# Updated instruction splitter (split by numbered points like 1., 2., etc.)
def split_instructions(text):
    if pd.isna(text):
        return []
    # Use regex to find numbered steps (e.g., 1. ... 2. ...)
    matches = re.split(r'\s*(?=\d+\.\s)', text)
    cleaned_steps = []
    for step in matches:
        step = step.strip()
        # Remove leading number (e.g., '1. ' or '2. ') from the line
        step = re.sub(r'^\d+\.\s*', '', step)
        if step:
            cleaned_steps.append(step)
    return cleaned_steps
 
# Convert to HTML for Ingredients
def convert_ingredients_to_html(text):
    lines = split_ingredients(text)
    html_lines = ''.join(f"<li>{html.escape(line)}</li>" for line in lines)
    return (
        '<h3 style="text-align: left;" class="directions-title">'
        '<span style="background-color: rgb(255, 255, 255); color: rgb(34, 34, 34);">'
        'Ingredients</span></h3>'
        f"<ul>{html_lines}</ul>"
    )
 
# Convert to HTML for Instructions
def convert_instructions_to_html(text):
    lines = split_instructions(text)
    html_lines = ''.join(
        f'<li><span style="background-color: rgb(255, 255, 255); color: rgb(68, 68, 68);">'
        f"{html.escape(line)}</span></li>" for line in lines
    )
    return (
        '<h3 style="text-align: left;" class="directions-title">'
        '<span style="background-color: rgb(255, 255, 255); color: rgb(34, 34, 34);">'
        'Directions</span></h3>'
        f"<ul>{html_lines}</ul>"
    )
 
# Apply both transformations
df['ingredients'] = df['ingredients'].apply(convert_ingredients_to_html)
df['instructions'] = df['instructions'].apply(convert_instructions_to_html)
 
# Save to a new Excel file
output_file = 'alexandracooks_recipes_final_html.xlsx'
df.to_excel(output_file, index=False)
 
output_file