# AetherAI — Complete File Reference

A file-by-file guide to the whole project: **what each file is, what it does, and
why it exists.** Read this when you're new to the codebase or trying to find
"where does X happen?"

> **About the name appearing twice:** `AetherAI/` (config) and `myapp/` (your code)
> are *different* folders with different jobs — see the README's "two AetherAI
> folders" note. This document covers every file in detail.

---

## Table of contents
1. [Project type & how it fits together](#1-project-type--how-it-fits-together)
2. [Top-level files](#2-top-level-files)
3. [`AetherAI/` — project configuration](#3-aetherai--project-configuration)
4. [`myapp/` — the application code](#4-myapp--the-application-code)
5. [`myapp/static/` — front-end assets](#5-myappstatic--front-end-assets)
6. [`templates/` — HTML pages](#6-templates--html-pages)
7. [`media/` — uploaded files](#7-media--uploaded-files)
8. [The AI / semantic-search files explained](#8-the-ai--semantic-search-files-explained)
9. [Large files NOT in git (must be copied manually)](#9-large-files-not-in-git-must-be-copied-manually)

---

## 1. Project type & how it fits together

**AetherAI is a Django web application** with two parts:

- **A staff/admin portal** — login, manage staff records, file uploads, complaints.
- **An AI semantic-search engine** — staff upload documents (PDF / CSV / image /
  Word), text is extracted (with OCR for images), and that text is turned into a
  searchable AI index so you can ask natural-language questions and get the most
  relevant documents back.

**Request flow (simplified):**

```
Browser → AetherAI/urls.py → myapp/urls.py → myapp/views.py → (models.py + templates/)
                                                   │
                                          AI search uses FAISS index
                                          (legal_index.faiss + metadata.pkl)
```

**Tech stack:** Django 6 · MySQL · FAISS · sentence-transformers · transformers ·
scikit-learn · Pillow / PyPDF2 / pytesseract (OCR).

---

## 2. Top-level files

| File | What it is / does |
|---|---|
| `manage.py` | Django's command runner. Everything starts here: `python manage.py runserver`, `migrate`, `makemigrations`, `createsuperuser`, etc. You rarely edit it. |
| `requirements.txt` | The list of Python packages to install (`pip install -r requirements.txt`). Includes Django, the MySQL driver, and all the AI libraries. Note: `pytesseract` also needs the **Tesseract OCR program** installed on the system separately. |
| `README.md` | Setup & day-to-day usage guide (install, run, where to edit things). |
| `FILE_REFERENCE.md` | **This document** — the detailed file-by-file reference. |
| `.gitignore` | Tells git which files **not** to upload to GitHub — chiefly the huge data/model files (`*.pkl`, `*.faiss`, `*.csv`, `*.xlsx`, `*.sql`, `media/uploaded_data.json`) plus Python/editor junk. |
| `db-aetherai-07-01-26.sql` | A MySQL database dump (backup/seed) from Jan 7. Used to load the starting data. *Currently git-ignored by the `*.sql` rule.* |
| `legal_index.faiss` *(generated)* | The AI vector index — see [section 8](#8-the-ai--semantic-search-files-explained). Not in git. |
| `metadata.pkl` *(generated)* | Maps each vector back to its document text + info. Not in git. |
| `processed_ids.pkl` *(generated)* | Tracks which documents are already indexed (so updates only add new ones). Not in git. |

---

## 3. `AetherAI/` — project configuration

This is the project's "brain": global settings and the top-level wiring. You touch
it mainly for configuration. **Never rename this folder** — `manage.py` and the
server entry points reference the exact name.

| File | What it does |
|---|---|
| `AetherAI/settings.py` | **The master config.** Defines installed apps, middleware, the **MySQL database connection** (db `aetherai`, user/password `root`/`root`), template directory, and static/media paths (`MEDIA_ROOT` → the `media/` folder). ⚠️ `DEBUG = True` and a hardcoded `SECRET_KEY` — fine for development, **must change for production**. |
| `AetherAI/urls.py` | **Top-level URL routing.** Sends `/admin/...` to Django's built-in admin, and everything under `/myapp/...` into `myapp/urls.py`. Also serves uploaded files from `media/` during development. |
| `AetherAI/wsgi.py` | Entry point for traditional (synchronous) web servers in production. Not edited normally. |
| `AetherAI/asgi.py` | Entry point for async servers. Not edited normally. |
| `AetherAI/__init__.py` | Marks the folder as a Python package. Empty on purpose. |

---

## 4. `myapp/` — the application code

**This is where the real work lives.** Features, database tables, AI logic.

| File | What it does |
|---|---|
| `myapp/views.py` | **The heart of the app** — every page's logic. Login/logout, role-based redirect (Admin vs Staff), staff CRUD (add/edit/view/delete), complaints, change password, **file upload + text extraction + AI index building**, and the **AI question-answering** views. See the detailed breakdown below. |
| `myapp/models.py` | **Database tables**, defined as Python classes: `Staff`, `Upload`, `Complaint`. See the model breakdown below. |
| `myapp/urls.py` | **App URL routing** — maps each `/myapp/<something>/` web address to a function in `views.py`. |
| `myapp/admin.py` | Where you'd register models to appear in Django's `/admin` site. Currently empty (nothing registered). |
| `myapp/apps.py` | App configuration class (`MyappConfig`). Auto-generated; rarely touched. |
| `myapp/tests.py` | Placeholder for automated tests. Currently empty. |
| `myapp/semantic.py` | **Standalone AI script** — builds/updates the FAISS index from `uploaded_data.json` and runs an interactive command-line legal search. Run directly (not through the web app). See [section 8](#8-the-ai--semantic-search-files-explained). |
| `myapp/h.py` | **Experimental/alternate AI search script** — a simpler version using `all-MiniLM-L6-v2` + scikit-learn cosine similarity instead of FAISS. Standalone CLI; has a hardcoded path to someone's local machine, so treat it as a scratch/experiment file. |
| `myapp/__init__.py` | Marks `myapp` as a Python package. Empty. |
| `myapp/migrations/0001_initial.py` | Auto-generated instructions that create the `Staff`, `Upload`, `Complaint` tables in the database. Generated by `makemigrations`; applied by `migrate`. Don't hand-edit. |
| `myapp/migrations/__init__.py` | Marks the migrations folder as a package. Empty. |

### `myapp/models.py` — the three database tables

| Model | Fields | Purpose |
|---|---|---|
| `Staff` | name, gender, dob, email, phone, photo, qualification, place, district, pin, join_date, experience, department, designation, salary, status, **USER** (one-to-one link to Django's auth `User`) | A staff member's full profile. Linked to a login account. |
| `Upload` | STAFF (FK), Date, document (file path), title, hashvalue (SHA-256) | One uploaded document. `hashvalue` is used to **detect duplicate uploads**. |
| `Complaint` | date, complaint, reply, status, STAFF (FK) | A complaint a staff member sends to admin, plus the admin's reply and status (`pending` / `replied`). |

### `myapp/views.py` — what the key functions do

**Auth & accounts**
- `loginpage_get` / `loginpage_post` — show login page; check credentials and
  **redirect by role**: Admin → admin home, Staff → staff home.
- `logout_get` — log out.
- `change_password_get/post` and `s_change_password_get/post` — change password
  (admin and staff versions).

**Admin: staff management**
- `new_home` / `home_get` — admin dashboard (lists uploads).
- `add_staff` / `add_staff_post` — add a staff member. Generates a random password,
  **emails it to the new staff member via Gmail SMTP**, creates their `User`
  account in the `Staff` group, saves their photo and profile.
  ⚠️ *Gmail credentials are hardcoded here — see security notes below.*
- `view_staff`, `view_more_staff`, `edit_staff`/`edit_staff_post`, `delete_staff` —
  list / view detail / edit / delete staff.

**Complaints**
- `adm_view_complaint`, `send_reply`/`send_reply_post` — admin views complaints and
  replies.
- `sendcomplaint_admin_get/post`, `view_complaintreply_get` — staff sends a
  complaint and views replies.

**File upload & AI indexing (the important one)**
- `upload_file` / `upload_file_post` — staff uploads a file. The POST handler:
  1. Validates the file type (jpg/png/pdf/doc/xlsx/csv…).
  2. Computes a **SHA-256 hash** and rejects duplicates.
  3. Saves the file into `media/` with a timestamp name.
  4. **Extracts text** — PDF via PyPDF2, CSV via the csv reader, **images via
     Tesseract OCR**.
  5. Saves an `Upload` record to the database.
  6. Appends the extracted text to `media/uploaded_data.json`.
  7. **Rebuilds the FAISS index** (`legal_index.faiss` + `metadata.pkl`) from that
     JSON so the new document becomes searchable.
- `view_upload_file` — lists all uploads.
- `extract_content` — re-extracts a saved file's text (PDF/CSV/image-OCR) and
  stores it in the session for Q&A.

**AI search / Q&A**
- `ask_doubt` — shows the "ask a question" page.
- `ask_question_post` — **semantic search**: loads the FAISS index + metadata,
  embeds the question with sentence-transformers, finds the closest document chunks
  (cosine similarity, score threshold 0.50), and returns the matching `Upload`
  records.
- `ask_question` — a different Q&A approach using a transformers
  `question-answering` pipeline (`distilbert`) over the extracted text in session.

> ⚠️ **Note on hardcoded paths:** several functions reference
> `C:\AetherAI\AetherAI\...` absolute paths for the JSON / index / metadata files.
> On a different machine these paths will be wrong and must be updated (ideally to
> use `settings.BASE_DIR` / `settings.MEDIA_ROOT`).

> 🔒 **Security notes (worth fixing later):** `add_staff_post` contains a Gmail
> address and app password in plain text, and `settings.py` has `DEBUG=True` + a
> committed `SECRET_KEY`. These should move to environment variables / a secrets
> file before any real deployment.

---

## 5. `myapp/static/` — front-end assets

Static assets live under `myapp/static/ahome/`. This is a **bootstrap-based
"eLearning" HTML template** used for styling and the public-facing pages.

| Path | What it is |
|---|---|
| `static/ahome/css/style.css` | Main custom stylesheet for the site's look. |
| `static/ahome/css/bootstrap.min.css` | Bootstrap CSS framework (layout, components). |
| `static/ahome/js/main.js` | Site JavaScript (menus, carousel init, animations). |
| `static/ahome/img/*.jpg` | Template images (carousel, team, courses, testimonials). |
| `static/ahome/lib/owlcarousel/` | Owl Carousel — the image/slider library. |
| `static/ahome/lib/animate/` | Animate.css — CSS animation library. |
| `static/ahome/lib/wow/` | WOW.js — triggers animations on scroll. |
| `static/ahome/lib/easing/` | jQuery easing — smooth scroll/animation timing. |
| `static/ahome/lib/waypoints/` | Waypoints — fires events as you scroll to elements. |
| `static/ahome/*.html` | Template demo pages (index, about, courses, team, contact, etc.) that ship with the theme. |
| `static/ahome/LICENSE.txt`, `READ-ME.txt`, `404.html` | Theme license, readme, and error page. |
| `static/ahome/lib/waypoints/links.php` | Leftover PHP file from the downloaded theme — not used by Django. |

> These `lib/` folders are third-party libraries from the downloaded template.
> You normally don't edit them; you edit `css/style.css` and `js/main.js`.

---

## 6. `templates/` — HTML pages

The actual pages Django renders, split by role. `templates/login.html` is the entry
page; the rest live under `admin/` and `staff/`.

**`templates/login.html`** — the login screen (the app's front door at `/`).

### `templates/admin/` (the admin portal)
| File | Page |
|---|---|
| `home_index.html` | Admin dashboard. |
| `add_staff.html` | Form to add a new staff member. |
| `edit_staff.html` | Form to edit a staff member. |
| `view_staff.html` | List of all staff. |
| `view_more_staff.html` | One staff member's full details. |
| `viewcomplaint.html` | List of complaints from staff. |
| `send reply.html` | Form for admin to reply to a complaint. *(note the space in the filename)* |
| `change_password.html` | Admin change-password form. |

### `templates/staff/` (the staff portal)
| File | Page |
|---|---|
| `s_home_index.html` | Staff dashboard. |
| `view_profile.html` | Staff member's own profile. |
| `view_more_staff.html` | View another staff member's details. |
| `upload_file.html` | Upload a document. |
| `view_uploadfile.html` | List of uploaded documents. |
| `view_content.html` | Shows extracted text from a document + Q&A. |
| `ask_doubt.html` | Ask a natural-language question (AI semantic search). |
| `send_complaint.html` | Send a complaint to admin. |
| `view_complaintreply.html` | View admin's replies to complaints. |
| `change_password.html` | Staff change-password form. |

---

## 7. `media/` — uploaded files

`MEDIA_ROOT` points here (`AetherAI/settings.py`). Every file a staff member
uploads is saved here with a **timestamp filename** (e.g. `20260301211740.pdf`).

- **Images / PDFs / Word / Excel** — the raw uploaded documents.
- **`media/uploaded_data.json`** *(large, not in git)* — the accumulated extracted
  text of every upload; this is the **source data the AI index is built from**.
- **`media/*.csv`, `media/*.xlsx`** *(large, not in git)* — uploaded spreadsheet
  data.

> Small sample media files (the timestamped jpg/pdf/docx) **are** committed; the
> big JSON/CSV/XLSX data dumps are git-ignored.

---

## 8. The AI / semantic-search files explained

This is the part that makes AetherAI "AI". Here's how the pieces relate:

```
Uploaded docs ──extract text──► media/uploaded_data.json
                                        │
                          (sentence-transformers embeds text)
                                        ▼
                       legal_index.faiss   +   metadata.pkl
                      (the numeric vectors)   (text + doc info per vector)
                                        │
                       processed_ids.pkl tracks what's already done
                                        ▼
              Ask a question → embed it → find nearest vectors → show matching docs
```

| File / concept | Role |
|---|---|
| `media/uploaded_data.json` | Plain-text content of every uploaded document — the **raw material** for the index. |
| `legal_index.faiss` | The **FAISS vector index**: each text chunk turned into a list of numbers (an "embedding"). FAISS searches these very fast to find text with similar meaning. |
| `metadata.pkl` | A Python pickle that **maps each vector back** to its document id, date, staff, and the original text snippet. Without it, search results would be meaningless numbers. |
| `processed_ids.pkl` | Remembers which document ids are **already indexed**, so re-running only adds new documents instead of rebuilding everything. |
| `myapp/semantic.py` | Standalone script that builds/updates the index and runs an **interactive CLI search**. The model used is `all-mpnet-base-v2`. Run with `python myapp/semantic.py`. |
| `myapp/h.py` | An **alternate/experimental** approach using `all-MiniLM-L6-v2` + scikit-learn cosine similarity (no FAISS). Has a hardcoded local path — treat as scratch. |
| in-app search (`views.py` → `ask_question_post`) | The **web** version of the search: loads the FAISS index + metadata and answers questions from the `ask_doubt` page. |

**Plain-English summary:** documents → text → numbers (embeddings) stored in FAISS;
ask a question, it's turned into numbers too, and FAISS returns the documents whose
meaning is closest. `metadata.pkl` translates the matches back into readable
documents.

---

## 9. Large files NOT in git (must be copied manually)

These are excluded from GitHub (too big / regenerable). On a fresh clone they will
be **missing** and must be copied over by hand (USB / cloud drive / zip) into the
**same paths**. See the README's "Large files are NOT in this repository" section.

| File | Location | ~Size | Needed for |
|---|---|---|---|
| `metadata.pkl` | repo root **and** `myapp/` | 326 MB | AI search results |
| `legal_index.faiss` | repo root **and** `myapp/` | 53 MB | AI search |
| `processed_ids.pkl` | repo root | small | incremental indexing |
| `media/uploaded_data.json` | `media/` | 339 MB | building the index |
| `media/*.csv`, `media/*.xlsx` | `media/` | varies | uploaded data |
| `db-aetherai-07-01-26.sql` | repo root | 8 KB | seeding the database |

Without `metadata.pkl` and `legal_index.faiss`, the AI semantic search won't return
results until they're copied over or regenerated by running `myapp/semantic.py`
(which needs `media/uploaded_data.json`).
