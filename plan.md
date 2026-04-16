# AI UGC Platform — Build Plan

**Product:** Fully automated pipeline: Shopify product URL → ready-to-run UGC-style video ads
**Beachhead:** Pet product founders on Shopify doing <$10k/month revenue
**Target price:** $99–199/month SaaS, no human in the loop

---

## Phase 0 — Manual Quality Validation
**Duration:** 2–3 days
**Goal:** Validate which video format produces credible, clickable output before writing any product code

- Pick 5 real pet product Shopify stores from Reddit/Twitter
- Generate 3 format variants per product (talking-head, text-on-screen, lifestyle b-roll)
- Show outputs to 20 people, ask "would you stop scrolling for this?"
- Identify which format(s) clear the quality bar
- Identify which avatar/voice combination is most credible

**Tools:** HeyGen web UI, ElevenLabs, CapCut, Pexels, Claude (script generation)

**Gate to Phase 1:** At least one format consistently passes the scroll-stop test across all 5 products.

→ See [phase-0.md](phase-0.md) for detailed execution plan

---

## Phase 1 — Pipeline Script
**Duration:** 1–2 weeks
**Goal:** End-to-end automated pipeline as a Python CLI. One command in, MP4 out. No web app yet.

```
python generate.py --url "https://yourstore.myshopify.com/products/xyz"
```

### Stage 1 — Shopify Scraper
- Playwright-based scraper (JS-rendered pages require headless browser)
- Extract: product images (all angles, high-res), description, bullet points, customer reviews, price, product name
- Reviews are the highest-signal input for script authenticity — prioritize extracting them
- Output: structured JSON with all product assets

### Stage 2 — Script Generation
- Feed scraped data to Claude API with a tight system prompt
- Format: problem → transformation → CTA (30 seconds = ~75 words)
- Force the LLM to use language from actual reviews — prevents generic output
- Demographic-aware: match script tone to likely buyer (pet product buyers skew women 25–45)
- Generate 3 script variants per product, select best programmatically or use all 3

### Stage 3 — Avatar + Voiceover
- ElevenLabs API: generate voiceover from script first
- HeyGen API v3: upload ElevenLabs audio as custom voiceover, select stock avatar
- Avatar selection: hardcode 2–3 avatars validated in Phase 0 (skip dynamic selection for MVP)
- Output: raw avatar video file

### Stage 4 — Video Composition
- FFmpeg + Python for full control (not a video SaaS)
- Assemble: avatar video + scraped product images as B-roll + auto-captions + royalty-free music
- Auto-caption via Whisper (transcribe ElevenLabs audio, burn in captions)
- B-roll timing: cut to product image on noun/product mentions in script
- Output: two files — 9:16 MP4 (TikTok, 15–30s) and 1:1 MP4 (Meta feed)
- Music: Pixabay or Free Music Archive for MVP

**Gate to Phase 2:** Pipeline produces a complete MP4 from URL input without manual intervention.

---

## Phase 2 — Stress Test
**Duration:** 3–5 days
**Goal:** Run 50+ pet product URLs through the pipeline. Fix failure modes before adding a UI.

Failure modes to catch:
- Script hallucinations (LLM inventing claims not on the product page)
- Avatar-script demographic mismatch
- Composition failures (bad cuts, music clash, caption timing)
- Generation time (target: under 5 minutes per video)
- Scraper failures (products with unusual Shopify themes or missing images)

**Gate to Phase 3:** Pipeline produces acceptable output on >80% of URLs without manual intervention. Generation time under 5 minutes.

---

## Phase 3 — Minimal Web Interface
**Duration:** 1 week
**Goal:** Wrap the pipeline in a single-page web app. Email delivery. No dashboard.

**Stack:** Next.js, async job queue (BullMQ or similar), email delivery (Resend)

**The user flow:**
1. Single form: product URL + optional benefit bullets (3–5 sentences) + target audience (one sentence)
2. Submit → job queued → "We'll email you when your videos are ready" confirmation
3. Generation runs async (3–5 min)
4. Email with secure download link → 2–3 MP4 files

**What is not being built:**
- Dashboard or video history
- Script editing interface
- Avatar selection UI
- Brand kit, logo overlay, color matching
- Analytics or performance tracking
- Direct platform publishing
- Team or agency accounts
- Auth (use magic link or no-auth download URLs for MVP)

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

## Open Questions (Pre-Build)

- **Pricing sensitivity:** Would a founder at $0–$5k/month revenue pay $99/month? Or does it need to be $49? Answer before setting price — talk to 20 of them.
- **Avatar shortlist:** Which 2–3 HeyGen stock avatars pass the Phase 0 credibility test for pet product buyers?
- **Script prompt:** Which Claude system prompt variant produces the most specific, non-generic scripts from Shopify data?
- **Gadget vertical timing:** When does Runway/Kling quality on physical objects improve enough to add gadgets as a second vertical?
