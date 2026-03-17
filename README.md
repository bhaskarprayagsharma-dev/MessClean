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
4. Copy the **Sheet ID** from the sheet URL: `https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit`.
5. Set environment variables (or use `.streamlit/secrets.toml` for local dev):
   - **GOOGLE_SHEETS_CREDENTIALS_JSON** — path to the service account JSON file.
   - **FEEDBACK_SHEET_ID** — the Sheet ID from step 4.

If these are not set, feedback is still collected and stored in **data/feedback.json**.

## Google OAuth setup (optional – “Continue with Google”)

Sign-in with Google is optional for MVP. To enable it:

1. In [Google Cloud Console](https://console.cloud.google.com/), create OAuth 2.0 credentials (Web application).
2. Add the **authorized redirect URI**: your app URL (e.g. `https://your-app.onstreamlit.app/` for Streamlit Cloud).
3. Set environment variables:
   - **GOOGLE_CLIENT_ID** — OAuth client ID
   - **GOOGLE_CLIENT_SECRET** — OAuth client secret

The current code shows a “Continue with Google” tab; the actual OAuth redirect flow still needs to be implemented (e.g. with `streamlit-oauth` or a custom callback). Until then, users can use **Continue with email** (name, age, country, email); data is stored in **data/users.json**.

## Before launch

1. In **utils/report_builder.py**, set **APP_URL** (and optionally APP_NAME / APP_DESCRIPTION) to your live app URL.
2. Run from the project root so **assets/styles.css** and **assets/logo.png** are found.
3. Configure Google Sheet (and optionally OAuth) as above if you want feedback in a sheet and Google sign-in.

## Limits

- Max file size: 50MB. Best for files under 100,000 rows.
