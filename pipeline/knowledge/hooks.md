# hooks.md — Stop-Scroll Hook Principles for Short-Form Video Ads

**Purpose:** System prompt reference for Stage 3 (video prompt generation). Every video prompt Claude generates must open with a hook that clears measurable retention thresholds. This file encodes what that means, what the data shows, and how to execute it for b-roll/voiceover format pet product ads.

---

## 1. Why the First 3 Seconds Are Existential, Not Just Important

The hook is not a creative preference — it is the algorithmic gatekeeping mechanism on both TikTok and Meta.

**TikTok data:**
- Users decide to scroll or stay within 0.4 seconds of a video appearing, per TikTok World 2025 data (cited by AudienceScience, 2025)
- Videos with 3-second retention above 65% receive 4–7x more impressions than videos with poor early retention (industry analysis of TikTok algorithm behavior, Shortimize 2025)
- 71% of viewer retention decisions happen in the first 3 seconds (Opus Clip / OpusClip Blog, 2025)
- 65% of people who watch the first 3 seconds will watch at least 10 seconds; 45% will watch 30+ seconds
- Videos under 15 seconds achieve 92% average completion rates (OpusClip, 2025)

**Meta/Facebook data:**
- Hook Rate — the % of people who watch at least 3 seconds of your video — is Meta's primary early-attention signal
- Target hook rate: 30–40% (Motion.app benchmarks for ecommerce)
- Below 25% hook rate = creative emergency; above 35% = algorithm serves efficiently and cheaply
- Improving hook rate from 15% to 28% in one documented campaign produced a 12% lift in conversion rate (AdManage.ai, 2025)
- 70–80% of Meta ad performance is attributable to creative quality, not budget or targeting (AppsFlyer 2025 report)
- 63% of top-watched Facebook videos deliver their core message within the first 3 seconds (Lebesgue research, cited by Metalla Digital)

**What this means for prompt generation:**
Every video prompt must specify exactly what happens in the first 2–3 seconds at the visual and audio level. Vague hooks ("starts with a product shot") will fail. The hook must be designed for 30%+ thumb-stop.

---

## 2. The Psychology Behind What Stops a Scroll

Three neurological mechanisms are responsible for virtually all effective hooks. Use at least one, ideally two:

### 2a. Curiosity Gap / Open Loop (Zeigarnik Effect)
The Zeigarnik Effect (Bluma Zeigarnik, 1920s) shows that humans remember unfinished tasks approximately 90% more than completed ones. An open question forces the brain to stay engaged until the loop closes. In video, this means opening with a statement or visual that promises a resolution viewers haven't received yet.

Application: "I tried every brush on the market..." (loop opened) forces the viewer to stay for "...and this one shocked me." The brain cannot comfortably scroll away from an open loop.

**Example structures:**
- "I gave up on [product category]..." → *why?* forces the viewer to stay
- "This sounds ridiculous, but..." → *what does?*
- Open with the dog's strange/cute behavior before any product mention → *what is that? why is it doing that?*

### 2b. Pattern Interrupt (Visual Surprise)
The feed is an endless scroll of similar content. Anything visually unexpected triggers the brain's orienting response — an involuntary reflex to stop and identify the anomaly. This is the "thumb-stopper" effect.

In b-roll format, pattern interrupt is created by:
- An unusual camera angle (extreme close-up of paws, overhead POV of mat suction-cupping to tile)
- Motion that reads as accidental or surprising (dog dragging the mat across the room)
- A visual contrast against typical feed aesthetics (very slow motion when feed is fast; total stillness when feed is motion)

### 2c. Emotional Resonance / Immediate Recognition
Pet owner identity is a powerful driver. If the hook triggers "that's exactly my dog" within 1 second, the viewer stops — not from curiosity, but from recognition. This is the basis of the PAS (Problem-Agitate-Solve) structure used in direct response advertising.

**Pet-specific emotional triggers that stop scrolls (highest performing first):**
1. Visible anxiety or stress behavior in a dog (panting, pacing, trembling) — triggers protective owner instinct
2. Messy, chaotic fast eating — recognizable problem for dog owners
3. Dog ignoring or outsmarting a product — humor and relatability
4. Before/after coat or behavior contrast — transformation narrative
5. Dog expressing contentment or calm — aspirational emotional state

---

## 3. Hook Structures Ranked by Measured Performance

These structures are ranked by measured performance across TikTok and Meta ad creative analysis (Motion.app, Metalla Digital, JoinBrands research, TikTok Creative Center findings):

### Structure 1: Immediate Problem Statement (Highest converting for pet products)
**Format:** Open with the problem, stated plainly and quickly. No setup. No brand name.
**Audio hook:** Voiceover begins mid-sentence as if already in a conversation.
**Visual hook:** Show the problem behavior or the messy/frustrating state, not the product.
**Why it works:** Triggers the PAS framework and Zeigarnik Effect simultaneously. The viewer recognizes their own problem and needs to hear the solution.

> Example: Video opens on overhead POV of empty food bowl, dog licking the last remnants in 4 seconds.
> Voiceover starts: "My dog was done with dinner before I'd even put the bowl down."

### Structure 2: Curiosity + Open Loop (High performing, especially for behavior/supplement products)
**Format:** Statement of a surprising result, without revealing the cause.
**Audio hook:** Drop the punchline first, then explain.
**Visual hook:** Show the end state (calm dog, clean coat, satisfied pet) before any product is visible.
**Why it works:** Reverses the information order. Most ads build to the result — this starts there.

> Example: Video opens on dog lying calm in a position that reads as unusual for the breed.
> Voiceover: "She used to shake for two hours after thunder. This is her during a storm."
> (Product reveal comes 5+ seconds later)

### Structure 3: Bold Claim / Specific Statistic (Strong for skeptical categories — supplements, grooming)
**Format:** First frame shows a number or a single dramatic word.
**Audio hook:** State the claim immediately. Specific numbers outperform vague claims.
**Visual hook:** Text overlay in first 2 seconds reinforces the spoken claim.
**Why it works:** Specificity signals credibility. "40 minutes" beats "so much longer." "More fur in 5 minutes than a month of brushing" is provable and verifiable in the video.

> Example: Text overlay appears: "40 minutes." Voiceover: "My dog has been eating for 40 minutes and she's not done yet."

### Structure 4: Direct Address / Question (Moderate performer, depends on precision of targeting)
**Format:** Voiceover directly addresses a specific owner type in the first word.
**Audio hook:** "If your dog eats too fast..." / "Do you have a heavy shedder?"
**Visual hook:** Product being used, hands in frame, already mid-action.
**Why it works:** Creates instant audience self-selection. The wrong viewer scrolls; the right viewer locks in.
**Warning:** Must be extremely specific. "Do you have a dog?" is useless. "Do you have a dog that still acts like a puppy at dinner?" is targeted enough to stop a scroll.

### Structure 5: Transformation / Before-After (Strong for visible-result categories)
**Format:** Fast cut between problem state and solution state.
**Audio hook:** Minimal words, let the visual do the work.
**Visual hook:** Two contrasting shots in rapid succession — chaotic then calm, fur-covered then clean, food inhaled vs. still eating.
**Why it works:** Exploits the visual cortex's ability to process contrast instantly. The viewer's brain completes the story without needing words.

---

## 4. Format-Specific Hook Rules for This Pipeline

### B-roll / POV format (primary format — what this pipeline generates)
- The hook must be established **visually** in the first 2 seconds, before the voiceover says anything meaningful
- First shot should show action, not setup. No establishing shots of a room. No product sitting on a counter with nothing happening.
- Best opening shots by product category:
  - **Slow feeders/lick mats:** Dog's face at mat level, nose down, licking intensely (extreme close-up)
  - **Calming supplements:** Dog in recognizably anxious posture (panting, pacing) OR in striking calm (contrasted against the expected behavior)
  - **Deshedding tools:** Tool mid-stroke, fur coming off in a satisfying visible clump
  - **Water bottles:** Dog drinking from the built-in bowl on a trail, the mechanism mid-use
- Camera movement: First shot should have slight motion — either slight handheld shake or a slow push-in. Static opening shots have lower thumb-stop rates than shots with any motion.

### Audio hook timing (for voiceover format)
- Voiceover must begin within 0.5 seconds of video start — silence in the first second kills hook rate on TikTok
- First spoken word should not be "I", "Hi", "So", or "Today" — these are the verbal equivalent of clearing your throat
- Best opening words/phrases for pet product ads:
  - A specific number: "Forty minutes..." / "Five minutes..."
  - A relatable problem stated flatly: "My dog used to..." / "I tried every..."
  - A completed observation: "She figured out every slow feeder I bought."
  - A mild confession: "I gave up on [category]."

### What NOT to do in the hook (confirmed failures)
- **Opening with the product name or brand name** — signals "this is an ad," triggers scroll reflex
- **Opening with the creator's face or greeting** — only works in talking-head format, which this pipeline does not use
- **Slow zoom-out from product packaging** — reads as commercial production, not UGC
- **Generic establishing shot** (kitchen, room, park) before any action begins
- **Voiceover starting with "Have you ever..."** — overused, now signals low-quality content

---

## 5. Pet Content Specific Findings

Pet content is one of the highest-performing organic categories on both TikTok and Instagram. However, paid pet product ads must be distinguished from organic pet content — the hook strategy differs.

**What makes organic pet content viral does NOT map directly to paid ad hooks:**
- Organic: cute/funny behavior, unexpected animal reactions, heartwarming rescue content
- Paid: problem recognition + credibility signal + solution preview — all in 3 seconds

**What does transfer from organic pet content to paid hooks:**
- Showing the animal's face in the first frame significantly increases watch time (emotional resonance with the animal is immediate)
- Sound of the animal (eating, licking, panting) used in the first 2 seconds as an audio hook outperforms music-only openings for this category
- The owner's hands (not face) in frame alongside the pet creates authenticity without requiring a human face

**Hook performance hierarchy for pet product categories:**
1. **Calming/anxiety products:** Problem-behavior visual hook is strongest (show the anxious state, then resolve it)
2. **Feeding solutions (slow feeders, lick mats):** Open-loop or before-state hook strongest ("done in 45 seconds")
3. **Grooming products (deshedders, brushes):** Transformation hook strongest (before fur volume vs. after)
4. **Accessories/outdoor (water bottles, harnesses):** Direct-address or specific scenario hook strongest ("if you hike with your dog...")

---

## 6. Benchmarks to Target

Use these as pass/fail criteria when evaluating hook quality during prompt generation:

| Metric | Target | Concern | Failure |
|--------|--------|---------|---------|
| TikTok 3-second retention | >65% | 40–65% | <40% |
| Meta hook rate (3-sec view / impressions) | >30% | 20–30% | <20% |
| Meta hold rate (15-sec / 3-sec views) | >25% | 15–25% | <15% |
| First voiceover word timing | <0.5 sec | 0.5–1.5 sec | >2 sec silence |
| First visual action | Frame 1 | By sec 1 | After sec 2 |

---

## Sources

- TikTok World 2025 data on 0.4-second decision window (AudienceScience)
- OpusClip Blog: TikTok length, format, and retention data (2025)
- Motion.app: Hook rate and hold rate benchmarks for ecommerce (2025)
- AppsFlyer 2025: 70–80% of Meta performance from creative quality
- Lebesgue / Metalla Digital: 63% of top videos hit key message in 3 seconds
- AdManage.ai: Hook rate improvement and conversion lift data
- Shortimize: 3-second retention benchmarks and impression multiplier data
- JoinBrands: Hook structure analysis
- Zeigarnik, B. (1927). Über das Behalten von erledigten und unerledigten Handlungen. — foundational psychology behind open loop retention
- ResearchGate (2024): "Hooked by curiosity: The Zeigarnik Effect amplifying customer loyalty and brand advocacy through thumb-stopper advertisements"
- Marketeze.ai: Pet creator viral hook analysis
- Influencers-time.com: POV format engagement data (1.6x recommendations vs. standard video)
- BetterVideoContent.com: Zeigarnik Effect applied to video retention
- Inceptly (YouTube Ads Agency): Open loop retention strategy for direct response
