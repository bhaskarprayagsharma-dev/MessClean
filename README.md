# MessClean – Excel Data Cleaner

Fix messy Excel files in seconds: clean quantities, currency, percentages, dates, remove duplicates and empty columns, and detect summary rows. Review each change before applying, then download a cleaned workbook with an embedded report.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the URL shown (usually http://localhost:8501). Use the **Upload & Clean** button in the top bar (sidebar is hidden).

## Logo and navigation

- The app logo lives in **assets/logo.png**. To replace it, overwrite this file; the logo is rendered as a link and will keep working.
- **Logo link:** Clicking the logo uses the query param `?go=home`. On the upload page, that is handled at the top of the script and triggers `st.switch_page("app.py")`.
- **Homepage CTA:** The inline “Upload & Clean” text in the green CTA box is a link with `?navigate=upload`. At the top of **app.py**, that param is checked and triggers `st.switch_page("pages/1_Upload_and_Clean.py")`.

## Project structure

- **app.py** — Home page and Streamlit entry point
- **pages/** — Upload and Clean flow (requires sign-in)
- **modules/** — Pipeline, tool registry, metadata, sheet parsing
- **tools/** — Cleaning tools
- **utils/** — Nav, auth gate, feedback-to-sheet, report builder, file validation
- **assets/** — Styles (styles.css), logo (logo.png), feature images (feature_*.png)

## Google Sheet setup (feedback for “Fill feedback to download”)

When users choose “Fill feedback to download”, their responses are appended to a Google Sheet (or, if not configured, to **data/feedback.json**).

1. Create a Google Cloud project and enable the **Google Sheets API**.
2. Create a **service account** and download its JSON key. Put the key file somewhere safe (e.g. project root or a secrets folder).
3. Create a Google Sheet and share it with the **service account email** (from the JSON key, e.g. `xxx@yyy.iam.gserviceaccount.com`) with “Editor” access.
4. Copy the **Sheet ID** from the sheet URL: `https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit`. (The app defaults to the MessClean Feedback sheet if you don’t set this.)
5. In Streamlit Community Cloud, set **Secrets** (recommended):
   - **FEEDBACK_SHEET_ID** — optional; if omitted, the default MessClean Feedback sheet is used.
   - **GOOGLE_SERVICE_ACCOUNT_JSON** — paste the entire service account JSON contents (use triple quotes in secrets).

   Example:

   ```toml
   FEEDBACK_SHEET_ID = "YOUR_SHEET_ID"
   GOOGLE_SERVICE_ACCOUNT_JSON = """
   { ...service account json... }
   """
   ```

   Local dev alternative:
   - **GOOGLE_SHEETS_CREDENTIALS_JSON** — file path to the service account JSON (on your machine).
   - **FEEDBACK_SHEET_ID** — the Sheet ID from step 4.

If these are not set, feedback is still collected and stored in **data/feedback.json**.

## Google OAuth (“Continue with Google”)

The app uses OAuth 2.0 with a callback on the **main page** (`app.py`), then sends the user to **Upload & Clean**.

1. In [Google Cloud Console](https://console.cloud.google.com/), **OAuth consent screen** (External) + **Test users** while in testing.
2. **Credentials** → OAuth **Web application** client.
3. **Authorized JavaScript origins**: `https://YOUR-APP.streamlit.app` (no path, no trailing slash).
4. **Authorized redirect URIs**: **exactly** your app root, e.g. `https://YOUR-APP.streamlit.app/` (trailing slash must match what you put in secrets).
5. In Streamlit **Secrets** (or env):

   ```toml
   GOOGLE_CLIENT_ID = "....apps.googleusercontent.com"
   GOOGLE_CLIENT_SECRET = "GOCSPX-..."
   GOOGLE_OAUTH_REDIRECT_URI = "https://YOUR-APP.streamlit.app/"
   ```

   `GOOGLE_OAUTH_REDIRECT_URI` must be **identical** to the redirect URI in Google Cloud (including `/` at the end if you use it).

6. Dependency: `google-auth-oauthlib` (see `requirements.txt`).

**Email sign-up** still works without OAuth; data is stored in **data/users.json**.

## Before launch

1. In **utils/report_builder.py**, set **APP_URL** (and optionally APP_NAME / APP_DESCRIPTION) to your live app URL.
2. Run from the project root so **assets/styles.css** and **assets/logo.png** are found.
3. Configure Google Sheet (and optionally OAuth) as above if you want feedback in a sheet and Google sign-in.

## Limits

- Max file size: 50MB. Best for files under 100,000 rows.
