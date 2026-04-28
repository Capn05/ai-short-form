# shot-guidelines.md — Shot Composition, Pacing, and Editing Principles

**Purpose:** System prompt reference for Stage 3 (video prompt generation). Every shot list Claude generates must conform to these principles. This file encodes format-specific rules for the b-roll/POV format this pipeline uses — no talking head, no green screen, no lip sync.

---

## 1. Foundational Format Constraints

This pipeline generates **one format only:** b-roll + voiceover, with POV/first-person sub-variants. The constraints below apply to this format. Nothing here applies to talking-head or green screen formats, which are eliminated from this pipeline.

**The four supported sub-formats:**
1. **POV/b-roll (primary)** — handheld shots showing hands + product + animal. No face. Voiceover only.
2. **Follow-me/over-the-shoulder** — camera follows the creator from behind or side profile. Profile glimpses okay; direct face-to-camera never.
3. **First-person eye-level (pure POV)** — camera acts as the user's eyes. Hands reach into frame from below. Never a face.
4. **Aesthetic b-roll + text overlay** — slow, cinematic single shot or 2–3 shot sequence. No voiceover. Text overlays carry the script.

---

## 2. Aspect Ratio and Safe Zone Specifications

**Primary format:** 9:16 vertical (1080 x 1920px)
- This is the only ratio to use for TikTok In-Feed, TikTok TopView, and Meta Reels placements
- 9:16 fills the full screen — any other ratio creates letterboxing that signals non-native production
- The 4:5 vertical crop outperforms 1:1 square on Meta Feed placements by up to 15% (industry testing, Billo)

**TikTok Safe Zones — critical for text and key visuals:**
- Top: keep critical content below the top 130px (search bar overlay zone)
- Bottom: keep critical content above the bottom 484px (caption, CTA, engagement buttons zone)
- Right side: keep critical content left of the rightmost 140px (profile icon, like/share buttons zone)
- Safe center zone for guaranteed visibility across all devices: approximately 880 x 1500px centered on the frame

**What gets blocked if you ignore safe zones:**
- Text overlays placed at bottom of frame: covered by TikTok caption and username
- CTAs placed on the right edge: covered by like/comment/share buttons
- Product shots in the bottom quarter: covered by the creator's handle and caption

**Practical rule:** All text overlays, product close-ups, and key visual information must be placed in the upper-center to middle-center zone of the frame. Design every shot assuming the bottom 25% of the frame is partially obscured.

---

## 3. Shot Count and Duration Per Shot

**Total video length target:** 21–34 seconds (conversion ad sweet spot for both TikTok and Meta)
- TikTok: 21–34 seconds performs best for conversion objectives (TikTok for Business creative best practices)
- Meta Reels: 15–30 seconds optimal; under 15 seconds gets 92% completion but less room for transformation narrative
- Under 15 seconds: works for awareness objectives, not conversion
- Over 34 seconds: sharp drop in completion rate for cold-traffic ads

**Shot count by video length:**
- 20–25 second video: 5–7 shots
- 25–34 second video: 7–10 shots
- Each shot should be 2–4 seconds long

**Shot length data:**
- Analysis of top 100 YouTube Shorts (2024): average clip length of 2.5 seconds correlated with 35% higher completion rates than clips averaging 4+ seconds
- Top-performing TikTok ads average 2.5–3.5 second clip lengths
- 3 seconds is the minimum time most viewers need to absorb a shot (motionedits.com, editing psychology research)
- Shots under 1.5 seconds feel chaotic and disorienting; shots over 5 seconds in a short-form ad feel slow and signal churn

**The rule:** Target 2.5–3.5 seconds per shot. Faster for action/motion moments. Slower (up to 4 seconds) for close detail or satisfying visual payoff.

---

## 4. Pacing and Cut Frequency

**Core principle:** Change the visual angle or introduce a new element every 2–3 seconds. This is called retention editing or "visual reset."

**Why this works:** Humans habituate to static visual stimuli within 3–4 seconds. Each cut resets attention and signals "new information is coming." This is the mechanism behind TikTok-native pacing.

**Platform-specific pacing norms:**
- TikTok: visual reset every 2–3 seconds is native behavior. Longer gaps between cuts trigger scroll reflex.
- Instagram Reels: slightly more tolerance for 3–4 second shots, but faster cutting is never penalized
- The 4:5 Meta Feed placement has higher tolerance for slightly slower pacing than the Reels placement

**Retention editing patterns (ranked by effectiveness):**
1. **Hard cut to a different angle of the same subject** (most common, lowest risk)
2. **Cut to close-up of detail that was visible in previous shot** (creates discovery, builds interest)
3. **Cut to b-roll reaction** (animal's face, hands interacting, result of previous action)
4. **Zoom-in within the shot** (not a cut — creates motion within a static setup; acceptable every other shot)
5. **Camera angle change** (top-down to eye-level, or low-angle to handheld)

**What to avoid:**
- Dissolve transitions (read as polished/commercial — kills UGC authenticity)
- Wipe or slide transitions (same problem)
- Jump cuts within the same angle and distance (disorienting, reads as editing error)
- More than two consecutive shots without changing the subject or distance

---

## 5. Camera Movement and Handheld Style

**The aesthetic this pipeline targets:** Shot on iPhone by a real person, not by a production crew. Slight imperfection is intentional and signals authenticity.

**Research backing:** Natural lighting and slight camera imperfection outperform studio production in UGC format because "consumers suspect these videos might be staged but still perform better than traditional ads" (BossWallah / UGC production research, 2025). The trust signal of apparent authenticity is not eliminated by knowledge that it's produced — it persists regardless.

**Camera movement rules by shot type:**

| Shot Type | Movement Style | Why |
|-----------|---------------|-----|
| Handheld POV (primary) | Slight natural shake. Not stabilized. Not jittery. | Signals real person filming |
| Follow-me (over-shoulder) | Handheld, slight bounce with walking rhythm | Authentic to "friend filming on a hike" aesthetic |
| Pure first-person eye-level | Minimal movement — like the user is watching carefully | Maximizes immersion; too much shake breaks POV |
| Product close-up (hands) | Static or very slight drift | Focus must be crisp for product detail to land |
| Animal face / reaction | Static or very slow push-in | Emotional connection requires visual stability |
| Aesthetic b-roll | Completely static or near-static. Tripod feel. | Deliberate contrast with fast-paced UGC for aesthetic format |

**Movement to specify in prompts:**
- "Slight handheld shake like she's holding the phone in one hand"
- "Camera propped on a counter — stable but not perfectly level"
- "Very slow push-in as the dog licks the mat — natural, not mechanical zoom"
- "Phone-propped angle — static, slightly off-center to the right"

**Movement to prohibit in prompts:**
- "Cinematic camera push" (too polished)
- "Smooth gimbal movement" (identifies professional production)
- "Drone shot" or "wide establishing" (wrong format entirely)

---

## 6. Lighting

**Research finding:** Natural lighting maintains the authentic aesthetic UGC viewers expect. Slightly uneven, warm, window-lit environments outperform ring-lit studio setups in UGC ad formats — even when audiences suspect the video is produced (BossWallah, 2025; Lemonlight UGC filming best practices).

**Lighting types by setting:**

| Setting | Lighting Direction | Quality | Notes |
|---------|----------|---------|-------|
| Kitchen (feeding products) | Natural window light from the side. Warm. | Soft, slightly uneven | Most common setting for lick mat / slow feeder content |
| Living room / couch (supplements) | Warm lamp light + ambient. Slightly dim is okay. | Very soft, intimate | Matches the emotional tone of calming product content |
| Outdoor / trail (water bottles, accessories) | Dappled natural light. Direction changes. | Variable, warm | Authentic to real outdoor activity; slightly inconsistent light is correct |
| Close-up product detail | Existing room light, slightly backlit to show texture | Soft side-light | Avoid direct overhead light which flattens texture |
| Animal face | Side or front window light | Catchlight in the eye ideally | Eye catchlight increases emotional connection in the frame |

**What makes lighting read as UGC vs. commercial:**
- UGC: slight inconsistency between shots is fine. Not all shots need the same light level.
- Commercial: perfectly consistent 3-point lighting across all shots. Avoid this.
- The worst lighting mistake: ring light visible in the eye reflection of the person or animal. This immediately signals "influencer/ad" rather than "real person."

**Lighting descriptor language for prompts:**
- "Warm natural indoor lighting from a window to the left"
- "Dappled outdoor trail light, slightly overcast"
- "Warm kitchen ambient, late afternoon, slightly dim in the background"
- "Soft window light catching the fur texture"

---

## 7. Visual Variety and Shot Sequencing

**Principle:** Within 21–34 seconds, vary across at least three of these five dimensions. Monotony in any single dimension causes churn.

| Dimension | Low-variety (avoid repeating) | High-variety (rotate) |
|-----------|-------------------------------|----------------------|
| Distance | All medium shots | Mix close-up, medium, POV overhead |
| Subject | Only product | Product + hands + animal face + detail |
| Angle | All same height | Eye-level, overhead, low-angle, close-up |
| Motion | All static | Mix static and handheld |
| Lighting zone | Same light every shot | Interior then exterior, or warm then slightly cooler |

**Shot sequencing by format:**

**POV/b-roll (primary):**
1. Action/problem shot (hook) — animal or hands showing the problem or product in use
2. Close detail — something specific about the product (texture, mechanism, material)
3. Result shot — animal behavior change, product working as intended
4. Wide-ish context shot — enough to show setting, ground, hands, and product together
5. Emotional payoff shot — animal face, contented/engaged/calm
6. CTA visual — product held toward camera, or being re-clipped/re-used in a natural action

**Follow-me (outdoor products):**
1. Follow shot from behind — creator + dog, product visible but not featured
2. Stop and use — profile view, product comes out, animal interacts with it
3. Close insert — product mechanism close-up (button press, bowl extend, snap shut)
4. Back to walk — product stowed, both hands free, natural closure

**Aesthetic b-roll + text (text-only format):**
1. Hero shot — single slow beautiful shot with product in natural context
2. Detail shot — optional second angle, same aesthetic quality
3. Text overlays carry all narrative — spacing between lines timed to beat or breath

---

## 8. Sound-On vs. Sound-Off Considerations

**TikTok:** Design for sound-on as the primary experience.
- 88% of TikTok users say sound is essential to the TikTok experience (TikTok research)
- 73% of users say they are more likely to stop on ads that use audio (TikTok research)
- Over 93% of top-performing TikTok videos use audio
- Brand recall increases 8x when distinctive audio is present vs. visual-only elements

**Meta Reels:** Design for sound-on, but include captions as failsafe.
- Unlike legacy Facebook (where sound-off viewing dominated), Reels are sound-on by default
- Captions still serve accessibility and serve viewers in noisy/quiet environments

**Practical implication for shot design:**
- When writing prompts, include notes on what ambient or diegetic sound each shot should capture
- Sound of product mechanism (water bowl snapping, suction cup locking, supplement powder falling) can function as a hook in itself — specify "capture the sound of X clearly"
- The aesthetic b-roll + text format is the one exception where the video is designed silent (ASMR-style ambient audio optional)

---

## 9. Text Overlay Principles

**When to use text overlays:**
- Problem identification in the first 2 seconds (reinforces verbal hook, helps sound-off viewers)
- Key stat or number that supports the claim (e.g., "40 minutes")
- CTA at the end (not "link in bio" — a specific action or observation)
- Aesthetic b-roll format: text overlays ARE the script; see Shot Sequencing above

**TikTok text overlay data:**
- Text boxes are used in 86% of all top-performing TikTok ads
- Text overlays result in a 64% lift in conversion rate (TikTok Creative Center analysis, cited by Creatify 2025)
- Action-oriented overlays ("Shop now", "Try this", "Get yours") increase conversion 18%+ over no-overlay CTAs

**Text overlay safe zone placement:**
- Center of frame (horizontally)
- Between the 30% and 70% vertical markers
- Never in the bottom 25% or top 10% of the frame
- White text, bold weight, high contrast is the TikTok-native style
- No script fonts, no brand-colored text for first-generation UGC — it reads as an ad before the hook lands

**Timing:**
- Problem text: appears with or just after the first voiceover word
- CTA text: appears in the final 3–5 seconds
- Never have text visible for more than 4 seconds per card (reading time is 2–3 seconds; longer feels paused)

---

## 10. What "UGC-Authentic" Looks Like vs. What to Avoid

| UGC-Authentic (use) | Commercial Production (avoid) |
|--------------------|-------------------------------|
| Slightly uneven framing | Perfectly composed every shot |
| Natural light variation between shots | Consistent 3-point studio lighting |
| Slight handheld movement | Gimbal-smooth or perfectly static |
| Real kitchen / real trail in the background | Staged, cleared, or branded backdrop |
| Hands visible but not manicured or styled | "Hero hands" (styled, ring-lit) |
| Animal behaving naturally in the environment | Animal in a posed or obviously staged position |
| Product held casually or used mid-action | Product displayed like a catalog photo |

---

## Sources

- TikTok for Business: Creative best practices for performance ads (ads.tiktok.com)
- TikTok Creative Center analysis: text overlay conversion lift (64%), action CTA lift (18%), cited by Creatify (2026)
- TikTok research: 88% of users say sound is essential; 73% more likely to stop on audio ads; 93% of top videos use audio
- TikTok for Business: 21–34 seconds optimal for conversion ads
- AppsFlyer 2025: 70–80% of Meta performance from creative quality
- Billo creative testing: 4:5 outperforms 1:1 by up to 15% on Meta Feed
- Motion.app: hook rate benchmarks (30–40% target), hold rate (25%+)
- AdManage.ai: TikTok safe zone specifications (130px top, 484px bottom, 140px right)
- OpusClip Blog: under-15-second videos achieve 92% completion rates; 2024 data
- Vidpros.com / YouTube Shorts 2024 analysis: 2.5-second average clip length correlates with 35% higher completion
- BossWallah: "UGC Illusion" — why even staged natural lighting outperforms studio production in UGC format
- Lemonlight UGC filming best practices: natural lighting and authentic framing
- Nature.com / PMC 2025: peer-reviewed research on short-form video and purchase intention (doi: 10.1038/s41598-025-94994-z)
- Motionedits.com: 3 seconds as minimum shot absorption time in short-form editing
- Stackmatix: TikTok Creative Center trending formats analysis
