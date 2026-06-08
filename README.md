# AetherAI

A Django web application with an AI / semantic-search engine (FAISS vector index +
sentence-transformers) plus an admin/staff portal for managing staff, uploads,
complaints and content.

---

## ⚠️ Read this first — about the "two AetherAI folders"

Django projects always have the project name appear **twice**. This is normal and
**not** a duplicate. Each one has a different job:

```
aetherainew\              ← THE PROJECT FOLDER  (open this in your editor)
│
├── manage.py             ← the command runner: python manage.py runserver
├── requirements.txt      ← list of Python packages to install
├── db-aetherai-07-01-26.sql  ← database backup/seed data
│
├── AetherAI\             ← CONFIG ONLY (the project's "brain") — rarely touched
│   ├── settings.py       ← all settings (database, apps, paths)
│   ├── urls.py           ← top-level URL routing
│   ├── wsgi.py / asgi.py ← server entry points
│   └── __init__.py
│
├── myapp\                ← 👈 YOUR ACTUAL CODE — this is where you work
│   ├── views.py          ← page logic (what each page does)
│   ├── models.py         ← database tables
│   ├── urls.py           ← app URL routing
│   ├── semantic.py       ← AI semantic-search engine
│   ├── h.py              ← AI helper
│   ├── admin.py
│   ├── migrations\       ← database schema history
│   └── static\           ← CSS, JS, images
│
├── templates\            ← HTML pages (admin\ and staff\)
├── media\                ← user-uploaded files
│
├── legal_index.faiss     ← AI vector index (do not delete)
├── metadata.pkl          ← AI data        (do not delete)
└── processed_ids.pkl     ← AI tracking    (do not delete)
```

**Simple rule:**
- Work in **`myapp\`** for features (views, models, AI code).
- Edit **`AetherAI\settings.py`** only for configuration.
- 🚫 **Never rename the inner `AetherAI\` folder** — `manage.py`, `settings.py`,
  and `wsgi.py` reference that exact name; renaming it breaks the project.

---

## Tech stack

- **Framework:** Django (Python)
- **Database:** MySQL — database name `aetherai` (see `AetherAI/settings.py`)
- **AI:** FAISS, sentence-transformers, transformers, scikit-learn
- **File handling / OCR:** Pillow, PyPDF2, pytesseract (needs the Tesseract OCR
  program installed separately on the system)

---

## ⚠️ Large files are NOT in this repository (read before cloning)

To stay under GitHub's 100 MB file limit, the large data and AI-model files are
**excluded from git** (see `.gitignore`). A fresh `git clone` gives you all the
**code** but **none** of these files — you must copy them over separately (USB
drive, Google Drive, or a zip) into the **exact same paths**:

| File | Where it must go | Size | What it is |
|---|---|---|---|
| `metadata.pkl` | repo root **and** `myapp\` | ~326 MB | AI data (needed for search) |
| `legal_index.faiss` | repo root **and** `myapp\` | ~53 MB | AI vector index |
| `processed_ids.pkl` | repo root | small | AI tracking |
| `media\uploaded_data.json` | `media\` | ~339 MB | uploaded data dump |
| `media\*.csv`, `media\*.xlsx` | `media\` | varies | uploaded data |
| `db-aetherai-07-01-26.sql` | repo root | ~8 KB | database dump |

Without the `.pkl` and `.faiss` files the AI semantic search will not work.

> **Note:** `.gitignore` only stops these files from going to GitHub — it does
> **not** delete them. On the machine where they already exist, the project runs
> normally. Only a fresh clone on another machine is missing them.

### Setting up on another computer — checklist
1. `git clone https://github.com/lizalfathim-eng/AetherAi.git` → gets the code.
2. Copy the large files from the table above into the cloned folder (same paths).
3. Follow **First-time setup** below (venv, dependencies, database).
4. Run the server.

> **Easiest alternative for moving between your own machines:** zip the whole
> project folder (skip `.git\` and `venv\`) and copy it — that carries the code
> *and* the data together in one step.

---

## First-time setup (Windows) — do this once

1. **Create & activate a virtual environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   You'll know it's active when your prompt starts with `(venv)`.

2. **Install dependencies** (uses the included `requirements.txt`)
   ```powershell
   pip install -r requirements.txt
   ```
   Also install the **Tesseract OCR** program separately (needed by `pytesseract`):
   https://github.com/UB-Mannheim/tesseract/wiki

3. **Set up the database** (MySQL must be installed and running)
   - Create a database named `aetherai`.
   - Confirm the user/password in `AetherAI/settings.py` match your MySQL
     (currently `root` / `root`).
   - Import the included dump to load the starting data:
     ```powershell
     mysql -u root -p aetherai < db-aetherai-07-01-26.sql
     ```

4. **Apply migrations**
   ```powershell
   python manage.py migrate
   ```

---

## Running it (every time you work)

```powershell
.\venv\Scripts\Activate.ps1     # 1. activate the environment
python manage.py runserver      # 2. start the server
```
Then open **http://127.0.0.1:8000/** in a browser. Press `Ctrl+C` in the terminal
to stop the server. (No need to repeat the first-time setup again.)

---

## How to work on the project

**Where to make changes:**

| I want to... | Edit this |
|---|---|
| Change what a page does / its logic | `myapp\views.py` |
| Add or change a database table/field | `myapp\models.py` (then run migrations, below) |
| Add or change a page's web address (URL) | `myapp\urls.py` |
| Change how a page looks (HTML) | `templates\admin\` or `templates\staff\` |
| Change styling / scripts / images | `myapp\static\ahome\` |
| Change the AI search behaviour | `myapp\semantic.py` and `myapp\h.py` |
| Change a setting (database, paths, etc.) | `AetherAI\settings.py` |

**The normal editing loop:**
1. Make your change in the right file above.
2. The dev server **auto-reloads** when you save — just refresh the browser.
3. If something breaks, the error appears in the terminal and in the browser page.

**If you changed `models.py` (database structure), run:**
```powershell
python manage.py makemigrations
python manage.py migrate
```
This updates the database to match your new model. You only need this for
database/model changes — not for views, templates, or styling.

**Handy commands:**
```powershell
python manage.py createsuperuser   # create an admin login for /admin
python manage.py shell             # open a Python console with the project loaded
pip freeze > requirements.txt      # save exact package versions once it all works
```

---

## Notes

- The big files `legal_index.faiss` and `metadata.pkl` are the pre-built AI index —
  keep them; rebuilding them takes time. They are **not committed to git** (too
  large for GitHub) — see "Large files are NOT in this repository" above for how
  to bring them to a new machine.
- The login page is at `/` (`templates/login.html`); admin and staff dashboards
  live under `templates/admin\` and `templates/staff\`.
- The `.sql` file is a point-in-time backup (Jan 7). It sets up / resets the
  database; the live MySQL database is the real data once you start working.
