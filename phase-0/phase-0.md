# Phase 0 — Manual Quality Validation

**Duration:** 2–3 days
**Cost:** <$30 (HeyGen Creator $29, everything else free tier)
**Goal:** Validate which video format produces credible, clickable output before writing any product code
**Status:** Complete

Do not write product code until this phase is complete. The only output that matters here is signal about format quality and which tools to build around.

---

## Findings Summary

| Finding | Detail |
|---------|--------|
| **Best video tool** | Seedance 2 via TopView.ai video agent |
| **Audio** | ElevenLabs outperforms Seedance 2 native audio |
| **Best format** | B-roll of user or product + voiceover or text overlay (no lip sync required) |
| **Talking head** | Did not perform well enough — deprioritize |
| **Green screen** | Did not work — do not use |
| **Text in video** | Seedance 2 cannot render text reliably — requires separate text overlay step post-generation |
| **Recommended pipeline** | Generate ElevenLabs audio → generate Seedance video without audio → combine in post |

---

## Step 1 — Find 5 Pet Products (1–2 hours)

*Completed as planned.*

Find 5 real Shopify pet product stores. These should be early-stage founders — not established brands. Ideal: stores with limited social presence, static image ads, or founders posting about marketing struggles.

**Where to find them:**
- r/shopify, r/ecommerce — search "pet product" or "dog/cat product" + recent posts
- Twitter/X — search "shopify pet" or "built a pet brand" in the last 30 days
- Just browse Shopify stores: search Google for `site:myshopify.com "dog"` or `site:myshopify.com "pet"`

**What you're looking for:**
- Pet product with a clear use case (slow feeder, lick mat, slicker brush, calming supplement, portable water bottle)
- Shopify product page with at least 3 product images and some customer reviews
- Product that tells a transformation story ("before and after" for pet health, behavior, or appearance)

For each product, save:
- Product URL
- Product name
- 3–5 bullet points describing the core benefits (from their page)
- Top 3 customer reviews (copy the text)
- All product images (download them)

---

## Step 2 — Generate Scripts (1 hour)

*Completed as planned. Scripts saved in `scripts.md`.*

For each of the 4 products, generate a script using this Claude prompt. Paste it into claude.ai:

```
You are writing a 30-second UGC-style video ad script for a pet product.

Product name: [NAME]
Product description: [PASTE DESCRIPTION]
Core benefits: [PASTE BULLET POINTS]
Real customer reviews: [PASTE TOP 3 REVIEWS]
Target audience: Pet owners, women 25–45, emotionally engaged with their animal's health and wellbeing

Write a 30-second script (~75 words) in this format:
1. Hook (problem): 1–2 sentences. Start with the pet's problem or the owner's frustration. Use language from the reviews if possible.
2. Transformation: 1–2 sentences. What changed after using the product. Specific, not generic.
3. CTA: 1 sentence. Direct but natural — avoid "link in bio", use "if your dog does X, you need to try this."

Rules:
- Never use the words "game changer", "amazing", "love this", or "obsessed"
- Use natural conversational speech, not ad copy
- Reference the specific pet problem and product benefit — no generic claims
- Write as if a real pet owner is talking to their phone camera
```

Generate 2 script variants per product. Save all 10 scripts. See `scripts.md` for the final versions with full Kling/Seedance prompts built out.

**Note on script quality:** Products with real customer reviews (1–3) produced noticeably stronger scripts. Products without reviews (4–5) felt generic. Prioritize review-rich products in future phases.

---

## Step 3 — Generate Voiceovers (1 hour)

*Completed as planned. ElevenLabs confirmed as the preferred audio source.*

In ElevenLabs, generate a voiceover for each script.

**Voice selection:** Browse their stock voices and pick 1–2 that fit the demographic — warm, conversational woman in her 30s. Suggested voices to test: "Rachel", "Bella", or search "conversational" in their voice library.

**Settings:**
- Style: Conversational (not Narration)
- Stability: 0.5 (allows some natural variation)
- Similarity boost: 0.75

Download each as an MP3. Label them `product1-script1.mp3`, etc.

**Finding:** ElevenLabs audio quality was noticeably better than Seedance 2's native audio generation. Going forward, always generate audio in ElevenLabs first and bring it into Seedance rather than using Seedance's built-in audio.

---

## Step 4 — Produce Videos (actual process)

*Deviated from original plan. HeyGen and CapCut were not used. Full Seedance 2 workflow used instead.*

**Tool:** TopView.ai video agent running Seedance 2.

**Process:**
1. Paste product reference photos directly into TopView.ai
2. Build a detailed video prompt for the agent based on the scripts in `scripts.md` — include shot list, camera style, audio direction, and avatar description
3. Seedance 2 generates 1–3 clips per prompt and stitches them together
4. Evaluate output quality and iterate on the prompt if needed

**What was tested:**

| Format | Result |
|--------|--------|
| Talking head (creator speaks to camera) | Acceptable quality but not good enough — deprioritize |
| Green screen (creator + background image/video) | Did not work — do not use |
| B-roll + voiceover | ✅ Best results — use this |
| POV / first-person | ✅ Works well — use this |
| Follow-me / over-the-shoulder | ✅ Works well — use this |
| Aesthetic b-roll + text overlay | ✅ Works — but requires separate text overlay step (see below) |

**Text overlay note:** Seedance 2 cannot reliably render text inside video frames. Any format that calls for on-screen text requires a separate tool to apply text overlays after video generation. This is a build requirement for Phase 1.

**Recommended pipeline going forward:**
1. Generate ElevenLabs audio from script
2. Generate Seedance 2 video without audio, using detailed prompt from `scripts.md`
3. Combine audio and video in post
4. Apply any text overlays as a final step

---

## Step 5 — Evaluate Output

*Evaluated qualitatively rather than through formal user testing.*

Original plan called for showing videos to 20 people and asking "would you stop scrolling." This was replaced with direct qualitative evaluation of format viability based on production output.

**Key signal:** Any format requiring lip sync (talking head, green screen) produced output that read as AI. Formats that avoid lip sync entirely (b-roll, POV, follow-me, aesthetic) produced output that cleared the quality bar.

---

## Phase 0 Exit Criteria

- [x] Videos produced across all 4 products
- [x] Multiple formats tested per product
- [x] Winning format identified: b-roll + voiceover, no lip sync
- [x] Failing formats identified: talking head, green screen
- [x] Primary tool identified: Seedance 2 via TopView.ai
- [x] Audio tool confirmed: ElevenLabs
- [x] Script prompt refined and saved in `scripts.md`
- [x] Build requirements identified: text overlay tool, ElevenLabs → Seedance pipeline
- [x] Decision made: proceed to Phase 1

Phase 1 should be built around the Seedance 2 pipeline. Do not build a HeyGen integration.
