# AI UGC Platform — Build Plan

**Product:** Fully automated pipeline: Shopify product URL → ready-to-run UGC-style video ads
**Beachhead:** Founders who've hit the UGC wall — cost, creator flakiness, or complexity
**Pricing:** $6/generation pay-as-you-go → ~$49/month subscription for volume users (10+ videos/month)
**Unit economics:** ~$2.50–3 COGS per generation, ~50–58% gross margin

---

## Phase 0 — Manual Quality Validation
**Status:** Complete
**Findings:** See [phase-0/phase-0.md](phase-0/phase-0.md) for full findings.

**Key outputs:**
- Seedance 2 is the only viable video generation model tested — accessed via TopView.ai manually in Phase 0
- Talking head and green screen formats do not work — eliminated from pipeline
- Winning format: b-roll of product/user + ElevenLabs voiceover, no lip sync required
- ElevenLabs audio outperforms Seedance native audio — always generate audio separately
- Seedance cannot render text reliably — text overlays must be applied post-generation
- Pipeline order: ElevenLabs audio → Seedance video (no audio) → FFmpeg combine → text overlay

**Gate passed:** B-roll + voiceover format produces credible output across all 4 tested products.

→ See [phase-0/phase-0.md](phase-0/phase-0.md) and [phase-0/scripts.md](phase-0/scripts.md)

---

## Phase 1 — Pipeline Script
**Status:** Complete (core pipeline working end-to-end)
**Goal:** End-to-end automated pipeline as a Python CLI. One command in, MP4 out. No web app yet.

```
python generate.py --url "https://yourstore.myshopify.com/products/xyz"
```

Flags:
- `--run-id <id>` — skip Stage 1, resume from an existing run
- `--stage <1-6>` — run a single stage in isolation (for debugging)
- `--n-scripts <n>` — number of script variants to generate (default: 1)
- `--skip-reviews` — skip Playwright review scraping

**Video generation API:** Seedance 2 via Replicate. Accepts reference images per generation call. Cost is per-second of generated video.

---

### Stage 1 — Shopify Scraper

- Playwright-based scraper (JS-rendered pages require headless browser)
- Extracts: all product images (high-res), description, bullet points, customer reviews, price, product name
- Also downloads first 15s of product demo video if present — used in Stage 3 for mechanics extraction
- Reviews are the highest-signal input for script authenticity — if a product has no reviews, flagged in output and warned to user
- Output: structured JSON with all product assets + image files saved to disk under `output/runs/<run_id>/`

---

### Stage 2 — Script Generation

- GPT-5.5
- 10 script types defined in `pipeline/knowledge/script_types.json`: Pattern Interrupt, Curiosity Gap, Social Proof, PAS, Before/After, Educational, Personal Story, Comparison, Urgency/Scarcity, Aspirational Identity
- Script type is selected randomly per run; `--n-scripts 2` selects two distinct types
- Format: 55–70 spoken words, ElevenLabs v3 emotion/delivery tags embedded inline (e.g. `[matter-of-fact]`, `[warm]`, `[thoughtful pause]`)
- CTA is type-specific — each script type has its own CTA guidance in `script_types.json`, no hardcoded formula
- Output: JSON per script variant + plain text file, summary `scripts.json`

---

### Stage 3 — Video Prompt Generation

Three Claude calls per run:

**Call 1 — Reference image selection:** GPT-5.4 reviews up to 8 product images and picks the single clearest product shot (plain background preferred). This image is used as the Seedance reference in Stage 5.

**Call 2 — Product mechanics extraction (if video present):** GPT-5.4 extracts frames from the product demo video and describes in 2–3 sentences exactly how the product is physically used — step by step hand actions, what opens/closes/pours. Used to prevent Seedance from generating physically impossible sequences.

**Call 3 — Chunk prompt generation:** GPT-5.5 generates 3 Seedance chunk prompts covering the full video. Each chunk is one Seedance API call (max 9.5s). Chunks support multiple cuts within a single generation using `| CUT |` as separator. Every shot specifies: subject, action, camera angle, movement, lighting, setting.

The system prompt encodes all Phase 0 learnings: POV/b-roll only, no presenter to camera, handheld shake movement, lived-in environments, lighting must be imperfect, hard cuts only, TikTok safe zone awareness, physical sequences must be fully described step by step.

**Default format:** POV/b-roll + voiceover. No talking head. No green screen. No lip sync.

- Output: JSON per script variant + summary `video_prompts.json`

---

### Stage 4 — Voiceover Generation

- ElevenLabs v3 model (`eleven_v3`) — supports inline emotion and delivery tags from Stage 2 scripts
- Voice persona fetched from ElevenLabs API (gender, age, accent) and passed to Stage 2 and Stage 3 so scripts and shot descriptions match the voice
- Audio duration drives video chunk length in Stage 5
- Output: MP3 per script variant + `audio.json` with duration

---

### Stage 5 — Video Generation

- Seedance 2 via Replicate (`bytedance/seedance-2.0`), 480p, 9:16, no audio
- Reference image pre-processing: gpt-image-2 edits the Claude-selected reference image to remove small text and fine print from product labels before sending to Seedance. Image is resized to ≤1024px before upload to stay within API limits.
- 3 chunks per video, durations distributed from actual audio length and rounded up to nearest valid Seedance value (4, 5, 6, 8, 10, 12, 15s)
- Reference video chaining: each chunk's output is passed as `reference_videos` input to the next chunk, improving visual consistency across cuts
- Retry logic: up to 2 retries per chunk with 15s/30s backoff on failure
- Clips stitched with FFmpeg `-c copy` immediately after all chunks complete
- Output: individual chunk MP4s + stitched silent MP4 per variant + `video.json`

---

### Stage 6 — Composition

FFmpeg handles everything — no SaaS video editor.

**Steps:**
1. Transcribe MP3 via OpenAI Whisper (`whisper-1`) — word-level timestamps
2. GPT-5.4 identifies ~15% of words with highest emotional impact — these render at larger font size (pop effect)
3. Burn word-by-word captions: uppercase, bold white, black outline, 1 word at a time, ASS format, timed to Whisper output
4. FFmpeg: combine silent video + voiceover, trim to exact audio duration, burn captions, encode H.264/AAC
5. Output: 9:16 MP4 per script variant

**Not yet implemented:** background music, 1:1 Meta feed export, text overlays from Stage 3 prompts.

**Output:** 1 MP4 per script variant (default run = 1 final video)

**Gate to Phase 2:** Pipeline produces a complete MP4 from a URL input without manual intervention. End-to-end generation time under 10 minutes.

---

## Phase 2 — Stress Test
**Duration:** 3–5 days
**Goal:** Run 50+ pet product URLs through the pipeline. Fix failure modes before adding a UI.

| Failure mode | What to look for |
|---|---|
| Script hallucinations | LLM inventing claims not on the product page |
| Weak prompts for review-poor products | Flag rather than silently producing bad video |
| Shot prompt quality variance | Does Claude produce consistently good per-shot prompts or does it drift? |
| Stitching artifacts | Jarring cuts, mismatched lighting between shots |
| Composition failures | Bad audio sync, caption timing errors, music clash |
| Scraper failures | Unusual Shopify themes, missing images, paywalled review widgets |
| Generation time | Target under 5 minutes end-to-end |
| Video API reliability | Rate limits, failure rates, retry behavior |
| Knowledge file gaps | Are there failure patterns the MD files don't account for? Update them. |

**Known limitation — mechanically novel products:** Products with a design patent or non-obvious physical mechanism (e.g. a one-hand poop scooper) produce poor video quality when no product demo video is present. Seedance generates motion from learned priors — if the product's mechanic is novel, it invents the wrong motion or produces something generic. No prompt tuning fixes this; a real demo video is required as input. Phase 2 should quantify how common this failure mode is and inform whether to add an upfront warning or hard gate for products without a video.

Run on at least:
- 20 products with strong reviews (3+ reviews, specific language)
- 20 products with weak or no reviews
- 10 products with unusual image sets (few images, low resolution, no lifestyle shots)
- 10 mechanically novel products (design patents, multi-step mechanisms) — split between those with and without a product demo video

**Gate to Phase 3:** Pipeline produces acceptable output on >80% of URLs without manual intervention. Generation time under 5 minutes. Failure modes logged and categorized.

---

## Phase 3 — Minimal Web Interface
**Status:** Complete
**Goal:** Wrap the pipeline in a single-page web app. Status-polling download page. Auth. No payments yet.

**Stack:**
- **Next.js 14 (App Router)** — frontend hosted on Vercel. Single form, 4s polling, download UI.
- **FastAPI** — REST API. Receives submissions, enqueues Celery tasks, serves job status and S3 download URLs.
- **Celery** — Python worker. Imports and runs the pipeline directly. Writes progress to Redis on each stage completion.
- **Redis** — Celery broker + per-job progress store (`job:{id}:progress` key, 2hr TTL).
- **PostgreSQL** — job and user storage via SQLAlchemy. Required for multi-container access (API + worker are separate Railway services, so SQLite won't work).
- **AWS S3** — output file storage. Worker uploads final MP4s after composition; API returns presigned download URLs (1hr expiry). Required because API and worker have separate container filesystems.
- **Auth** — Google OAuth via FastAPI. Backend exchanges code → issues JWT → redirects to frontend with token in query param. Frontend stores token in localStorage.
- **Hosting** — Railway (two services: API + Celery worker) + Redis plugin + PostgreSQL plugin. Next.js on Vercel.

**The user flow:**
1. User hits landing page → clicks "Sign in with Google"
2. Google OAuth handled entirely by FastAPI backend
3. JWT issued, user redirected to `/auth/callback?token=...` on Vercel frontend
4. Frontend stores token, redirects to `/dashboard`
5. User pastes Shopify product URL → submits → job queued
6. Status page polls `/jobs/{id}` every 4s, shows stage progress bar (6 stages)
7. On completion, download button appears — clicks generate a presigned S3 URL, browser downloads MP4 directly from S3

**Key implementation details:**
- `railway.toml` only sets `dockerfilePath` and `restartPolicyType` — start commands set per-service in Railway UI to avoid both services using the same command
- API start: `sh -c 'uvicorn api.main:app --host 0.0.0.0 --port $PORT'`
- Worker start: `celery -A api.celery_app worker --loglevel=info`
- `DATABASE_URL` uses `postgres://` → `postgresql://` rewrite at config load time (SQLAlchemy 2.0 requirement)
- `check_same_thread` connect arg stripped for PostgreSQL connections
- All LLM calls use OpenAI (gpt-5.5 for Opus-equivalent, gpt-5.4 for Haiku-equivalent) — Anthropic API reserved for Claude Code

**What is not being built:**
- Script editing interface
- Voice or avatar selection
- Format selection UI (POV/b-roll only)
- Brand kit, logo overlay, color matching
- Analytics or performance tracking
- Direct platform publishing
- Team or agency accounts
- Email delivery
- Payments

**Gate to Phase 3 complete:** A logged-in user can go from URL to downloaded MP4 without any manual intervention.

---

## Phase 4 — Distribution
**Duration:** Ongoing, starting before Phase 3 is complete
**Goal:** First 10 paying customers using "Show Don't Tell" strategy

**Positioning (product and inbound):**
Center on the pain stage, not a vertical. The customer is any founder who has hit the UGC wall — cost, creator flakiness, or complexity. That pain is identical whether they sell dog brushes or supplements. Product copy, landing page examples, and framing should speak to that moment, not to pet products specifically. Pet products were useful for pipeline testing but are not the product's identity. Hair-on-fire customers self-select through the copy regardless of what they sell.

**Outbound — find the fire:**
Scan Reddit and Twitter for posts where founders are actively in pain: complaining about UGC costs, creator no-shows, ad creative fatigue, or not knowing where to start. These are the hair-on-fire moments. When you find one:
1. Scrape their Shopify URL, run it through the pipeline
2. DM them with the video already made:
   *"Noticed you're scaling ads for [product]. I'm building an AI tool that automates UGC creation for bootstrapped stores. Ran your site through the beta — built this in 3 minutes. Want the unwatermarked version to test on Meta? It's $6 — I'll send you the link."*
3. The watermarked demo is free — that's the hook. The self-serve product charges $6 from generation one. Someone who won't pay $6 after seeing a working demo isn't the hair-on-fire customer.

**Inbound — start the fire where you already have presence:**
Distribution needs a community focus, not a vertical focus. The right starting community is wherever you actually have presence — Twitter/X founder community first. Post about building this, show output, document what works. Founders who follow builders on Twitter are disproportionately early adopters watching the AI tools space. Reddit (r/ecommerce, r/dropshipping) is a second channel once you have early results to show — works through targeted "show don't tell" replies to specific posts, not through building a presence.

**Outbound channels (scan for hair-on-fire posts):**
- Reddit: r/dropshipping, r/ecommerce, r/shopify
- Twitter/X: founders posting about ad creative problems
- Discord: Ecom Guild, Demand Curve, Online Geniuses
- Indie Hackers: founders posting about marketing failures

**Avoid:**
- Shopify Community forums (heavily moderated, ban risk)
- Facebook groups (low signal, dropshipping spam)
- Pet product communities specifically — no presence there, and the vertical restriction isn't needed

**Sequence — what to build and when:**

1. **Start outbound DMs immediately — no landing page needed.** The DM script does the selling. The watermarked video of their own product is the landing page. Send them directly to the app (Google login → paste link → generate). A landing page between the DM and the app adds a step — don't add it.

2. **Build a minimal one-pager (one day) in parallel.** Required before posting on X or Reddit — inbound readers land with zero context, and a bare Google login screen loses everyone. The entire page is:
   - Headline: what it does in one sentence ("Paste your Shopify URL. Get a UGC video ad in 3 minutes.")
   - One or two example output videos
   - Price: "$6/video. No subscription."
   - Login/CTA button
   Don't innovate on the landing page — innovation energy goes on the pipeline.

3. **Post on X/Reddit only after the first 2–3 paying customers from outbound.** First paying customer validates the product is worth $6. That's the signal you want before driving inbound traffic anywhere.

---

## Revenue Milestones

| Milestone | Signal | Notes |
|-----------|--------|-------|
| Alive | 10 paying generations | Validate $6 converts after seeing demo — no hesitation = hair-on-fire |
| Traction | 50 generations/month | Word of mouth starting; some founders hitting volume → offer $49/month |
| Ramen | 200 generations/month | ~$1.2k/month gross, ~$600–700 after COGS |
| Real | 1k generations/month | ~$6k/month gross; subscription tier doing real work |

---

## Open Questions

- **$6 conversion friction:** Does $6 hesitate or convert cleanly after seeing a demo? Answer by watching drop-off behavior after launch — not by asking beforehand.
- **Subscription migration trigger:** At what generation volume do users ask for the subscription? Hypothesis: 10+/month. Watch for it and offer proactively.
- **Second format timing:** 10 generations of the same product felt visually similar — format-level problem, not script variation. Direct talking-head is the first post-launch format addition. Add when users ask for it.
- **Gadget vertical timing:** When does Seedance quality on physical objects in motion improve enough to add gadgets? Monitor quarterly.
