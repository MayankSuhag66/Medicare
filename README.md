# Medi Guide

A medical-document companion with in-browser OCR, optional AI explanations, Supabase authentication and opt-in saved history. **Educational prototype only; not a medical device or a substitute for a clinician.**

## Local setup (Python 3.9+, no npm required)

1. Copy `.env.example` to `.env`. Fill in `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and one or more provider API keys. **Never add the Supabase `service_role` key or an AI key to frontend code.**
2. Run `supabase/schema.sql` in your Supabase project's SQL Editor. It creates a private per-user `documents` table with row-level security (RLS). Only extracted text you explicitly choose to save is stored; original files remain in the browser.
3. Set Supabase **Authentication → URL Configuration → Site URL** to your local or deployed URL. Add `http://localhost:8000/**` and your Vercel URL to allowed redirect URLs. If email confirmation is enabled, users must confirm before signing in.
4. Run `python3 server.py`, then open http://localhost:8000. The Python server reads `.env` automatically, without a third-party dotenv package.

### Google sign-in (optional)

The **Continue with Google** button on both sign-in and sign-up uses Supabase Auth. It does not need a Google client secret in this project's `.env` or frontend code.

1. In Google Cloud Console, create an OAuth client of type **Web application**. Add `https://<your-supabase-project-ref>.supabase.co/auth/v1/callback` as an authorized redirect URI (use your project's actual Supabase callback URL).
2. In **Supabase → Authentication → Providers → Google**, enable Google and enter that client's ID and secret. Keep the secret in Supabase, never in this repo.
3. In **Supabase → Authentication → URL Configuration**, allow `http://localhost:8000/**` and `https://<your-vercel-domain>/**` as redirect URLs. The app returns to `/?auth_callback=google` on each origin and then opens the dashboard.

If the Google OAuth app is in testing mode, add your test Google accounts in Google Cloud Console. Google sign-in will not work until the provider and redirect URLs are configured; email/password sign-in remains available.

## Deploy to Vercel

Import this folder as a Vercel project with **Framework Preset: Other** and **Root Directory: this folder**. Do not set a build command or output directory. `vercel.json` explicitly builds the four `api/*.py` Python Functions and only the HTML/CSS/JS, favicon and social-preview image as static files; server source, SQL and project notes must not be publicly served. The functions share the same `backend.py` logic as the local server. After deploying, `/api/status` must return JSON (not a 404), and `/backend.py` must return 404.

In **Vercel → Project Settings → Environment Variables**, add the values from `.env.example` for Production (and Preview if needed), then redeploy. **Vercel does not read your local `.env` at deployment time.** Keep `.env` untracked; `.gitignore` and `.vercelignore` exclude it. `SUPABASE_URL` and `SUPABASE_ANON_KEY` are public configuration returned via `/api/config`; this is how browser Supabase Auth works. The anon key is *not* a secret. RLS is essential. AI keys are server-only and are never returned to the browser.

Set Supabase's Site URL and allowed redirect URLs to your real Vercel domain. Turn on email confirmation and appropriate abuse-prevention settings in Supabase Auth. Vercel Functions use HTTPS in production. The app has not been assessed for HIPAA/GDPR or other regulated health-data compliance.

Vercel and Supabase also have free-plan quotas. A public deployment is not guaranteed to stay free as traffic grows; monitor all dashboards and disable paid upgrades if a strict zero-cost budget is required.

## Optional AI providers

Configure any combination in `.env` locally and in Vercel Environment Variables when deployed:

| Provider | Key variable | Default model | Important |
|---|---|---|---|
| Google Gemini | `GEMINI_API_KEY` | `gemini-3.1-flash-lite` | Free tier subject to changing quotas and data-use terms. If `GEMINI_MODEL` is set in Vercel, update it there too and redeploy. |
| Groq | `GROQ_API_KEY` | `llama-3.3-70b-versatile` | Free plan has rate limits. |
| OpenRouter | `OPENROUTER_API_KEY` | `openrouter/free` | Routes only to free models; daily limits and provider privacy policies vary. |
| Cohere | `COHERE_API_KEY` | `command-r7b-12-2024` | Free evaluation/trial keys are **not** a production free tier; verify licensing before using in a public deployment. |

Optional overrides: `GEMINI_MODEL`, `GROQ_MODEL`, `OPENROUTER_MODEL`, `COHERE_MODEL`, `APP_URL`. Choose only free-tier models if you want to avoid provider charges. No automatic fallback to a paid model exists. Free-tier access is **not unlimited or guaranteed**; track usage and quotas in each provider dashboard. In particular, free providers may use prompts to improve their products—do **not** send sensitive patient data until you have reviewed their terms and have an appropriate legal basis.
The OpenRouter integration refuses models other than `openrouter/free` or IDs ending in `:free` to prevent accidental paid routing.

AI calls require a signed-in Supabase user. The server validates each access token with Supabase Auth, then proxies the request to the selected provider. Uploaded original files never pass through these Python Functions; AI receives only extracted OCR text when a user explicitly requests analysis or sends a document question. No API key is placed in the browser or Supabase table.

## Capabilities and limitations

- The site starts in dark mode. Use the sun/moon button in the header to switch themes; your choice is remembered in this browser.
- The browser tab uses `favicon.ico`. Shared links use a 1200 × 630 `og-image.png` with Open Graph and Twitter Card metadata; crawlers may cache previews, so updates may not appear immediately.
- Browser OCR uses Tesseract.js and PDF.js; PDF export uses jsPDF. These, Supabase JS, fonts, and the homepage image load from third-party hosts. Internet access is required for these features.
- PDF/JPG/PNG up to 15 MB; first five PDF pages processed. AI analysis sends at most the first 12,000 OCR characters; document chat sends at most 10,000 context characters.
- Unsaved results remain only in memory for the current tab. Saved history stores extracted text, name, editable result, and document type in Supabase with RLS. Original files are never saved. Deleting saved history removes the row from Supabase.
- Scans and AI can make mistakes. Verify every field against the source. High/low flags are displayed only when present in the source; the app does not diagnose, prescribe, change doses, or interpret medical images.
- Form PDF export is a **reviewed field summary**, not a modified copy of the original form.
- For emergencies, contact local emergency services immediately.
