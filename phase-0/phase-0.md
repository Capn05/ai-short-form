# Phase 0 — Manual Quality Validation

**Duration:** 2–3 days
**Cost:** <$30 (HeyGen Creator $29, everything else free tier)
**Goal:** Validate which video format produces credible, clickable output before writing any product code

Do not write product code until this phase is complete. The only output that matters here is signal about format quality and which tools to build around.

---

## Setup (Day 0, ~2 hours)

Sign up and get familiar with:

| Tool | Purpose | Cost |
|------|---------|------|
| [HeyGen](https://heygen.com) | Talking-head avatar generation | $29/month Creator |
| [ElevenLabs](https://elevenlabs.io) | Voiceover generation | Free tier (10k chars/month) |
| [CapCut](https://capcut.com) | Video assembly, captions, music | Free |
| [Pexels](https://pexels.com) | Stock lifestyle footage | Free |
| [Claude](https://claude.ai) | Script generation | Free tier or existing access |

---

## Step 1 — Find 5 Pet Products (1–2 hours)

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

For each of the 5 products, generate a script using this Claude prompt. Paste it into claude.ai:

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
3. CTA: 1 sentence. Direct. "Link in bio" or "Check it out below."

Rules:
- Never use the words "game changer", "amazing", "love this", or "obsessed"
- Use natural conversational speech, not ad copy
- Reference the specific pet problem and product benefit — no generic claims
- Write as if a real pet owner is talking to their phone camera
```

Generate 2 script variants per product (run the prompt twice with slightly different benefit emphasis). Pick the better one. Save all 10 scripts.

---

## Step 3 — Generate Voiceovers (1 hour)

In ElevenLabs, generate a voiceover for each of the 10 scripts.

**Voice selection:** Browse their stock voices and pick 1–2 that fit the demographic — warm, conversational woman in her 30s. Suggested voices to test: "Rachel", "Bella", or search "conversational" in their voice library.

**Settings:**
- Style: Conversational (not Narration)
- Stability: 0.5 (allows some natural variation)
- Similarity boost: 0.75

Download each as an MP3. Label them `product1-script1.mp3`, etc.

---

## Step 4 — Produce 3 Format Variants Per Product

For each of the 5 products, produce all 3 formats using the same script and voiceover. This is the core of Phase 0 — you're comparing formats, not products.

---

### Format A: Talking-Head Avatar (HeyGen)

1. In HeyGen, go to Create Video → Avatar Video
2. Select a stock avatar — test these demographic types:
   - White woman, 30s, warm/approachable
   - Latina woman, 30s, energetic
   - Black woman, 30s, direct/trustworthy
   Pick 2–3 to test across your 5 products
3. Upload your ElevenLabs MP3 as the custom audio (do not use HeyGen's built-in TTS)
4. Set background to plain/neutral or a simple indoor environment
5. Export at 9:16 aspect ratio
6. In CapCut: add product images as B-roll overlay (cut in during "transformation" section), add auto-captions, add quiet background music

**What you're evaluating:** Does the avatar feel like a real person? Is the lip-sync credible? Does it feel like UGC or clearly AI?

---

### Format B: Text-on-Screen + Voiceover

1. Open CapCut → New Project → 9:16
2. Import your product images as clips (2–3 seconds each, total ~30 seconds of images)
3. Import your ElevenLabs MP3 as audio
4. Use CapCut's Auto Captions feature — this generates word-by-word captions timed to the audio
5. Style captions: bold white text, centered, large (think TikTok native style)
6. Add background music at low volume under the voiceover
7. Add 1–2 text callouts for the product name and key benefit (not in the caption — a separate text element)
8. Export 9:16

**What you're evaluating:** Does this feel like a real UGC ad or a generic slideshow? Does the voiceover carry enough trust without a face?

---

### Format C: Lifestyle B-Roll + Voiceover

1. Go to Pexels and download 4–6 clips of relevant lifestyle footage. Search: "dog owner", "dog playing", "pet care", "dog walk", "cat owner" — whatever fits the product
2. Open CapCut → New Project → 9:16
3. Import lifestyle clips + your ElevenLabs MP3
4. Edit clips to match the voiceover rhythm (problem section → sad/frustrated footage, transformation → happy pet footage)
5. Add auto-captions, background music, export
6. Note: the footage will not be product-specific — that's the point. You're testing whether the format style works despite generic assets.

**What you're evaluating:** Does lifestyle b-roll feel more authentic than avatar? Does the mismatch between generic footage and specific product hurt credibility?

---

## Step 5 — The Test (1–2 hours)

You now have 15 videos (5 products × 3 formats).

Show them to 20 people. This doesn't need to be formal — friends, family, Twitter followers, Discord communities you're in. The people should not be professional marketers or familiar with how AI UGC works.

**For each video, ask one question only:**
> "If this appeared in your TikTok or Instagram feed, would you stop scrolling and watch it? Yes or no."

Do not ask about production quality, whether it looks AI-generated, or whether they'd buy the product. Just: stop scrolling or not.

Track responses in a simple table:

| Product | Format A (Avatar) | Format B (Text) | Format C (Lifestyle) |
|---------|-------------------|-----------------|----------------------|
| Product 1 | Y/N | Y/N | Y/N |
| Product 2 | Y/N | Y/N | Y/N |
| Product 3 | Y/N | Y/N | Y/N |
| Product 4 | Y/N | Y/N | Y/N |
| Product 5 | Y/N | Y/N | Y/N |

---

## What to Do With the Results

**If Format A (avatar) wins consistently:** Build the pipeline around HeyGen + ElevenLabs. Lip-sync quality is sufficient. Note which avatar demographic performed best.

**If Format B (text-on-screen) wins:** The pipeline doesn't need an avatar API at all. Cheaper, simpler, faster to build. Primary output becomes voiceover + product images + captions.

**If Format C (lifestyle) wins:** You have a sourcing problem. Full automation requires either real footage (founders don't have it) or AI-generated footage (quality too low currently). This result means the format works but the pipeline can't deliver it automatically — file it as a future vertical.

**If nothing wins:** The quality bar isn't cleared. Do not proceed to Phase 1. Diagnose: is it the script quality, the voiceover, the avatar, the composition? Fix the weakest link and retest before building anything.

**Most likely result:** Format A and Format B both win for different reasons. Format A feels more trustworthy (human face), Format B feels more native to the platform (fast-paced, text-heavy). Build both as outputs from a single pipeline run.

---

## Phase 0 Exit Criteria

- [ ] 15 videos produced (5 products × 3 formats)
- [ ] Shown to at least 20 people
- [ ] At least one format scores >60% "yes" across all 5 products
- [ ] Avatar shortlist identified: 2–3 HeyGen stock avatars that tested best
- [ ] Script prompt variant identified: which Claude prompt produced the most specific, non-generic output
- [ ] Decision made: which format(s) to build in Phase 1

Do not start Phase 1 until all exit criteria are met.
