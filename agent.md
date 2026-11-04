# Medi Guide — project handoff

Last updated: 5 November 2026. This is a continuity note for a future chat or coding agent. Read `README.md` for user-facing setup and deployment instructions. **Do not put credentials or full authentication callback URLs in this file.**

## Project location and goal

- Current workspace on Windows: `E:\medi-guide\medi-guide`. The previous handoff's `/Users/mayank/medi-guide` path is no longer the active workspace.
- GitHub repository: `https://github.com/MayankSuhag66/Medicare` (`main`). Production URL: `https://medi-care-swart.vercel.app/`.
- Medi Guide is a responsive, educational medical-document companion. It helps people read forms, prescriptions, reports, and medical terminology; it is **not** a doctor, diagnostic device, or clinically validated product.
- The user wants to keep hosting and AI usage on free tiers where possible, use Supabase for authentication/backend data, and deploy to Vercel. Free-tier availability is not guaranteed.
- The project uses static HTML/CSS/vanilla JavaScript and Python's standard library. **No Node/npm or Python package installation is required** for the current implementation.

## Files and responsibilities

| File/path | Purpose |
|---|---|
| `index.html` | HTML entry point, dark-by-default theme bootstrap, favicon link, and Open Graph/Twitter preview metadata. |
| `favicon.ico`, `og-image.png` | Multi-size cross-mark favicon and 1200 × 630 dark-themed social preview. Their root URLs are explicitly allowed by `vercel.json`. |
| `styles.css`, `theme.css` | Responsive light design and dark-theme overrides. Header toggle persists the choice in browser `localStorage`. |
| `app.js` | Hash-based routing/pages, browser OCR, editable results, camera capture, PDF export, chat, Supabase auth (email/password and Google OAuth), saved history, provider selector and theme toggle. |
| `backend.py` | Shared server-side API implementation, local `.env` loader, Supabase token verification, safety prompts, Gemini/Groq/OpenRouter/Cohere integrations. |
| `server.py` | Local static server, delegating `/api/*` to `backend.py`; blocks local access to hidden files and Python source. |
| `api/status.py`, `api/config.py`, `api/chat.py`, `api/analyze.py` | Vercel Python Function entry points. Each declares an explicit top-level `class handler(APIHandler)`; an imported `handler` alias alone is **not** recognized by Vercel. |
| `supabase/schema.sql` | Private `documents` table, grants, and per-user row-level security (RLS) policies. |
| `.env.example` | Template for local environment variables. **Not real credentials.** |
| `.gitignore`, `.vercelignore` | Exclude `.env`, build artifacts, and local state; `.DS_Store` is ignored by Git. |
| `vercel.json` | Explicit `@vercel/python` builds for the four API endpoints, `@vercel/static` allowlist for the six public assets, and API/root routes. Use Framework Preset **Other**. |
| `tests/test_backend.py` | Standard-library unit tests for provider payloads, JSON handling, token checks, OpenRouter free-model guard and Vercel handler entry points. |
| `README.md` | Full local setup, deployment, free-tier cautions, and limitations. |

## Implemented website pages

Home, login, sign up, dashboard, AI Doctor Assistant, Medical Form Scanner, Prescription Analyzer, Medical Report Analyzer, Medical Dictionary, Document History, User Profile, Privacy & Security, About, and Terms/Medical Disclaimer. Navigation is hash-based, e.g. `/#/reports`.

The landing page has hero CTAs, feature cards, how-it-works, benefits, privacy section, FAQ, and footer. The workspace has a sidebar and mobile navigation.

Dark mode is the default when no theme preference has been saved. The sun/moon button in the header switches themes and stores the preference locally. Light and dark home/workspace views and toggle persistence were visually/smoke-tested in headless Edge; this is not a full accessibility audit.

The homepage advertises an absolute `og:image` and Twitter image URL at `https://medi-care-swart.vercel.app/og-image.png`. The static allowlist must include both the image and `/favicon.ico`; otherwise share crawlers and browsers see 404. Social platforms may cache older previews.

## Document and AI flows

- Upload PDF/JPG/JPEG/PNG (15 MB maximum) or capture an image with the camera. Tesseract.js performs image OCR in the browser; PDF.js extracts PDF text or OCRs scanned PDF pages (first five pages). Libraries are loaded from CDNs on demand.
- Without AI, conservative local parsing identifies clearly labeled form fields, simple checkboxes, and some lab values. Prescription details are deliberately left blank rather than guessed. Results and extracted text can be reviewed and corrected.
- Users must **explicitly** click **Analyze with AI (sends text)** to send OCR text to the chosen provider. The backend sends at most 12,000 OCR characters for analysis and 10,000 document-context characters for chat. The four providers are Gemini, Groq, OpenRouter, and Cohere; only configured providers appear in the picker.
- The server returns structured analysis for forms, prescriptions, and reports. The frontend displays warnings, doctor-discussion questions, editable fields/tables, and document follow-up chat. AI output can still be wrong and must be verified against the original.
- Medical dictionary has ten built-in terms. Chat links to MedlinePlus, NHS, and WHO. Emergency phrases produce an immediate emergency-services message. Safety prompts prohibit diagnosis, prescribing, dose changes, invented facts, and definitive image interpretation.
- The form PDF download uses jsPDF and is a **summary of reviewed fields**, not a modified original form.

## Supabase and data handling

- Supabase Auth handles email/password sign-up, sign-in, sign-out, display-name updates, and Google OAuth from both login and sign-up pages. Email verification depends on project settings. Google OAuth is started with `signInWithOAuth({provider: 'google'})`; the browser returns to the same origin with `?auth_callback=google`, then navigates to the dashboard on a valid session. Supabase JS detects sessions from the callback URL.
- **Outstanding production login issue:** a user screenshot showed a Supabase callback landing on `localhost:3000` with an access token in the URL, where no app runs. The likely cause is a Supabase Auth Site URL or redirect allowlist still set to localhost. In **Supabase → Authentication → URL Configuration**, set Site URL to `https://medi-care-swart.vercel.app` and allow `https://medi-care-swart.vercel.app/**`; keep `http://localhost:8000/**` for local testing. Start a fresh login after saving. Google Cloud's authorized redirect URI should be the Supabase project's `https://<project-ref>.supabase.co/auth/v1/callback`, not the Vercel URL. **This external dashboard setting has not been confirmed or fixed from this workspace.** Do not share a full `#access_token=...` URL; if a complete token was exposed, revoke that session.
- The frontend obtains `SUPABASE_URL` and `SUPABASE_ANON_KEY` from `/api/config` and loads Supabase JS from a CDN. These two values are **public configuration**; the anon key is not a server secret. **Never use a `service_role` key in frontend code.**
- AI provider keys exist only in server environment variables. Python API endpoints validate the signed-in user's Supabase access token via Supabase Auth before calling a provider. Do not expose provider keys through `/api/config`, HTML, or browser code.
- Original files are processed in the browser and are not saved to Supabase or uploaded to Python functions. Results stay in the current tab unless the signed-in user explicitly clicks **Save to my account**. Saving stores extracted text, editable result JSON, file name, type, and timestamp in the RLS-protected `documents` table. Saved rows load on sign-in and can be deleted. This is not a certified electronic health record.
- Supabase Auth manages its normal browser session persistence; unsaved document contents exist in app memory only.

## Environment variables

The user created a local `.env`; it is ignored by Git and was **not** pushed. The Python server reads it automatically without `python-dotenv`. Presence checks showed the local Supabase URL and anon key set, and local `/api/status` and `/api/config` returned HTTP 200. Never display, commit, copy, or overwrite `.env` contents. Vercel has separate environment variables; the live `/api/status` currently reports Supabase configured and all four AI providers configured, but that does **not** prove the keys work or that their plans allow production use.

Required for accounts: `SUPABASE_URL`, `SUPABASE_ANON_KEY`. Optional AI keys: `GEMINI_API_KEY`, `GROQ_API_KEY`, `OPENROUTER_API_KEY`, `COHERE_API_KEY`. Optional model overrides: `GEMINI_MODEL`, `GROQ_MODEL`, `OPENROUTER_MODEL`, `COHERE_MODEL`; `APP_URL` is optional for OpenRouter attribution. Defaults are in `.env.example`.

OpenRouter defaults to `openrouter/free`; the backend rejects an override unless it is `openrouter/free` or ends in `:free`. No automatic paid-provider fallback exists. Free-tier limits and policies can change. **Cohere's free evaluation key is not a guaranteed free production plan.** Gemini and other free providers may have data-use terms unsuitable for sensitive patient information; review policies before sending real medical data.

## Run, test, and deploy

1. Run `supabase/schema.sql` in the Supabase SQL Editor if it has not already been applied. Execution of the schema against the user's project has **not** been verified. Configure Supabase Auth Site URL and allowed redirects as above.
2. Run `python server.py` in the project root on Windows and open `http://localhost:8000/#/login`. Do not open `index.html` directly or use a static-only server: the page requires `/api/status` and `/api/config`.
3. Run `$env:PYTHONDONTWRITEBYTECODE='1'; python -m unittest discover -s tests -v` in PowerShell. **Five tests passed** after the Vercel handler fix. `node --check app.js` passed. The local API returned HTTP 200 for status/config; real Google/email login, saving to Supabase, AI-provider calls, and document processing have **not** been verified end to end on production.
4. For Vercel, use the GitHub repo root with Framework Preset **Other**, no custom build command or output-directory override, and the repository's `vercel.json`. Set Vercel Production environment variables separately and redeploy after changes. The `builds` warning that dashboard build settings do not apply is expected because the config intentionally uses explicit builders.
5. Production health checks (last checked 5 November 2026): `https://medi-care-swart.vercel.app/api/status` returned HTTP 200 with `supabaseConfigured: true`, `aiAvailable: true`, and providers `gemini`, `groq`, `openrouter`, `cohere`; `/backend.py` returned 404. Do **not** paste `/api/config` output because it contains public Supabase configuration, and never paste secret keys or OAuth callback tokens.

## Deployment and Git history

- The initial Vercel deployment treated the entire repository as static assets: `/api/status` and `/api/config` were 404, while `/backend.py` and `/api/status.py` were publicly served. Explicit builders and the static allowlist in `vercel.json` fixed this. The next build failed with `PYTHON_ENTRYPOINT_NOT_FOUND` because `from backend import APIHandler as handler` was not accepted; explicit top-level `handler` subclasses in all four API files fixed it.
- Python-function fix commit: `f090cbe` (`Expose explicit Vercel Python handler classes`); check `git log -1` for the current HEAD after later asset changes. Earlier commits `6c86a41` and `874acde` were authored under a different local Git identity; published history was **not** rewritten.
- This repository's **local** Git identity is configured as `Mayank Suhag <mayank25bcam016@ncuindia.edu>` for future commits after the user reported that Vercel blocked the previous author's identity. Do not change global Git identity or force-push without permission. Check the author **and committer** before pushing, and confirm the email is verified on the GitHub account with Vercel access if a deployment is blocked.

## Important future-work cautions

- Keep health claims cautious; never silently invent missing medical information or treat OCR/AI output as verified fact.
- Preserve explicit user consent before sending document text to an AI provider or saving it in Supabase.
- Protect RLS policies and keep provider keys server-side. Avoid accidentally turning on paid models or claiming that any service is unlimited/free forever.
- For handling real patient data, investigate consent, security, retention, deletion, regional privacy requirements, and provider data-use agreements. The current app has **not** been assessed for HIPAA, GDPR, or other regulated-health-data compliance.
- If deployment fails, first inspect the build log and Resources/Functions for all four Python handlers; verify `/api/status` returns JSON and `/backend.py` stays 404. A `Ready` static-only deployment is insufficient. Do not rewrite API routes to serve `.py` files as static assets.
- The next likely user task is correcting the **Supabase Auth redirect** away from `localhost:3000` and testing a fresh Google/email flow on the Vercel domain. This is separate from the now-working Vercel API deployment.
