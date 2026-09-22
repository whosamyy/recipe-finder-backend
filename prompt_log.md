# Prompt Log

## Tools Used
- Codex

## Key Prompts

### 1. Initial project instructions (verbatim)

I am working on CMU 15-113 HW4: Backend + Frontend.

Please help me build this assignment from scratch and make sure the implementation satisfies EVERY requirement on the HW4 assignment page.

Assignment context:
- My existing frontend is my Recipe Finder from HW3.
- It is deployed at:
  https://whosamyy.github.io/recipe-finder/
- My frontend is already inside my whosamyy.github.io GitHub repository.
- THIS repository is a separate new repository for the backend only.
- The backend will eventually be deployed publicly using Render.
- Use Python + Flask.

IMPORTANT:
Prioritize a simple, reliable, working frontend/backend integration over adding unnecessary features.
I need to understand the code and be able to explain it.

==================================================
PROJECT IDEA
==================================================

Turn my existing Recipe Finder into a frontend + backend application.

The user enters ingredients they already have.

Instead of doing the important recipe matching entirely in frontend JavaScript, the frontend should send the user's ingredients to this Flask backend.

The backend should:

1. Accept the ingredients from the frontend.
2. Validate and normalize them.
3. Retrieve recipe data from the public DummyJSON Recipes API.
4. Compare the user's ingredients against recipe ingredients.
5. Rank the recipes by how well they match.
6. Return structured JSON containing the best matches.
7. Include useful information such as:
   - recipe id
   - name
   - image
   - ingredients
   - instructions
   - cuisine
   - difficulty
   - prep time
   - cook time
   - rating
   - meal type
   - number of matching ingredients
   - match percentage
   - ingredients the user is missing

This backend processing should be meaningful and not simply echo the user's input.

==================================================
BACKEND REQUIREMENTS
==================================================

Use Flask.

Create at least these endpoints:

GET /

Return a small JSON response confirming the backend is running, such as:

{
  "status": "ok",
  "message": "Recipe Finder backend is running"
}

GET /health

Return:

{
  "status": "healthy"
}

POST /recommend

Accept JSON similar to:

{
  "ingredients": ["chicken", "rice", "garlic"]
}

Optionally allow fields such as:

{
  "ingredients": ["chicken", "rice", "garlic"],
  "limit": 10,
  "maxTime": 45,
  "difficulty": "Easy"
}

The /recommend endpoint must return meaningful structured JSON.

Example general shape:

{
  "success": true,
  "ingredients": ["chicken", "rice", "garlic"],
  "count": 5,
  "recipes": [
    {
      "id": 1,
      "name": "...",
      "image": "...",
      "ingredients": [...],
      "instructions": [...],
      "matchedIngredients": [...],
      "missingIngredients": [...],
      "matchCount": 2,
      "matchPercentage": 67,
      "cuisine": "...",
      "difficulty": "...",
      "prepTimeMinutes": 10,
      "cookTimeMinutes": 20,
      "rating": 4.5,
      "mealType": [...]
    }
  ]
}

Use the REAL response structure from the DummyJSON API.
Do not invent API fields.

==================================================
MATCHING LOGIC
==================================================

Make the matching algorithm understandable enough that I can explain it.

At minimum:

- convert user ingredients to lowercase
- trim extra whitespace
- remove empty entries
- prevent duplicates
- compare user ingredients against each recipe's ingredient strings
- allow reasonable partial matching, such as "chicken" matching "chicken breast"
- calculate how many of the user's ingredients match
- calculate a match percentage based on the user's entered ingredients
- calculate which recipe ingredients are still missing
- sort strongest matches first

Do not falsely say the user can make a recipe with only the ingredients they entered unless all required ingredients are actually covered.

==================================================
VALIDATION + ERROR HANDLING
==================================================

The backend MUST handle bad input gracefully.

Test and properly respond to:

- no JSON body
- missing "ingredients"
- ingredients not being a list
- empty ingredient list
- ingredient list containing empty strings
- duplicate ingredients
- API request failure
- DummyJSON returning unexpected data
- server errors

Return useful JSON errors instead of crashing.

Use appropriate HTTP status codes, for example:

400 for bad user input
502 or similar if the external API fails
500 only for unexpected server errors

Example:

{
  "success": false,
  "error": "Please provide at least one ingredient."
}

==================================================
EXTERNAL API
==================================================

Use the public DummyJSON Recipes API.

First inspect the actual API response and verify the real fields before writing logic around them.

Use a request such as:

https://dummyjson.com/recipes?limit=0

Use the Python requests library from the backend instead of fetching DummyJSON directly from the frontend for the recommendation request.

Handle:
- timeouts
- non-200 responses
- invalid JSON
- missing recipes array

Use a reasonable timeout.

==================================================
CORS
==================================================

My frontend is hosted at:

https://whosamyy.github.io

My backend will be on Render, so they are different origins.

Enable CORS correctly using flask-cors.

Allow requests from:
https://whosamyy.github.io

Also allow localhost during development if necessary.

Do not simply disable all browser security.

==================================================
SECURITY — EXTREMELY IMPORTANT
==================================================

Do NOT create, expose, hardcode, print, log, or commit:

- API keys
- access tokens
- passwords
- credentials
- secret keys
- private configuration values

The DummyJSON endpoint used for this assignment should not require a private API key.

If any feature turns out to require a private credential, STOP and tell me instead of placing it in the code.

Create a .gitignore containing at least:

.env
.env.*
venv/
.venv/
__pycache__/
*.pyc
.DS_Store
secrets.json

If environment variables are ever needed, read them using os.environ.get().

Never place private values in:
- Python source code
- JavaScript
- HTML
- README
- prompt log
- Git history

Before finishing, inspect all files you created or modified and explicitly tell me whether you found any secrets.

==================================================
FILES
==================================================

Create a clean backend structure.

At minimum:

app.py
requirements.txt
README.md
prompt_log.md
.gitignore

Keep the project simple unless another file is clearly useful.

requirements.txt should include all dependencies required by Render, including at least:

Flask
flask-cors
gunicorn
requests

Pin versions if appropriate.

==================================================
RENDER COMPATIBILITY
==================================================

Prepare the backend to deploy cleanly on Render.

It must work with a start command such as:

gunicorn app:app

Make sure Flask does not depend on hardcoded localhost-only settings.

For local development, allow:

python app.py

Use:

if __name__ == "__main__":

appropriately.

Do not deploy yet until local testing passes.

If useful, create a render.yaml, but only if it genuinely simplifies deployment. Do not make the project more complicated than needed.

==================================================
LOCAL TESTING
==================================================

Before touching the frontend, test the backend locally.

Give me exact commands for:

1. creating/activating a virtual environment if needed
2. installing dependencies
3. starting Flask
4. testing GET /
5. testing GET /health
6. testing POST /recommend using curl

Example POST test input:

{
  "ingredients": ["chicken", "rice", "garlic"]
}

Also test at least:

- valid ingredients
- empty ingredients
- missing ingredients property
- malformed request
- ingredient with no useful recipe matches

Do not move on until the backend itself works locally.

==================================================
FRONTEND INTEGRATION
==================================================

After the backend works locally, help me update my EXISTING Recipe Finder frontend.

Do NOT redesign the frontend or replace my existing project.

Preserve its current design and features as much as possible.

The important change is:

Frontend:
https://whosamyy.github.io/recipe-finder/

        ↓ fetch()

Backend:
POST /recommend

        ↓

Backend processes ingredients and returns JSON

        ↓

Frontend displays the returned recipe recommendations.

Use fetch() with:

method: "POST"
Content-Type: "application/json"

and JSON.stringify() for the request body.

The frontend must:

- send user ingredients to the backend
- wait for the response
- parse response JSON
- display returned recipes
- display loading feedback while waiting
- handle non-OK HTTP responses
- show a human-readable error if the backend is unavailable
- show a useful message for invalid/empty input
- avoid crashing if response data is missing

IMPORTANT:
During local testing, the frontend may temporarily use:

http://127.0.0.1:5000/recommend

BUT before the final GitHub push, it MUST use the public Render URL.

Add a clear comment near the backend URL so I know exactly where to replace it after Render deployment.

==================================================
RENDER DEPLOYMENT
==================================================

Once all local tests work, tell me exactly how to deploy this repo to Render.

The Render service should be:

Web Service

Expected settings should likely be:

Language:
Python

Build Command:
pip install -r requirements.txt

Start Command:
gunicorn app:app

Free instance type.

Do not guess if the actual repo structure requires different commands.

After deployment, I need to test:

GET /
GET /health
POST /recommend

using the public onrender.com URL.

Remember that Render's free tier may sleep and the first request can take a while.

After I provide the actual Render URL, update the frontend to use that URL instead of localhost.

Then test the COMPLETE flow:

GitHub Pages frontend
→ Render backend
→ DummyJSON API
→ backend processing
→ JSON response
→ frontend display

==================================================
README — REQUIRED FOR HW4
==================================================

Create a clear README.md in THIS BACKEND REPOSITORY.

It must explain:

1. What the backend does.

2. Every endpoint:
   - endpoint path
   - HTTP method
   - parameters/body it accepts
   - what it returns

3. How the frontend communicates with the backend:
   - which endpoint it calls
   - when it calls it
   - what JSON it sends
   - what it does with the response

4. How to set up and run the backend locally.

5. Dependencies.

6. Environment variables/API keys:
   - explain that this implementation uses the public DummyJSON Recipes endpoint and currently does not require a private API key
   - explain how environment variables would be used if a secret were added later

7. Security:
   - secrets belong on the backend
   - secrets must never be included in frontend JavaScript or committed to GitHub

8. Render deployment information.

9. Frontend URL:
   https://whosamyy.github.io/recipe-finder/

10. After deployment, include the public Render URL.

Keep the README student-readable and straightforward rather than overly corporate.

==================================================
PROMPT LOG — REQUIRED FOR HW4
==================================================

Create prompt_log.md.

It should contain:

# Prompt Log

## Tools Used
- Codex

## Key Prompts

Add THIS ENTIRE PROMPT verbatim as the first key prompt.

Do not:
- summarize it
- rewrite it
- shorten it
- invent prompts that I did not actually send

For later important implementation/debugging prompts, append them verbatim as additional key prompts.

==================================================
FRONTEND GITHUB REQUIREMENT
==================================================

My frontend already lives in my whosamyy.github.io repository.

Do not move it into this backend repo.

HW4 requires frontend and backend code to be on GitHub.

Keep:

Frontend repo:
whosamyy.github.io

Backend repo:
recipe-finder-backend

separate.

==================================================
PORTFOLIO
==================================================

My Recipe Finder is already part of my portfolio.

Do not redesign the portfolio.

Make sure the portfolio continues linking to:

recipe-finder/

Do not break my Project 1, Crossy Road, or any other existing portfolio content.

==================================================
SHORT VIDEO
==================================================

Do not create a video for me, but at the end give me a short demo checklist for the required HW4 video.

The video should demonstrate enough for a grader to understand the frontend/backend integration if they cannot run it themselves.

I should be able to demonstrate:

1. Open deployed Recipe Finder.
2. Enter ingredients.
3. Submit them.
4. Show loading state.
5. Show recipe results returned through the backend.
6. Show at least one error case such as empty input.
7. Briefly show/mention that the backend is deployed on Render.

Give me an approximately 30–60 second demo order.

==================================================
FINAL ASSIGNMENT CHECK
==================================================

Before saying this project is finished, check it against EVERY HW4 deliverable.

The assignment requires:

- public running backend deployment
- new public GitHub backend repository
- backend README
- backend prompt log/key prompts
- frontend code on GitHub
- frontend deployed
- frontend making real requests to backend
- meaningful structured backend response
- frontend displaying response
- graceful frontend and backend error handling
- portfolio integration/link
- no exposed private keys or secrets
- short demo video
- Google Form submission

Do NOT claim the project is fully complete until things requiring my action, such as the video and Google Form, are actually done.

==================================================
WORK ORDER
==================================================

Work incrementally.

PHASE 1:
Inspect this backend repository and create the initial files.

PHASE 2:
Implement GET / and GET /health.

PHASE 3:
Implement POST /recommend.

PHASE 4:
Test the backend locally and fix errors.

PHASE 5:
Explain the backend to me in simple terms.

PHASE 6:
Prepare it for Render.

PHASE 7:
Tell me when it is ready for me to create/connect the Render Web Service.

PHASE 8:
After I give you the Render URL, integrate the deployed backend into my existing Recipe Finder frontend.

PHASE 9:
Test frontend/backend communication and error cases.

PHASE 10:
Complete README and prompt log.

PHASE 11:
Perform a final security scan and HW4 requirement checklist.

Do NOT skip directly to deployment before local testing succeeds.

Do NOT commit or push changes without telling me what is being committed.

If you can make commits, use clear incremental commit messages instead of one giant commit.

==================================================
WHEN YOU FINISH EACH PHASE
==================================================

Tell me:

- which files you created or changed
- what changed
- how I can test it
- what I should understand about the code
- whether there are any errors still unresolved

At the final checkpoint, tell me:

1. Backend repository URL
2. Frontend repository URL
3. Frontend public URL
4. Render public URL
5. Which endpoint the frontend calls
6. Example request JSON
7. Example response JSON
8. How CORS works in this project
9. How errors are handled
10. Whether ANY secrets are present
11. Exactly what remains for me to submit manually

### 2. Assignment page

Here's the full instructions: [https://www.cs.cmu.edu/\~113/hw4.html](https://www.cs.cmu.edu/~113/hw4.html)
