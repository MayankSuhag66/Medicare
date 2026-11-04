# Medi Guide — project handoff

Last updated: 5 November 2026. This file is a continuity note for a future chat or coding agent. Read `README.md` for user-facing setup and deployment instructions.

## Project location and goal

- Project root: `/Users/mayank/medi-guide`.
- Medi Guide is a responsive, educational medical-document companion. It helps people read forms, prescriptions, reports, and medical terminology; it is **not** a doctor, diagnostic device, or clinically validated product.
- The user wants to keep hosting and AI usage on free tiers where possible, use Supabase for authentication/backend data, and deploy to Vercel.
- The project uses static HTML/CSS/vanilla JavaScript and Python's standard library. **No Node/npm or Python package installation is required** for the current implementation.

## Files and responsibilities

| File/path | Purpose |
|---|---|
| `index.html` | HTML entry point and page metadata. |
| `styles.css` | Responsive healthcare design, landing page, workspace, tools, auth, chat, mobile layouts. |
| `app.js` | Hash-based frontend routing, all pages, browser OCR, editable results, camera capture, PDF export, chat, Supabase client/auth/history, provider selector. |
| `backend.py` | Shared server-side API implementation, local `.env` loader, Supabase token verification, safety prompts, Gemini/Groq/OpenRouter/Cohere integrations. |
| `server.py` | Local static server, delegating `/api/*` to `backend.py`; blocks local access to hidden files and Python source. |
| `api/status.py`, `api/config.py`, `api/chat.py`, `api/analyze.py` | Vercel Python Function entry points importing the shared API handler. |
| `supabase/schema.sql` | Private `documents` table, grants, and per-user row-level security (RLS) policies. |
| `.env.example` | Template for local environment variables. **Not real credentials.** |
| `.gitignore`, `.vercelignore` | Exclude `.env`, build artifacts, and local state. |
| `vercel.json` | Minimal Vercel project configuration; use Framework Preset **Other**. |
| `tests/test_backend.py` | Standard-library unit tests for provider payloads, JSON handling, token checks, and OpenRouter free-model guard. |
| `README.md` | Full local setup, deployment, free-tier cautions, and limitations. |

## Implemented website pages

Home, login, sign up, dashboard, AI Doctor Assistant, Medical Form Scanner, Prescription Analyzer, Medical Report Analyzer, Medical Dictionary, Document History, User Profile, Privacy & Security, About, and Terms/Medical Disclaimer. Navigation is hash-based, e.g. `/#/reports`.

The landing page has hero CTAs, feature cards, how-it-works, benefits, privacy section, FAQ, and footer. The workspace has a sidebar and mobile navigation.

## Document and AI flows

- Upload PDF/JPG/JPEG/PNG (15 MB maximum) or capture an image with the camera. Tesseract.js performs image OCR in the browser; PDF.js extracts PDF text or OCRs scanned PDF pages (first five pages). Libraries are loaded from CDNs on demand.
- Without AI, conservative local parsing identifies clearly labeled form fields, simple checkboxes, and some lab values. Prescription details are deliberately left blank rather than guessed. Results and extracted text can be reviewed and corrected.
- Users must **explicitly** click **Analyze with AI (sends text)** to send OCR text to the chosen provider. The backend sends at most 12,000 OCR characters for analysis and 10,000 document-context characters for chat. The four providers are Gemini, Groq, OpenRouter, and Cohere; only configured providers appear in the picker.
- The server returns structured analysis for forms, prescriptions, and reports. The frontend displays warnings, doctor-discussion questions, editable fields/tables, and document follow-up chat. AI output can still be wrong and must be verified against the original.
- Medical dictionary has ten built-in terms. Chat links to MedlinePlus, NHS, and WHO. Emergency phrases produce an immediate emergency-services message. Safety prompts prohibit diagnosis, prescribing, dose changes, invented facts, and definitive image interpretation.
- The form PDF download uses jsPDF and is a **summary of reviewed fields**, not a modified original form.

## Supabase and data handling

- Supabase Auth handles email/password sign-up, sign-in, sign-out, and display-name updates. Email verification depends on project settings.
- The frontend obtains `SUPABASE_URL` and `SUPABASE_ANON_KEY` from `/api/config` and loads Supabase JS from a CDN. These two values are **public configuration**; the anon key is not a server secret. **Never use a `service_role` key in frontend code.**
- AI provider keys exist only in server environment variables. Python API endpoints validate the signed-in user's Supabase access token via Supabase Auth before calling a provider. Do not expose provider keys through `/api/config`, HTML, or browser code.
- Original files are processed in the browser and are not saved to Supabase or uploaded to Python functions. Results stay in the current tab unless the signed-in user explicitly clicks **Save to my account**. Saving stores extracted text, editable result JSON, file name, type, and timestamp in the RLS-protected `documents` table. Saved rows load on sign-in and can be deleted. This is not a certified electronic health record.
- Supabase Auth manages its normal browser session persistence; unsaved document contents exist in app memory only.

## Environment variables

Local setup: copy `.env.example` to `.env` and fill in values. The Python server reads `.env` automatically without `python-dotenv`. As of this handoff, **no `.env` file or real keys were created by the agent**. Check whether the user has created one before changing it; never display or commit its contents.

Required for accounts: `SUPABASE_URL`, `SUPABASE_ANON_KEY`. Optional AI keys: `GEMINI_API_KEY`, `GROQ_API_KEY`, `OPENROUTER_API_KEY`, `COHERE_API_KEY`. Optional model overrides: `GEMINI_MODEL`, `GROQ_MODEL`, `OPENROUTER_MODEL`, `COHERE_MODEL`; `APP_URL` is optional for OpenRouter attribution. Defaults are in `.env.example`.

OpenRouter defaults to `openrouter/free`; the backend rejects an override unless it is `openrouter/free` or ends in `:free`. No automatic paid-provider fallback exists. Free-tier limits and policies can change. **Cohere's free evaluation key is not a guaranteed free production plan.** Gemini and other free providers may have data-use terms unsuitable for sensitive patient information; review policies before sending real medical data.

## Run, test, and deploy

1. Create `.env` from `.env.example` and add user-supplied values.
2. Execute `supabase/schema.sql` in Supabase SQL Editor (the SQL is intended to be run once); configure Supabase Auth Site URL and allowed redirect URLs for local and Vercel domains.
3. Run `python3 server.py` from the project root, then open `http://localhost:8000`.
4. Run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`. Four backend tests passed at handoff. Frontend routes were smoke-tested in headless Chrome, and local API status/config/auth-guard responses were checked with curl. **Actual provider calls, real Supabase credentials, and Vercel deployment have not been end-to-end tested** because no user credentials were provided.
5. For Vercel, import this folder with Framework Preset **Other** and no build/output command. Set environment variables in **Vercel Project Settings → Environment Variables**, then redeploy. A local `.env` is not automatically transferred to Vercel. Add the deployed domain to Supabase allowed redirect URLs.

## Important future-work cautions

- Keep health claims cautious; never silently invent missing medical information or treat OCR/AI output as verified fact.
- Preserve explicit user consent before sending document text to an AI provider or saving it in Supabase.
- Protect RLS policies and keep provider keys server-side. Avoid accidentally turning on paid models or claiming that any service is unlimited/free forever.
- For handling real patient data, investigate consent, security, retention, deletion, regional privacy requirements, and provider data-use agreements. The current app has **not** been assessed for HIPAA, GDPR, or other regulated-health-data compliance.
- If deployments fail, verify Vercel's Python Function imports from `backend.py` and that all four `/api/*` routes are live. There is no deployed URL or verified production instance yet.
