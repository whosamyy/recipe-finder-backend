"""Run with python -m unittest -v; external failures are simulated."""
import unittest
from unittest.mock import Mock, patch
import requests
from app import app, matches

RECIPE = dict(id=1, name='Test chicken', image='https://example.com/chicken.webp',
              ingredients=['Chicken breast', 'Rice', 'Salt and pepper to taste'],
              instructions=['Cook thoroughly.'], cuisine='Test', difficulty='Easy',
              prepTimeMinutes=10, cookTimeMinutes=20, rating=4.5, mealType=['Dinner'],
              servings=2, caloriesPerServing=300, reviewCount=10)


class BackendTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.mock = patch('app.requests.get').start()
        self.addCleanup(patch.stopall)
        self.mock.return_value = Mock(status_code=200)
        self.mock.return_value.json.return_value = {'recipes': [RECIPE]}

    def test_status(self):
        self.assertEqual(self.client.get('/').json['status'], 'ok')
        self.assertEqual(self.client.get('/health').json, {'status': 'healthy'})

    def test_normalization_and_missing(self):
        r = self.client.post('/recommend', json={'ingredients': [' Chicken ', '', 'chicken', 'rice', 'garlic', 'salt']})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json['ingredients'], ['chicken', 'rice', 'garlic', 'salt'])
        recipe = r.json['recipes'][0]
        self.assertEqual(recipe['matchCount'], 3)
        self.assertEqual(recipe['matchPercentage'], 75)
        self.assertEqual(recipe['missingIngredients'], ['Salt and pepper to taste'])

    def test_invalid_input(self):
        for data in (None, [], {}, {'ingredients': 'rice'}, {'ingredients': []},
                     {'ingredients': [' ', '']}, {'ingredients': [None]},
                     {'ingredients': ['!!!']}, {'ingredients': ['rice'], 'limit': True},
                     {'ingredients': ['rice'], 'maxTime': -1},
                     {'ingredients': ['rice'], 'difficulty': []}):
            with self.subTest(data=data):
                r = self.client.post('/recommend', json=data)
                self.assertEqual(r.status_code, 400)
                self.assertFalse(r.json['success'])
        self.mock.assert_not_called()

    def test_malformed_and_missing_body(self):
        for body in ('{broken', ''):
            self.assertEqual(self.client.post('/recommend', data=body, content_type='application/json').status_code, 400)

    def test_no_matches_and_filters(self):
        for data in ({'ingredients': ['unobtainium']}, {'ingredients': ['rice'], 'maxTime': 15},
                     {'ingredients': ['rice'], 'difficulty': 'Hard'}):
            self.assertEqual(self.client.post('/recommend', json=data).json['recipes'], [])
        self.assertFalse(matches('rice', 'licorice'))
        self.assertFalse(matches('olive oil', 'olive leaves'))

    def test_ranking_and_limit(self):
        self.mock.return_value.json.return_value = {'recipes': [RECIPE, {**RECIPE, 'id': 2, 'ingredients': ['Chicken breast'], 'rating': 5}]}
        result = self.client.post('/recommend', json={'ingredients': ['chicken', 'rice'], 'limit': 1}).json
        self.assertEqual(result['count'], 1)
        self.assertEqual(result['recipes'][0]['id'], 1)

    def test_upstream_failure(self):
        for failure in (requests.Timeout(), requests.ConnectionError()):
            self.mock.side_effect = failure
            self.assertEqual(self.client.post('/recommend', json={'ingredients': ['rice']}).status_code, 502)
        self.mock.side_effect = None
        self.mock.return_value.status_code = 503
        self.assertEqual(self.client.post('/recommend', json={'ingredients': ['rice']}).status_code, 502)

    def test_bad_provider_data(self):
        for payload in (None, [], {}, {'recipes': {}}, {'recipes': [None]}, {'recipes': [{'name': 'incomplete'}]}):
            self.mock.return_value.json.return_value = payload
            self.assertEqual(self.client.post('/recommend', json={'ingredients': ['rice']}).status_code, 502)
        self.mock.return_value.json.side_effect = ValueError('bad JSON')
        self.assertEqual(self.client.post('/recommend', json={'ingredients': ['rice']}).status_code, 502)

    def test_server_errors(self):
        self.mock.side_effect = RuntimeError('private diagnostic detail')
        r = self.client.post('/recommend', json={'ingredients': ['rice']})
        self.assertEqual(r.status_code, 500)
        self.assertNotIn('private', r.get_data(as_text=True))
        self.assertEqual(self.client.get('/missing').status_code, 404)
        self.assertEqual(self.client.get('/recommend').status_code, 405)
        self.assertEqual(self.client.post('/recommend', data='x' * 17000, content_type='application/json').status_code, 413)

    def test_cors(self):
        for origin in ('https://whosamyy.github.io', 'http://localhost:8000', 'http://127.0.0.1:8000'):
            r = self.client.options('/recommend', headers={'Origin': origin, 'Access-Control-Request-Method': 'POST', 'Access-Control-Request-Headers': 'Content-Type'})
            self.assertEqual(r.headers['Access-Control-Allow-Origin'], origin)
            self.assertIn('POST', r.headers['Access-Control-Allow-Methods'])
        r = self.client.get('/health', headers={'Origin': 'https://unrelated.example'})
        self.assertNotIn('Access-Control-Allow-Origin', r.headers)


if __name__ == '__main__':
    unittest.main()
