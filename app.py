from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask_cors import CORS
import json
import re

load_dotenv()

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Gemini API Key not found. Please set the GEMINI_API_KEY environment variable")
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

def generate_prompt(image_data):
    return f"""
        Analyze the ingredients present in this image of a pantry.
        Please detect all the distinct ingredients or food items in the picture.
        When you are unsure or there are multiple possibilities, provide those as well,
        marked with a `?` at the end of the ingredient. Make sure there are no repeated ingredients.

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

            # Retrieve recipes based on ingredients
            recipes = get_recipes(ingredients)

            return jsonify({
                'ingredients': ingredients,
                'recipe': recipes
            }), 200

        except Exception as e:
            return jsonify({'error': f"Could not process Gemini response: {e}"}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': f'Error processing request: {e}'}), 500

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
