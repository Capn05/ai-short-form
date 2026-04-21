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
**Duration:** 2–3 weeks
**Goal:** End-to-end automated pipeline as a Python CLI. One command in, MP4 out. No web app yet.

```
python generate.py --url "https://yourstore.myshopify.com/products/xyz"
```

The pipeline has six sequential stages. Each stage outputs a file that the next stage consumes. Every stage should be independently runnable for debugging.

**Pre-Phase 1 task:** Identify and validate the video generation API before writing any pipeline code. TopView.ai was used manually in Phase 0 but their API pricing is prohibitive. Evaluate cheaper alternatives with Seedance 2 access (Fal.ai, Replicate, Segmind, or direct Seedance API). Confirm: Does the API accept reference images? What are per-generation costs and rate limits? This is the highest-priority unknown.

---

### Stage 1 — Shopify Scraper

- Playwright-based scraper (JS-rendered pages require headless browser)
- Extract: all product images (high-res), description, bullet points, customer reviews, price, product name
- Reviews are the highest-signal input for script authenticity — if a product has no reviews, flag it in the output JSON
- Output: structured JSON with all product assets + image files saved to disk

---

### Stage 2 — Script Generation

- Feed scraped JSON to Claude API
- System prompt forces the model to use language pulled directly from real reviews — prevents generic output
- Format: problem → transformation → CTA (~75 words, 30 seconds spoken)
- CTA should be natural, not "link in bio" — e.g. "if your dog eats too fast, you need to try this"
- Generate 2 script variants per product; keep both, let Stage 3 run on both in parallel
- Output: 2 script text files

**Note on products without reviews:** Phase 0 confirmed that scripts for review-poor products are noticeably weaker. Surface a warning in the output and prompt the user to provide 2–3 customer testimonials manually if reviews are unavailable.

---

### Stage 3 — Video Prompt Generation

Phase 0 proved that Seedance 2 requires detailed, structured prompts to produce good output. Shot lists, camera style per shot, lighting, setting, and audio direction all materially affect quality. This stage is where the "agent" logic that TopView.ai handled manually gets built and automated.

**What this stage builds:**

Claude receives the script, product type, and product images, and outputs a complete Seedance-ready video prompt that includes:
- Total shot count (typically 4–7 shots to cover the audio duration)
- Per-shot description: camera angle, subject, action, composition, lighting
- Stitching cues: each shot is written so the cut to the next shot is seamless (matching setting, lighting, and presence)
- Audio direction: voiceover tone and pacing notes
- Any text overlay cues with approximate timing (e.g. "text appears at 0:04: 'there has to be a better way'")

**Character consistency:** The winning format (POV/b-roll, no recurring face) sidesteps the hardest consistency problem. Because the "character" is hands and perspective rather than a face, shots only need to match on setting and lighting — which is enforced through the prompt. No reference frame tracking required.

**Source-of-truth knowledge files:** Claude's system prompt for this stage includes a set of curated MD files that encode what makes videos work. These live in `pipeline/knowledge/` and are loaded into the system prompt at generation time. Starting set:

- `hooks.md` — principles for stop-scroll first 3 seconds, hook structures that work by product type, what to avoid
- `shot-guidelines.md` — format-specific shot composition rules for each supported format (POV, follow-me, first-person, aesthetic b-roll), lighting principles, pacing
- `voiceover-tone.md` — delivery tone guidelines by product category, friend voice note principles, CTA language that converts without sounding like an ad

These files are the codified learnings from Phase 0 and should be updated after every batch of new video generation. They are the mechanism for quality improvement over time without rewriting pipeline code.

**Default format:** POV/b-roll + voiceover. Hardcoded in Phase 1. No talking head. No green screen. No lip sync under any circumstances.

- Output: 2 video prompt text files (one per script variant)

---

### Stage 4 — Voiceover Generation

- ElevenLabs API: generate voiceover from script text
- Voice selection: warm, conversational woman in her 30s — hardcode 1–2 validated voices at launch
- Settings: Conversational style, Stability 0.5, Similarity boost 0.75
- Generate audio first — video length in Stage 5 is determined by audio duration
- Output: MP3 file per script variant + duration in seconds

---

### Stage 5 — Video Generation

- Seedance 2 via cheaper API (to be validated pre-Phase 1 — see note above)
- Input: per-shot prompts from Stage 3 + product reference images from Stage 1 + audio duration from Stage 4
- Generate each shot as a separate API call — 4–7 calls per video
- Each shot is generated without audio
- Stitch shots in order using FFmpeg immediately after generation — do not wait for all shots before stitching
- Total video duration should match or slightly exceed audio duration
- Output: single stitched silent MP4 per script variant

**Why per-shot generation instead of one prompt:** Shorter generations per call produce higher quality output from Seedance 2. TopView.ai's agent used this approach in Phase 0 — multiple clips per prompt, then stitch. Building it explicitly gives full control over shot length, order, and stitching logic.

---

### Stage 6 — Composition

FFmpeg handles everything — no SaaS video editor.

**Steps:**
1. Combine stitched silent video (Stage 5) + voiceover MP3 (Stage 4) — sync audio to video start
2. Trim or pad video to exactly match audio length
3. Transcribe ElevenLabs MP3 via Whisper — output word-level timestamps
4. Burn captions: bold white text, centered, large, TikTok native style, timed to Whisper output
5. Apply text overlay blocks from Stage 3 prompt — parse overlay cues, render at specified timing
6. Add royalty-free background music at low volume under voiceover (Pixabay or Free Music Archive)
7. Export: 9:16 MP4 (TikTok/Reels, 15–30s) and 1:1 MP4 (Meta feed)

**Output:** 2 formats × 2 script variants = 4 MP4 files per product URL run

**Gate to Phase 2:** Pipeline produces 4 complete MP4 files from a URL input without manual intervention. End-to-end generation time under 5 minutes.

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

Run on at least:
- 20 products with strong reviews (3+ reviews, specific language)
- 20 products with weak or no reviews
- 10 products with unusual image sets (few images, low resolution, no lifestyle shots)

**Gate to Phase 3:** Pipeline produces acceptable output on >80% of URLs without manual intervention. Generation time under 5 minutes. Failure modes logged and categorized.

---

## Phase 3 — Minimal Web Interface
**Duration:** 1–2 weeks
**Goal:** Wrap the pipeline in a single-page web app. Email delivery. Format selection. No dashboard.

**Stack:** Next.js, async job queue (BullMQ), email delivery (Resend)

**The user flow:**
1. Single form:
   - Product URL (required)
   - Optional: 3–5 benefit bullets
   - Optional: one sentence on target audience
   - Video style: choose a format or leave on auto
2. Submit → job queued → "We'll email you when your videos are ready"
3. Generation runs async (3–5 min)
4. Email with secure download link → 4 MP4 files

**Format selection UI:** Show 3–4 tiles with a short visual preview clip and a one-line description for each format. Not a dropdown — founders need to see what a format looks like before they can pick it. Include an "Auto" option (defaults to POV/b-roll) for founders who don't want to decide.

Supported formats at Phase 3 launch:
- **Auto** (POV/b-roll + voiceover) — works for everything
- **POV / b-roll** — product shown close-up from the user's perspective, voiceover
- **Follow-me** — creator filmed from behind or side profile, walking with the product, voiceover
- **Aesthetic b-roll** — slow, cinematic single shot + text overlay, trending audio

**What is not being built:**
- Dashboard or video history
- Script editing interface
- Voice or avatar selection
- Brand kit, logo overlay, color matching
- Analytics or performance tracking
- Direct platform publishing
- Team or agency accounts
- Auth (magic link or no-auth download URLs for MVP)

**Gate to Phase 3 complete:** A founder can go from URL to downloaded MP4 without talking to anyone.

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
