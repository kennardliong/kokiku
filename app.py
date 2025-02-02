from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask_cors import CORS
import json
import re
import requests

load_dotenv()

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Gemini API Key not found. Please set the GEMINI_API_KEY environment variable")
genai.configure(api_key=GEMINI_API_KEY)

SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")
if not SPOONACULAR_API_KEY:
    raise ValueError("Spoonacular API Key not found. Please set the SPOONACULAR_API_KEY environment variable")

model = genai.GenerativeModel("gemini-1.5-flash")

def generate_prompt(image_data):
    return f"""
        Analyze the ingredients present in this image of a pantry.
        Please detect all the distinct ingredients or food items in the picture.
        When you are unsure or there are multiple possibilities, provide those as well,
        marked with a `?` at the end of the ingredient.

        Give me a response in the form of a JSON list. Here is the image data {image_data}

        For example:
        [
        "ingredient 1", "ingredient 2", "ingredient 3", "possible ingredient?",...
        ]

        If no ingredients are found or nothing is detectable, return an empty list.
        """

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    return send_from_directory('.', 'recipe.html')

@app.route('/recipe-details/<int:recipe_id>')
def recipe_details(recipe_id):
    try:
      url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={SPOONACULAR_API_KEY}&includeNutrition=false"
      response = requests.get(url)
      response.raise_for_status()
      data = response.json()
      print("Recipe details data: ", data)

      ingredients = data.get("extendedIngredients", [])
      analyzed_instructions = data.get("analyzedInstructions", [])
      instructions_list = []

      if analyzed_instructions and len(analyzed_instructions) > 0 and analyzed_instructions[0].get("steps"):
         instructions_list = analyzed_instructions[0].get("steps", [])
      else:
          instructions_text = data.get("instructions", "")
          if instructions_text:
              instructions_list = re.findall(r'<li>(.*?)<\/li>', instructions_text)


      formatted_ingredients = []
      for item in ingredients:
        formatted_ingredients.append({
            "name": item.get("name"),
            "amount": item.get("measures").get("metric").get("amount"),
            "unit" : item.get("measures").get("metric").get("unitShort")
        })


      return jsonify({
            "title": data.get("title"),
            "image": data.get("image"),
            "extendedIngredients": formatted_ingredients,
             "instructions": instructions_list
      })

    except requests.exceptions.RequestException as e:
      print(f"Spoonacular request failed: {e}")
      return jsonify({
           "error" : f"Could not get recipe details {e}"
      }), 500

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    try:
        print("Request received")
        data = request.get_json()
        print(f"Received data: {data}")

        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400

        base64_image = data['image']
        print(f"base64 image: {base64_image[:10]}...")

        image_data = {"mime_type": "image/jpeg", "data": base64_image}
        prompt = generate_prompt(image_data)
        print(f"Prompt: {prompt}")

        try:
            response = model.generate_content([prompt, image_data])
            print("Response: ", response.text)

            if not response.text:
                return jsonify({'error': 'Empty response from Gemini'}), 500

            # Extract JSON list using regex if it's inside a markdown block
            match = re.search(r"\[.*\]", response.text, re.DOTALL)
            if match:
                try:
                    ingredients = json.loads(match.group(0))  # Properly parse JSON
                except json.JSONDecodeError:
                    return jsonify({'error': f'Could not parse JSON response: {response.text}'}), 500
            else:
                return jsonify({'error': f'Could not extract JSON list from response: {response.text}'}), 500


            print(f"Ingredients detected: {ingredients}")
             # Remove any ingredients that are marked with ? for searching recipes
            search_ingredients = [item.replace("?", "") for item in ingredients]

            # Get Dropdown values from request
            meal_type = data.get("mealType", "")
            cuisine = data.get("cuisine", "")
            intolerances = data.get("intolerances", "")
            diet = data.get("diet", "")

            recipes = get_spoonacular_recipes(search_ingredients, meal_type, cuisine, intolerances, diet)

            return jsonify({
                'ingredients': ingredients,
                'recipes': recipes
            }), 200

        except Exception as e:
            return jsonify({'error': f"Could not process Gemini response: {e}"}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': f'Error processing request: {e}'}), 500


def get_spoonacular_recipes(ingredients, meal_type, cuisine, intolerances, diet):
    try:
        ingredients_str = ",".join(ingredients)
        url = f"https://api.spoonacular.com/recipes/findByIngredients?apiKey={SPOONACULAR_API_KEY}&ingredients={ingredients_str}&number=10&sort=min-missing-ingredients"
        if meal_type:
            url += f"&type={meal_type}"
        if cuisine:
             url += f"&cuisine={cuisine}"
        if intolerances:
            url += f"&intolerances={intolerances}"
        if diet:
            url += f"&diet={diet}"


        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        recipes = []
        for recipe in data:
            recipes.append({
                'title': recipe.get('title'),
                'image': recipe.get('image'),
                'id': recipe.get("id")
            })
        return recipes
    except requests.exceptions.RequestException as e:
          print(f"Spoonacular request failed: {e}")
          return []


def get_recipes(ingredients):
    # Placeholder for recipe retrieval based on ingredients
    # Could be API call to third party
    # This will return dummy data for demonstration.
    if "Chicken" in ingredients and "Rice" in ingredients and "Soy Sauce" in ingredients:
        return {
            "title": "Chicken Fried Rice",
            "description": "Combine the ingredients and fry in a wok, delicious!"
        }
    return None

if __name__ == '__main__':
    app.run(debug=True)
