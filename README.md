# Recipe Finder Backend — HW4

This Flask backend receives ingredients, validates and normalizes them, fetches public DummyJSON recipes, and ranks recipes by ingredient matches. The existing Recipe Finder remains in its separate frontend repository.

## Project links and current status

- Frontend repository: https://github.com/whosamyy/whosamyy.github.io
- Frontend website: https://whosamyy.github.io/recipe-finder/
- Backend repository: pending creation of a separate public `recipe-finder-backend` repository.
- Render URL: pending deployment.
- Frontend integration: pending the actual Render URL. The existing HW3 frontend still calls DummyJSON directly; it has not yet been changed to call this backend.

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

## Frontend communication — planned integration

After deployment, update `recipe-finder/app.js` in the **frontend repository**, preserving the existing design. On Find recipes, send a request like:

```js
// Replace with the actual public Render origin after deployment.
const BACKEND_URL = "https://YOUR-SERVICE.onrender.com";
const response = await fetch(`${BACKEND_URL}/recommend`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ ingredients: userIngredients, limit: 100 })
});
const data = await response.json();
if (!response.ok) throw new Error(data.error || "Recipe search failed.");
```

The final frontend should show loading feedback, validate the response, render returned recipes using backend match fields, preserve filters/favorites/details, and show readable errors. A failed or superseded request must not display stale results. This snippet is documentation, not a completed integration. Before pushing, verify the active frontend URL is the real Render URL, not localhost or the placeholder above.

## Render deployment

After local tests pass:

1. Create a separate public GitHub repository named `recipe-finder-backend` and upload these backend files at its root. Do not upload `.venv`, environment files, or the frontend.
2. In Render, choose **New → Web Service** and connect that repository.
3. Choose the Python runtime, leave Root Directory blank, use `pip install -r requirements.txt` as Build Command and `gunicorn app:app` as Start Command. Select the Free instance type. Set `PYTHON_VERSION` to `3.13.7` to match the local interpreter; this is public configuration, not a secret.
4. Deploy and copy the actual public service URL into the links section above.
5. Repeat the curl checks above using that HTTPS URL in place of `http://127.0.0.1:5000`.
6. Provide that URL for frontend integration. Then test the complete deployed GitHub Pages → Render → DummyJSON → results flow and error states before pushing the final frontend change.

These commands assume `app.py` and `requirements.txt` are at the backend repository root. See [Render's Flask guide](https://render.com/docs/deploy-flask). Free services may sleep while idle; allow extra time on the first request.

## HW4 deliverable checklist

- [x] Meaningful backend processing and structured JSON.
- [x] Input validation and JSON error handling.
- [x] Backend README and verbatim key prompt log.
- [ ] New public backend GitHub repository.
- [ ] Running public Render deployment and public endpoint tests.
- [ ] Frontend calls Render and displays returned data, with loading and errors.
- [ ] Frontend integration pushed to GitHub and deployed on Pages.
- [ ] Full browser integration and error tests on the deployed site.
- [x] Existing portfolio link points to `recipe-finder/` (frontend unchanged).
- [ ] Final security inspection of both repositories before publication.
- [ ] Record and upload a short demo video; test viewing permissions in incognito.
- [ ] Submit the Google Form linked from the assignment page before the deadline.

The frontend site already exists, but its HW4 integration is pending. Do not mark this assignment complete until all required deliverables are verified.

## 30–60 second video order

- 0–10 seconds: Open the deployed Recipe Finder and enter chicken, rice, and garlic.
- 10–25 seconds: Submit; show loading and the returned recipe cards.
- 25–40 seconds: Open a recipe and explain match percentage and missing ingredients. Show the browser Network tab's POST to the public Render `/recommend` endpoint.
- 40–50 seconds: Clear ingredients and submit to show the helpful empty-input message.
- 50–60 seconds: Show Render `/health` and briefly explain that Flask retrieves and ranks DummyJSON recipes.

Submit the frontend URL, both repository URLs, public backend URL, and viewable video link through the [HW4 assignment form link](https://www.cs.cmu.edu/~113/hw4.html).

## Local verification checkpoint

On September 21, 2026, all 10 automated test methods passed, along with the Gunicorn configuration check. Live Flask HTTP requests on port 5001 returned 200 for `/` and `/health`, 200 with 10 real recipes for chicken/rice/garlic, 400 for empty/missing/malformed inputs, and 200 with an empty list for unobtainium. Port 5000 was occupied. All six project files were inspected; no secrets were found. The original project prompt is preserved verbatim. Public deployment and frontend integration are still untested and pending.
