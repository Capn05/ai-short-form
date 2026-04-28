# AI UGC Platform — Build Plan

**Product:** Fully automated pipeline: Shopify product URL → ready-to-run UGC-style video ads
**Beachhead:** Pet product founders on Shopify doing <$10k/month revenue
**Target price:** $99–199/month SaaS, no human in the loop

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

- Claude Opus 4 with adaptive thinking
- 10 script types defined in `pipeline/knowledge/script_types.json`: Pattern Interrupt, Curiosity Gap, Social Proof, PAS, Before/After, Educational, Personal Story, Comparison, Urgency/Scarcity, Aspirational Identity
- Script type is selected randomly per run; `--n-scripts 2` selects two distinct types
- Format: 55–70 spoken words, ElevenLabs v3 emotion/delivery tags embedded inline (e.g. `[matter-of-fact]`, `[warm]`, `[thoughtful pause]`)
- CTA is type-specific — each script type has its own CTA guidance in `script_types.json`, no hardcoded formula
- Output: JSON per script variant + plain text file, summary `scripts.json`

---

### Stage 3 — Video Prompt Generation

Three Claude calls per run:

**Call 1 — Reference image selection:** Claude Haiku reviews up to 8 product images and picks the single clearest product shot (plain background preferred). This image is used as the Seedance reference in Stage 5.

**Call 2 — Product mechanics extraction (if video present):** Claude Haiku extracts frames from the product demo video and describes in 2–3 sentences exactly how the product is physically used — step by step hand actions, what opens/closes/pours. Used to prevent Seedance from generating physically impossible sequences.

**Call 3 — Chunk prompt generation:** Claude Opus 4 with adaptive thinking generates 3 Seedance chunk prompts covering the full video. Each chunk is one Seedance API call (max 9.5s). Chunks support multiple cuts within a single generation using `| CUT |` as separator. Every shot specifies: subject, action, camera angle, movement, lighting, setting.

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
2. Claude Haiku identifies ~15% of words with highest emotional impact — these render at larger font size (pop effect)
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
**Duration:** 1–2 weeks
**Goal:** Wrap the pipeline in a single-page web app. Status-polling download page. Auth. No payments yet.

**Stack:**
- **Next.js** — frontend (single form, status polling, download UI). Decoupled from backend — can evolve independently.
- **FastAPI** — REST API. Receives submissions, enqueues Celery tasks, serves job status and file downloads.
- **Celery** — Python worker. Imports and runs the pipeline directly (no subprocess). Updates job state in Redis on completion/failure.
- **Redis** — job queue (Celery broker) + job state storage (Celery result backend). No separate database needed for Phase 3.
- **Auth** — JWT or session-based via FastAPI. No payments.
- **Hosting** — Railway. Single repo, three processes (FastAPI, Celery worker, Redis) configured via `railway.toml`. Billed on resource usage — cheap at low volume when the Celery worker is mostly idle.

**The user flow:**
1. User logs in
2. Single form:
   - Product URL (required)
   - Optional: 3–5 benefit bullets
   - Optional: one sentence on target audience
3. Submit → job queued → status page shows "generating..." with live progress
4. Status page flips to download button when complete — user downloads MP4 directly, no email

**Job state tracked in Redis per job:**
- Job ID
- Status (queued / running / done / failed)
- Run directory path
- User ID
- Timestamp

**What is not being built:**
- Dashboard or video history
- Script editing interface
- Voice or avatar selection
- Format selection UI (POV/b-roll only for Phase 3)
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

**The outreach playbook:**
1. Find a pet product founder on Reddit or Twitter complaining about ads, UGC costs, or not getting traction
2. Scrape their Shopify URL, run it through the pipeline manually
3. DM them with the watermarked video already made:
   *"Noticed you're scaling ads for [product]. I'm building an AI tool that automates UGC creation for bootstrapped stores. Ran your site through the beta — built this in 3 minutes. Want the unwatermarked version to test on Meta? Free, just want feedback."*
4. Free offer: first 3 videos, no credit card

**Primary channels:**
- Reddit: r/dropshipping (239k+), r/ecommerce, r/shopify
- Twitter/X: founders building pet brands in public
- Discord: Ecom Guild, Demand Curve, Online Geniuses
- Indie Hackers: founders posting about marketing failures

**Avoid:**
- Shopify Community forums (heavily moderated, ban risk)
- Facebook groups (low signal, dropshipping spam)

---

## Revenue Milestones

| Milestone | Customers | MRR | Notes |
|-----------|-----------|-----|-------|
| Alive | 10 | ~$1.5k | Validate quality floor + willingness to pay |
| Ramen | 50 | ~$7.5k | Word of mouth starting in founder communities |
| Real | 200 | ~$30k | Expand to gadget vertical |
| Meaningful | 500 | ~$75k | Mid-market pricing tier, usage-based expansion |

---

## Open Questions

- **Video generation API:** Which API provides Seedance 2 access at viable cost (Fal.ai, Replicate, Segmind, or direct)? Does it accept reference images per shot? What are per-generation costs? Answer before writing Phase 1 code.
- **Knowledge file content:** What specifically goes in hooks.md, shot-guidelines.md, and voiceover-tone.md at launch? Draft these before Stage 3 implementation — they are the system prompt for the most uncertain stage.
- **Per-shot prompt structure:** What is the right schema for a machine-readable shot prompt that Claude outputs and Stage 5 can parse reliably? Design this interface before implementing either stage.
- **Pricing sensitivity:** Would a pet product founder at $0–$5k/month pay $99/month? Or $49? Talk to 20 of them before setting the price.
- **Gadget vertical timing:** When does Seedance quality on physical objects in motion improve enough to add gadgets? Monitor quarterly.
