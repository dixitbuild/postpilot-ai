# Deployment

How PostPilot AI was deployed, what we used, and the problems we hit along the way.

## What we used

| Thing | Why |
|---|---|
| **Streamlit Community Cloud** | Free hosting made for Streamlit apps. Deploys straight from GitHub. |
| **GitHub** (`dixitbuild/postpilot-ai`) | Streamlit Cloud pulls the code from here. |
| **uv** (`pyproject.toml` + `uv.lock`) | Streamlit Cloud reads these files to install dependencies. |
| **Streamlit Secrets** | Stores `GROQ_API_KEY` on the server instead of a `.env` file. |

## Before deploying

These were already in place:

- `.env` is in `.gitignore`, so the Groq API key never goes to GitHub.
- `data/enriched_post.json` is committed, so the app can load example posts.
- `pyproject.toml` and `uv.lock` list all dependencies.

## Steps we followed

1. **Push the code to GitHub.** Make sure the `main` branch on GitHub matches your local code.
2. **Sign in** at [share.streamlit.io](https://share.streamlit.io) with your GitHub account.
3. **Create the app:**
   - Repository: `dixitbuild/postpilot-ai`
   - Branch: `main`
   - Main file: `main.py`
4. **Add the secret.** Go to **Advanced settings → Secrets** and paste:
   ```toml
   GROQ_API_KEY = "your-key-here"
   ```
   Streamlit turns this into an environment variable, so `Groq()` in `llm_helper.py` finds it without any code changes.
5. **Pick the Python version** in Advanced settings (we used 3.12, which matches `requires-python = ">=3.12"`).
6. **Click Deploy** and open the public URL to test.

## How Streamlit Cloud knew what to install

We never told it how to install dependencies. It found them on its own:

- Streamlit Cloud only runs Python apps, so it assumes Python.
- It looks through the repo for a dependency file (`requirements.txt`, `Pipfile`, `pyproject.toml`, `uv.lock`).
- Our repo has `pyproject.toml` and `uv.lock`, so it installed with **uv**, using the exact versions from `uv.lock`.
- To see this, open **Manage app** and scroll to the top of the logs. The build lines show which file it used and which packages it installed.

## Problem we hit: 403 "Access denied"

After deploying, clicking **Generate** showed this error:

```
groq.PermissionDeniedError: Error code: 403 - {'error': {'message': 'Access denied. Please check your network settings.'}}
```

**What it meant:**

- The API key was fine. A wrong or missing key gives a **401** (`AuthenticationError`).
- A **403** with "check your network settings" means Groq was blocking requests from the Streamlit Cloud server's address.
- That's why the same key worked on a laptop but not on the server.

**How we found the real error:** Streamlit hides error messages on the page. Click **Manage app** (bottom-right) to see the full logs.

**How we fixed it:** we went to **Manage app → ⋮ → Reboot app**. After the reboot the app worked.

**If it happens again and a reboot doesn't help:** host the app somewhere else, like [Render](https://render.com), using the same repo:

```
streamlit run main.py --server.port $PORT --server.address 0.0.0.0
```

Add `GROQ_API_KEY` as an environment variable in Render's dashboard.

## Updating the app later

- **Code change:** push to `main`. Streamlit Cloud redeploys automatically.
- **New package:** run `uv add <package>`, then push **both** `pyproject.toml` and `uv.lock`.
- **New secret:** go to **Manage app → Settings → Secrets**.
