# voiceover-tone.md — Voiceover Delivery, Pacing, and Tonal Principles

**Purpose:** System prompt reference for Stage 4 (voiceover generation) and Stage 3 (video prompt generation). This file encodes how the voiceover should sound, what delivery characteristics convert in short-form pet product ads, and what to instruct ElevenLabs and what to write in the prompt's audio direction section.

---

## 1. The Single Most Important Principle: Friend, Not Announcer

The voiceover for this format is not a commercial narrator. It is not a spokesperson. It is not an influencer performing enthusiasm. It is a person talking to their phone as if recording a voice note to send to a friend who asked for a product recommendation.

This is not a creative preference — it is the dominant format that outperforms polished narration in short-form UGC ads across multiple data points:

- UGC posts achieve 6.9x more engagement than brand-generated content (industry analysis, AdCreative.ai)
- UGC-style video (creator-filmed, less polished) outperforms produced video for cold-traffic prospecting because it feels native to the feed
- Native audio ads achieve 53% higher recall and 39% higher purchase intent than traditional polished audio ads (AdsWizz research, cited by industry sources)
- Audio tone impacts purchase intent by up to 43% more than visuals alone (Nielsen audio advertising research, 2024)
- When brands make TikTok-first content — including content that feels authentic to the platform — 74% of viewers say it catches their attention and it drives 3.3x more action than off-platform content repurposed for TikTok (TikTok for Business research)

**The diagnosis test:** Read the script aloud. If it sounds like something a professional announcer would say, rewrite it. If it sounds like something you'd say to a friend who texted "what should I get my dog for X?", it's right.

---

## 2. Tonal Profile — The Target Voice Character

**The voice persona for all pet product ads in this pipeline:**

A woman in her early-to-mid 30s. Warm but not gushing. Direct but not flat. Slightly amused by her own story — she finds it mildly funny or mildly surprising that something worked this well, and she's sharing that genuine reaction. She is not performing for the camera (there is no camera). She is narrating over clips she already filmed.

This is the "I finally found something that actually works" voice. Not the "Oh my GOD this product changed my LIFE" voice. The difference is energy level and authenticity signal.

**Tonal qualities in priority order:**
1. **Conversational** — sounds like speech, not writing. Contractions, natural pauses, slightly incomplete sentence structures are correct.
2. **Warm** — genuine care about the animal comes through in how the story is told, not through performed enthusiasm
3. **Grounded** — not dramatic. Not breathless. The product worked, she's reporting it, she finds it worth sharing.
4. **Slightly wry/dry** — the best-performing pet product scripts have a mild "can you believe this worked?" undercurrent. Not sarcastic. Not detached. Just slightly amused by the specificity of the result.
5. **Confident** — knows the recommendation she's making. No hedging. "You need to try this" not "you might want to consider trying this."

**What this is NOT:**
- High-energy influencer voice ("Okay so I NEED to talk about this")
- Formal narrator voice ("Introducing the revolutionary new...")
- Corporate announcement voice ("This product is designed to...")
- Over-enthusiastic testimonial voice ("I am OBSESSED with this")
- Whisper/ASMR voice (wrong category, wrong energy)

---

## 3. Speech Rate — Data-Backed Targets

**Research finding (Journal of Advertising Research, 2019 — "Do Your Ads Talk Too Fast To Your Audio Audience?"):**
- Optimal speech rate for listener comprehension and recall in audio advertising: 170–190 words per minute
- Peak: 180 wpm produces the highest skin conductance levels (physiological arousal) and attention
- Above 190 wpm: comprehension drops 17–25% due to cognitive overload (Cognitive Load Theory, Sweller 1988)
- Below 150 wpm: sounds too slow, unnatural, loses engagement

**Research finding (University of Missouri / ScienceDirect, 2025):**
- Most broadly acceptable speech rate for comprehension across diverse audiences: 150–160 wpm
- Above 180 wpm: brain cannot fully decode incoming speech stream reliably

**Target for this pipeline:**
- **Ideal: 150–170 wpm** — slightly below the "maximum attention" peak to allow for natural pauses and comprehension in a noisy, distraction-rich mobile environment
- A 75-word script at 150 wpm = 30 seconds. A 75-word script at 180 wpm = 25 seconds. Both are in-spec.
- **Never exceed 180 wpm** in the final output. Flag to ElevenLabs settings if the generated audio is too fast.

**Practical implication for ElevenLabs:**
- ElevenLabs Stability setting: 0.5 (allows natural variation; too high makes speech robotic)
- ElevenLabs Similarity boost: 0.75
- Style: Conversational (not Narration)
- These settings produce natural rate variation — the voice speeds up slightly for casual phrases and slows for emphasis, which is correct. Do not lock it to a fixed rate.

---

## 4. Pauses — The Most Underused Conversion Tool

Natural pauses are a deliberate structural tool, not a flaw in the delivery. They serve three functions:
1. Allow the viewer's brain to process what was just said before the next claim arrives
2. Create natural "beat" moments that align with visual cuts in the video
3. Signal authenticity — a prepared commercial script has no pauses; a person talking does

**Where to pause:**
- After the hook line — let the problem statement land before moving to the transformation
- Before the CTA — a beat of silence before "if your dog does X, you need to try this" makes the CTA feel considered, not rushed
- After a specific number — "forty minutes" + [pause] is more impactful than "forty minutes and she wasn't done"

**ElevenLabs pause technique:** Use em-dashes (—) or ellipses (...) in the script to instruct ElevenLabs to insert natural pauses. Test: "Forty minutes — and she still wasn't done." The em-dash produces a 200–400ms natural pause in most ElevenLabs voice settings.

**Target pause structure in a 30-second script:**
- 1 pause after the hook (0.3–0.5 seconds)
- 1–2 pauses within the transformation (at natural breath points)
- 1 pause before the CTA
- Total silence budget: approximately 2–3 seconds across a 30-second script

---

## 5. Gender and Voice Matching — What the Research Actually Shows

**Research finding (ResearchGate: "Male and Female Voices in Commercials: Analysis of Effectiveness, Adequacy for the Product, Attention and Recall"):**
- Gender alone is a weaker predictor of ad effectiveness than previously assumed
- The practice of preferring male voices is not supported by objective effectiveness data
- **Vocal pitch** has a more significant effect than gender on unaided recall
- **Low-pitched female voices** generate more favorable attitudes toward the ad and the brand
- **Gender-product matching** enhances memorability and effectiveness: matching the perceived gender of the voice to the demographic the product is primarily for produces better results

**Research finding (Journal of Marketing Research, 2024 — "The Power of AI-Generated Voices"):**
- Digital vocal tract length shapes product congruency and ad performance
- Voices perceived as matching the product category (warmth for a pet care product, authority for a technical product) outperform category-mismatched voices regardless of gender

**Application to this pipeline:**

Pet product ads targeting women 25–45 (primary demographic for pet product purchasers):
- **Use:** Warm, low-to-mid-pitched female voice in her 30s
- **Why:** Gender matches the primary demographic; warmth matches the emotional tone of the category; slightly lower pitch improves recall over a high-pitched or thin voice
- **Do not use:** High-pitched or "bubbly" female voice (signals influencer performance, not friend recommendation), male voice (gender mismatch for this demographic reduces congruency)

**ElevenLabs voice selection note:**
- "Rachel" and "Bella" (ElevenLabs stock voices): warm, mid-pitched, conversational — validated in Phase 0 as suitable
- Search term in ElevenLabs library: "conversational" + "warm"
- Avoid: voices tagged "energetic," "upbeat," or "professional narrator"
- Avoid: voices that sound young (under 25) — less credibility for product recommendation content

---

## 6. Energy Level — The Calibration Problem

The most common failure mode in AI-generated voiceover for UGC ads is **incorrect energy level** — too high or too low relative to the format.

**Too high (the influencer error):**
"Okay so I NEED to talk about this product because my dog absolutely LOVES it and I cannot believe how well it works—"
Signals: ad, performance, inauthenticity. Triggers ad-scroll reflex.

**Too low (the narrator error):**
"My dog experienced difficulty completing her meals in a reasonable timeframe. This product provided a measurable improvement in her eating habits."
Signals: written copy being read aloud. Destroys conversational authenticity.

**Correct calibration:**
"My dog used to finish dinner before I'd even put the bowl down. We got this lick mat and slow feeder combo and she spent forty minutes on the same meal."
Signals: person talking, reporting a real thing that happened, finding it slightly notable but not performing surprise.

**The calibration test:** Could a real person say this sentence exactly as written while recording a voice note on their phone? If no — if it requires breath control, pacing preparation, or reads as written prose — rewrite it.

---

## 7. CTA Delivery — What Converts vs. What Doesn't

The CTA is the last thing the viewer hears. Its delivery determines whether they act or don't.

**High-converting CTA characteristics:**
- Delivered at the same conversational pace as the rest of the script — not slowed down or made "announcer-y" for emphasis
- Specific condition: "if your dog eats too fast" not "if you have a dog"
- Direct: "you need to try this" not "you might want to look into this"
- Natural: sounds like the final sentence of the friend's voice note, not a sales pitch

**CTA language to use:**
- "If your dog does X, you need to try this."
- "If you've tried everything else, try this one."
- "If you hike with your dog, you need one of these."
- "Most owners get [specific result] — it's worth trying."

**CTA language to avoid (confirmed low-performing):**
- "Link in bio" (format-specific to organic; reads as non-ad-native in paid; also, no links in the video)
- "Click the button below" (not conversational)
- "Order yours today" (announcer register)
- "Don't miss out" (urgency without specificity — generic)
- Any CTA that begins with the brand name

**CTA energy note:** The CTA should not be louder, faster, or more emphatic than the rest of the script. It should land with the quiet confidence of a real recommendation — "I found a thing that works. If you have the same problem, try it." Not a closing pitch.

---

## 8. Script Language Rules (Feeds Into Voiceover Quality)

The voiceover is only as good as the script it reads. These language rules are constraints on script generation that directly affect voiceover output quality.

**Words and phrases that kill conversational authenticity — never use:**
- "game changer" (overused beyond credibility)
- "amazing" (too vague, signals generic copy)
- "obsessed" (influencer register, not friend register)
- "love this" (same problem)
- "introducing" (announcer register)
- "revolutionary" / "innovative" (corporate register)
- "you'll love" (assumes emotional outcome, sounds salesy)
- Any claim not supported by something visible in the video

**Language patterns that increase authenticity:**
- Specific numbers: "forty minutes," "five strokes," "two weeks"
- Specific animal behavior: "trying to carry it to bed," "finally stopped shaking," "walked back over when I stopped"
- Mild hedging that sounds real: "I wasn't expecting much," "I'd basically given up," "I almost didn't try this one"
- Natural filler that survived editing: "she just — can't inhale it" (the em-dash creates a natural pause that reads as real speech)
- Present-tense reporting: "she's noticeably calmer" not "she was noticeably calmer" (immediacy)

**Script rhythm targets:**
- Sentences vary in length. No string of three sentences the same length.
- The hook sentence should be the shortest sentence in the script (punchy, direct).
- The CTA should be one sentence.
- Total word count for a 25–30 second voiceover: 65–80 words.

---

## 9. Product Category Tone Calibration

Different pet product categories require different emotional registers within the "warm and conversational" range:

| Product Category | Tonal Register | Energy Level | Key Emotional Driver |
|-----------------|---------------|-------------|---------------------|
| Calming/anxiety supplements | Quiet, warm, slightly relieved | Low — 3/10 | Protection instinct, relief that something works |
| Slow feeders / lick mats | Slightly amused, dry | Medium — 5/10 | "Can you believe this worked" surprise |
| Deshedding / grooming | Slightly incredulous, satisfied | Medium — 6/10 | "I tried everything" credibility, visible result |
| Outdoor accessories | Light, practical, wry | Medium — 5/10 | Convenience, one-handed ease, active lifestyle |
| Health supplements / joint support | Earnest, caring, measured | Low-medium — 4/10 | Trust, transformation over time |

**Never match tone to product category by going louder or faster.** Higher-energy delivery signals performance, not authenticity. Calibrate by adjusting warmth and emotional register, not volume or pace.

---

## 10. Audio Direction Language for Prompts (Stage 3 → Stage 4 handoff)

When Stage 3 generates the video prompt, the audio direction section should specify:

**Required fields:**
- Delivery style: "friend voice note — not performing, just talking"
- Pace: "natural conversational pace, approximately 150–165 wpm"
- Energy: [select from category table above]
- Pause locations: mark in the script with em-dashes or ellipses
- CTA delivery note: "same pace and energy as the rest of the script — no sales pitch inflection"

**Example audio direction block for a slow feeder product:**
> Delivery: Friend voice note. She's recorded this on her phone while sitting in the kitchen, immediately after noticing how long the dog has been at the mat. Slightly amused — she's been surprised this worked. Pace: conversational, ~155 wpm. Energy: 5/10. No announcer quality at any point. The CTA ("if your dog eats too fast, you need to try this") is delivered at the same speed as the rest of the sentence — not slower for emphasis.

---

## Sources

- AdsWizz research: native audio ads achieve 53% higher recall and 39% higher purchase intent than traditional audio ads
- Nielsen audio advertising research (2024): audio tone impacts purchase intent 43% more than visuals alone
- Journal of Advertising Research (2019): "Do Your Ads Talk Too Fast To Your Audio Audience?" — 180 wpm peak attention, comprehension decline above 190 wpm (Tandfonline)
- University of Missouri / ScienceDirect (2025): 150–160 wpm most broadly acceptable for comprehension
- Cognitive Load Theory (Sweller, 1988): theoretical basis for speech rate and processing limits
- ResearchGate: "Male and Female Voices in Commercials: Analysis of Effectiveness, Adequacy for the Product, Attention and Recall" — vocal pitch > gender; gender-product matching effect
- Journal of Marketing Research (2024): "The Power of AI-Generated Voices: How Digital Vocal Tract Length Shapes Product Congruency and Ad Performance" (Efthymiou et al., Sage Journals)
- TikTok for Business research: 74% attention capture for TikTok-first content, 3.3x action vs. repurposed content
- AdCreative.ai: UGC achieves 6.9x more engagement than brand-generated content
- ElevenLabs blog: "Voiceovers for Video and Audio Ads" — practical guide for ad voiceover generation
- ElevenLabs blog: "Why AI Narrator Voices Are Dominating TikTok and Instagram in 2025"
- Phase 0 findings: ElevenLabs Conversational style at Stability 0.5, Similarity 0.75 validated across 4 pet products
- Narration Box: AI voices that convert for ads — genre analysis
- Everythingcinemaproductions.com: "The Secret to Sounding Real in Commercial VO" — authentic vs. polished delivery
