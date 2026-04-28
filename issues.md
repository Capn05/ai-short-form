# Phase 2 — Issue Log

Issues found during stress testing. Updated as new problems are discovered.

---

## Pipeline Failures

**Empty script output** (run `8137931d`)
Stage 2. `max_tokens=500` was too low — adaptive thinking consumed all tokens before Claude could output any script text. Fixed: raised to 2000.

**`chunk_count` KeyError**
Stage 6 print statement referenced `chunk_count` key which doesn't exist in the result dict. Fixed: changed to `len(v['clip_paths'])`.

**`image/webp` media type mismatch**
CDN serving JPEG files with `.webp` extension, causing Claude to reject the image. Fixed: magic byte detection to infer true media type regardless of extension.

**Claude `video` content block rejected (400)**
Claude's API does not support a `video` content block type. Attempted to pass product video as video block. Fixed: extract frames with ffmpeg and pass as image blocks instead.

---

## Script Quality

**Wrong product usage — capsule product**
Claude wrote "sprinkling capsule contents onto food." Seedance rendered whole capsules being poured. Root cause: Claude inferred usage from product name without understanding the mechanic. Fixed: PHYSICAL SEQUENCES rule — never invent a physical interaction not clearly described in product materials.

---

## Video Quality

**Feeder lid physics impossible** (run `9f1ba49a`)
Seedance rendered food dropping through a closed flat surface of the feeder hopper. Root cause: prompt said "kibble poured into top hopper" without specifying lid-open step. Fixed: PHYSICAL SEQUENCES rule — describe every intermediate step, never just the outcome.

**Fix confirmed** — rerunning the same URL after the prompt changes produced output that looked like a low-budget UGC TikTok video rather than a high-production ad. Changes validated.

**Zoom/push-in effect + professional lighting** (run `0fbadfdb`)
Shots had a slow zoom-in effect and lighting that looked professionally lit. Root cause: (1) "slight handheld shake" is too weak — Seedance adds zoom by default when movement isn't strongly asserted; (2) zoom and push-toward-subject weren't explicitly banned, only gimbal/pan; (3) professional framing terms ("medium close-up", "side-angle medium shot") leaked into prompts. Fixed: changed to "handheld shake" (no "slight"), explicitly banned zoom/push, banned professional cinematography terminology, required imperfect/uneven lighting in every shot description.

**Staged prop-list clutter + art-directed appearance** (run `0fbadfdb`)
Shots looked like a TV ad despite having background objects. Root cause: the "name at least one background detail" rule caused Claude to append explicit prop lists to every shot ("a chewed rope toy", "a dog-eared paperback", "a tennis ball") which reads as staged, not organic. Voice persona also bled into shot descriptions as costume direction ("American, early 20s, casual sweatshirt sleeve"). Fixed: replaced the rule with "describe the room as it naturally is — never append a prop list"; told Claude not to describe clothing or appearance from voice persona.

**Professional-looking shots** (run `8c850498`)
Shots had amazing lighting, perfect framing, and camera pans — looked like a commercial not UGC. Root cause: Claude used overhead/top-down angles and clean background descriptions; product video frames likely influenced framing style. Fixed: banned overhead/top-down/pan angles, required specific background clutter in every shot, strengthened product video instruction.

**First chunk looked professional** (run `4e6db174`)
Chunk 1 looked like a professional ad (panning, perfect lighting) while chunk 2 looked like genuine UGC. Root cause: Claude used "rotating to show", "neutral background", "showcasing" language in chunk 1 prompt. Fixed: banned product showcase language, reframed system prompt opening to emphasize UGC authenticity.

**Dog inconsistency between chunks**
Different dog breed/appearance in each chunk. Root cause: Seedance has no memory between generation calls. Fixed: reference video chaining — each chunk passes previous chunk's output as `reference_videos` to Seedance.

**Gender mismatch — voice vs. on-screen person**
ElevenLabs voice was a young woman but video shots described/showed a man. Fixed: query ElevenLabs voice metadata (gender, age, accent from labels) and pass as `voice_persona` to Stage 2 and Stage 3.

**Seedance hallucinates brand app UI when brand is visible in frame** (run `07630fac`)
Prompt mentioned "hand holding a phone" with PETLIBRO fountain visible in background. Seedance inferred a PETLIBRO app on the phone screen from its training data and rendered it as illegible squiggles. Was accidentally out of focus in this run. Covered by READABLE TEXT rule but worth knowing this hallucination pattern exists — Seedance associates known brands with their app/packaging and projects them onto nearby screens.

**Phone screen / device display text renders as squiggles**
Seedance cannot invent text it hasn't seen in reference images — app UI, nutritional labels, device displays all render illegibly. Fixed: READABLE TEXT rule — never write shots requiring invented text; describe hand action only for phone screens, indicator light/glow for device displays.

---

**Physical interaction hallucination on thin product descriptions** (run `e306a11c`, HHOLOVE litter box)
Claude invented a "tied drawstring bag inside the waste drawer" — a detail not in the description, images, or video. Root cause: product description was extremely thin ("no more manual scooping", "intelligent APP control") giving Claude almost nothing to work with. With no described mechanic to reference, it filled in from general knowledge of self-cleaning litter boxes despite the PHYSICAL SEQUENCES rule. Mitigation: if description is under ~100 words, Claude is likely to hallucinate mechanics — flag these runs for manual review.

---

## Scraper Quality

**Bullet points grabbing wrong content**
`_extract_bullet_points` was picking up stress trigger list items (e.g. "Stormy nights", "Fireworks") instead of product features. Fixed: removed bullet point extraction entirely — Claude gets raw description text.

**Description empty for some products**
`body_html` from Shopify JSON was empty or stale for merchants using page builders. Fixed: use Playwright to scrape rendered page description via `scrape_page_content`.
