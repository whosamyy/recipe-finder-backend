"""Recipe recommendations from the public, keyless DummyJSON API."""
import os
import re

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024
CORS(app, origins=[
    'https://whosamyy.github.io',
    'http://localhost:8000', 'http://127.0.0.1:8000',
], methods=['GET', 'POST', 'OPTIONS'], allow_headers=['Content-Type'])
API_URL = 'https://dummyjson.com/recipes?limit=0'


def normalize(value):
    return ' '.join(value.lower().split())


def matches(user, ingredient):
    """Match a whole word or phrase, never 'rice' inside 'licorice'."""
    words = lambda text: ' '.join(re.findall(r'\w+', text.lower()))
    return f' {words(user)} ' in f' {words(ingredient)} '


def covered(ingredient, users):
    # A combined entry needs both parts: salt alone does not cover pepper.
    parts = re.split(r'\s+and\s+|\s*&\s*', ingredient, flags=re.IGNORECASE)
    return all(any(matches(user, part) for user in users) for part in parts)


def error(message, status):
    return jsonify(success=False, error=message), status


def valid_recipe(recipe):
    if not isinstance(recipe, dict):
        return False
    for key in ('name', 'image', 'cuisine', 'difficulty'):
        if not isinstance(recipe.get(key), str) or not recipe[key].strip():
            return False
    for key in ('ingredients', 'instructions', 'mealType'):
        values = recipe.get(key)
        if not isinstance(values, list) or not values or not all(isinstance(x, str) and x.strip() for x in values):
            return False
    for key in ('id', 'prepTimeMinutes', 'cookTimeMinutes', 'rating', 'servings', 'caloriesPerServing', 'reviewCount'):
        value = recipe.get(key)
        if type(value) not in (int, float) or value < 0:
            return False
    return True


@app.get('/')
def index():
    return jsonify(status='ok', message='Recipe Finder backend is running')


@app.get('/health')
def health():
    return jsonify(status='healthy')


@app.post('/recommend')
def recommend():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error('Send a JSON object with an ingredients list.', 400)
    raw = data.get('ingredients')
    if not isinstance(raw, list):
        return error('ingredients must be a list of strings.', 400)
    if len(raw) > 50 or any(not isinstance(x, str) or len(x) > 100 for x in raw):
        return error('Use at most 50 ingredients, each a string of at most 100 characters.', 400)
    ingredients = list(dict.fromkeys(normalize(x) for x in raw if x.strip()))
    if not ingredients:
        return error('Please provide at least one ingredient.', 400)
    if any(not re.search(r'\w', x) for x in ingredients):
        return error('Each ingredient must contain a letter or number.', 400)
    limit = data.get('limit', 10)
    if type(limit) is not int or not 1 <= limit <= 100:
        return error('limit must be an integer from 1 to 100.', 400)
    max_time = data.get('maxTime')
    if max_time is not None and (type(max_time) is not int or not 1 <= max_time <= 1440):
        return error('maxTime must be an integer from 1 to 1440 minutes.', 400)
    difficulty = data.get('difficulty')
    if difficulty is not None and difficulty not in ('Easy', 'Medium', 'Hard'):
        return error('difficulty must be Easy, Medium, or Hard.', 400)
    try:
        response = requests.get(API_URL, timeout=(3, 10))
        if response.status_code != 200:
            return error('The recipe provider is unavailable. Please try again later.', 502)
        payload = response.json()
    except requests.RequestException:
        return error('Could not reach the recipe provider. Please try again later.', 502)
    except ValueError:
        return error('The recipe provider returned invalid JSON. Please try again later.', 502)
    recipes = payload.get('recipes') if isinstance(payload, dict) else None
    if not isinstance(recipes, list) or not all(valid_recipe(r) for r in recipes):
        return error('The recipe provider returned unexpected data. Please try again later.', 502)
    results = []
    for recipe in recipes:
        if max_time is not None and recipe['prepTimeMinutes'] + recipe['cookTimeMinutes'] > max_time:
            continue
        if difficulty is not None and recipe['difficulty'] != difficulty:
            continue
        matched = [user for user in ingredients if any(matches(user, item) for item in recipe['ingredients'])]
        if not matched:
            continue
        missing = [item for item in recipe['ingredients'] if not covered(item, ingredients)]
        results.append({**recipe, 'matchedIngredients': matched, 'missingIngredients': missing,
                        'matchCount': len(matched), 'matchPercentage': round(100 * len(matched) / len(ingredients))})
    results.sort(key=lambda r: (-r['matchCount'], -r['rating'], r['id']))
    results = results[:limit]
    return jsonify(success=True, ingredients=ingredients, count=len(results), recipes=results)


@app.errorhandler(HTTPException)
def http_error(exc):
    return error(exc.description, exc.code)


@app.errorhandler(Exception)
def unexpected_error(exc):
    # Do not expose exception messages, request bodies, or configuration.
    return error('An unexpected server error occurred. Please try again later.', 500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '5000')), debug=False)
