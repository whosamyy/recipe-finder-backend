# Recipe Finder Backend — HW4

This Flask backend receives ingredients, validates and normalizes them, fetches public DummyJSON recipes, and ranks recipes by ingredient matches. The existing Recipe Finder remains in its separate frontend repository.

## Project links and current status

- Frontend repository: https://github.com/whosamyy/whosamyy.github.io
- Frontend website: https://whosamyy.github.io/recipe-finder/
- Backend repository: https://github.com/whosamyy/recipe-finder-backend
- Render URL: https://recipe-finder-backend-o6bk.onrender.com/
- Frontend integration: implemented in the separate frontend repository; recipe searches call the backend’s `POST /recommend` endpoint.

## Endpoints

| Method | Path | Input | Output |
| --- | --- | --- | --- |
| GET | `/` | None | `{"status":"ok","message":"Recipe Finder backend is running"}` |
| GET | `/health` | None | `{"status":"healthy"}` (checks this service, not DummyJSON) |
| POST | `/recommend` | JSON object described below | Normalized ingredients, count, and ranked recipe objects |

Example request:

```json
{"ingredients":["chicken","rice","garlic"],"limit":10,"maxTime":45,"difficulty":"Easy"}
```

`ingredients` is required: a list of up to 50 strings, at most 100 characters each. Blank entries are removed, duplicates are removed after lowercasing and collapsing whitespace, and at least one ingredient must remain. Optional `limit` is an integer 1–100 (default 10), `maxTime` is an integer 1–1440 for total preparation plus cooking minutes, and `difficulty` is `Easy`, `Medium`, or `Hard`. Request bodies are limited to 16 KiB.

Success has `success: true`, `ingredients`, `count`, and `recipes`. Each recipe preserves the real DummyJSON fields including `id`, `name`, `image`, `ingredients`, `instructions`, `cuisine`, `difficulty`, `prepTimeMinutes`, `cookTimeMinutes`, `rating`, `mealType`, `servings`, `caloriesPerServing`, and `reviewCount`. It adds:

- `matchedIngredients`: entered ingredients found in the recipe.
- `matchCount`: number of entered ingredients that matched.
- `matchPercentage`: rounded `100 * matchCount / number of normalized entered ingredients`.
- `missingIngredients`: recipe entries not covered by the entered ingredients.

No matches is a successful response: `{"success":true,"ingredients":["unobtainium"],"count":0,"recipes":[]}`.

## How matching works

The backend compares whole words or phrases, ignoring case and punctuation. `chicken` matches `Chicken breast, sliced`; `rice` does not match `licorice`. Multiword inputs must match as a phrase. Recipes sort by match count, then rating, then ID for consistent ties. Recipes with zero matches are omitted.

For combined entries such as `Salt and pepper to taste`, both parts must match before the entry is removed from the missing list. This is simple text matching, not a complete pantry or nutrition model: it does not understand quantities, substitutions, all plural forms, or the difference between chicken meat and chicken broth. A 100% match means all entered ingredients matched, **not** that you can make the recipe without buying anything. The UI should describe missing entries as an estimate and let users review the full ingredient list and instructions; it must not promise the recipe is ready to make.

## Local setup and tests

From the backend repository root, using Python 3.13:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m unittest -v
python app.py
```

In another terminal:

```sh
curl -i http://127.0.0.1:5000/
curl -i http://127.0.0.1:5000/health
curl -i http://127.0.0.1:5000/recommend -H 'Content-Type: application/json' -d '{"ingredients":["chicken","rice","garlic"]}'
curl -i http://127.0.0.1:5000/recommend -H 'Content-Type: application/json' -d '{"ingredients":[]}'
curl -i http://127.0.0.1:5000/recommend -H 'Content-Type: application/json' -d '{}'
curl -i http://127.0.0.1:5000/recommend -H 'Content-Type: application/json' -d '{broken'
curl -i http://127.0.0.1:5000/recommend -H 'Content-Type: application/json' -d '{"ingredients":["unobtainium"]}'
```

Expected status: 200 for health and valid requests, 400 for invalid input, and 200 with no recipes for an unknown ingredient. Tests also simulate upstream timeouts, non-200 responses, invalid JSON, invalid recipe data, and unexpected server errors. The real API requires internet access. If port 5000 is occupied, run `PORT=5001 python app.py` and adjust test URLs.

## Dependencies, configuration, and security

`requirements.txt` pins Flask (routes and JSON), flask-cors (browser origin permissions), requests (DummyJSON HTTP requests), and gunicorn (production server).

The [public DummyJSON Recipes API](https://dummyjson.com/docs/recipes) requires no private API key. No credentials are needed or created. Local `PORT` is optional and defaults to 5000; it is read with `os.environ.get()`. If a future feature requires a secret, keep it on the backend in environment variables configured on Render and read it with `os.environ.get()`. Never put secrets in frontend JavaScript, source code, prompt logs, or Git history. `.env` files are ignored but are not automatically loaded by this application.

CORS allows `https://whosamyy.github.io`, `http://localhost:8000`, and `http://127.0.0.1:8000`, including JSON POST preflight requests. Serve the frontend through a local HTTP server, not a `file://` URL. CORS controls browser access to responses; it is not authentication and does not block curl clients.

Invalid inputs return 400; oversized bodies return 413; external failures or unexpected external data return 502; unexpected application failures return 500 with a generic message. Errors use `{"success":false,"error":"Readable explanation"}`. Exception details and request bodies are not printed. Requests to DummyJSON have a 3-second connection timeout and a 10-second read timeout. Debug mode is off.

## Frontend communication

When the user chooses Find recipes, the frontend sends their ingredients as JSON to `POST https://recipe-finder-backend-o6bk.onrender.com/recommend`. The backend retrieves recipes from DummyJSON, ranks ingredient matches, and returns recipe data for the frontend to display as recipe cards. Matching is handled on the backend.

Example request from the frontend:

```js
const BACKEND_URL = "https://recipe-finder-backend-o6bk.onrender.com";
const response = await fetch(`${BACKEND_URL}/recommend`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ ingredients: userIngredients, limit: 100 })
});
const data = await response.json();
if (!response.ok) throw new Error(data.error || "Recipe search failed.");
```

The response includes `recipes`, `count`, and the normalized `ingredients`. Each recipe includes `matchedIngredients`, `missingIngredients`, `matchCount`, and `matchPercentage` for displaying recommendation results. Errors return `success: false` and a readable `error` message.

To verify the deployed integration, check that searches show loading feedback and returned recipe cards, empty input and network failures produce readable messages, and no matches produces an empty-results message. Also check recipe details, filters, and favorites after a search.

## Render deployment

The backend is deployed at https://recipe-finder-backend-o6bk.onrender.com/. To recreate the deployment, connect the public backend repository to a Render Python Web Service with these settings:

- Root Directory: repository root (leave blank).
- Build Command: `pip install -r requirements.txt`.
- Start Command: `gunicorn app:app`.
- Instance type: Free.
- Python version: `PYTHON_VERSION=3.13.7`.
- API keys: none required.

Check the running service with:

```sh
curl -i https://recipe-finder-backend-o6bk.onrender.com/health
curl -i https://recipe-finder-backend-o6bk.onrender.com/recommend -H 'Content-Type: application/json' -d '{"ingredients":["chicken","rice","garlic"]}'
```

Repeat the local error-case requests against this public URL, then verify the complete GitHub Pages → Render → DummyJSON → recipe cards workflow in the browser.

These commands assume `app.py` and `requirements.txt` are at the backend repository root. See [Render's Flask guide](https://render.com/docs/deploy-flask). Free services may sleep while idle; allow extra time on the first request.

## HW4 deliverable checklist

- [x] Meaningful backend processing and structured JSON.
- [x] Input validation and JSON error handling.
- [x] Backend README and verbatim key prompt log.
- [x] New public backend GitHub repository.
- [x] Running public Render deployment; health and recommendation success responses verified.
- [x] Frontend calls the backend (integration completed by the project owner).
- [ ] Verify deployed result display, loading feedback, and error handling in the browser.
- [ ] Frontend integration pushed to GitHub and deployed on Pages.
- [ ] Full browser integration and error tests on the deployed site.
- [x] Existing portfolio link points to `recipe-finder/` (existing portfolio integration).
- [ ] Final security inspection of both repositories before publication.
- [ ] Record and upload a short demo video; test viewing permissions in incognito.
- [ ] Submit the Google Form linked from the assignment page before the deadline.

The backend is public and deployed, and frontend integration has been implemented. Unchecked items above still need verification or completion; they do not imply that the frontend integration code is missing.

## 30–60 second video order

- 0–10 seconds: Open the deployed Recipe Finder and enter chicken, rice, and garlic.
- 10–25 seconds: Submit; show loading and the returned recipe cards.
- 25–40 seconds: Open a recipe and explain match percentage and missing ingredients. Show the browser Network tab's POST to the public Render `/recommend` endpoint.
- 40–50 seconds: Clear ingredients and submit to show the helpful empty-input message.
- 50–60 seconds: Show Render `/health` and briefly explain that Flask retrieves and ranks DummyJSON recipes.

Submit the frontend URL, both repository URLs, public backend URL, and viewable video link through the [HW4 assignment form link](https://www.cs.cmu.edu/~113/hw4.html).

## Verification checkpoints

On September 21, 2026, all 10 automated test methods passed, along with the Gunicorn configuration check. Live Flask HTTP requests on port 5001 returned 200 for `/` and `/health`, 200 with 10 real recipes for chicken/rice/garlic, 400 for empty/missing/malformed inputs, and 200 with an empty list for unobtainium. Port 5000 was occupied. All six project files were inspected; no secrets were found. The original project prompt is preserved verbatim.

On September 22, 2026, the backend GitHub repository was confirmed public. The deployed `/health` endpoint returned `{"status":"healthy"}`, and `POST /recommend` returned HTTP 200 with a real recipe for chicken/rice/garlic. The recommendation response included the CORS header allowing `https://whosamyy.github.io`. A fresh local test run could not start because the active Python environment lacked `requests`; install the dependencies using the setup instructions above before rerunning tests. The project owner confirmed frontend integration is implemented; full browser verification of the deployed integration remains a separate checklist item.
