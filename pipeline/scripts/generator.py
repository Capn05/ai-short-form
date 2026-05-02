import json
import random
from pathlib import Path

from openai import OpenAI


KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"


def _build_system_prompt() -> list[dict]:
    text = """You are an expert UGC scriptwriter for short-form product ads (TikTok, Instagram Reels).

Scripts are for b-roll + voiceover — no talking head, no presenter. The voiceover sounds like a real customer leaving a voice note for a friend: warm, specific, conversational. Never corporate or salesy.

FORMAT:
- 55–70 spoken words maximum (excluding bracket tags). Every word over 70 adds unwanted seconds.
- Contractions and natural speech patterns throughout
- CTA ends the script: natural, warm, never salesy. Follow the CTA guidance provided per script type.
- No emojis, no hashtags

HOOK RULES (first line):
- Establish the problem or surprise result immediately — no setup, no brand name in the opening
- First line must be the shortest sentence in the script
- Never start with "I", "Hi", "So", or "Today"
- Specific numbers beat vague claims: "forty minutes" > "a long time", "two weeks" > "a while"
- Best structures: immediate problem ("I used to..."), open loop ("Nothing worked until..."), transformation preview ("I sleep through the night now. This is why.")

SCRIPT LANGUAGE:
- Never use: "game changer", "amazing", "obsessed", "love this", "revolutionary", "introducing", "you'll love"
- Use: specific outcomes tied to the product, specific numbers, mild hedging that sounds real ("I wasn't expecting much", "I'd basically given up")
- Ground every claim in product details from the user message — don't invent benefits
- Vary sentence length — no three sentences the same length in a row
- Present tense for results: "it works" not "it worked"

TONE BY PRODUCT CATEGORY:
- Pain relief / calming / sleep: quiet, warm, slightly relieved — energy 3/10
- Food / supplements / health: earnest, measured, caring — energy 4/10
- Convenience / productivity tools: dry, slightly amused, satisfied — energy 5/10
- Beauty / skincare / grooming: slightly incredulous, confident — energy 6/10
- Fitness / performance: direct, energetic, results-focused — energy 7/10
- If the product doesn't fit a category above, infer the right energy from the product's core emotional benefit

EMOTION TAGS (ElevenLabs v3 — consumed by TTS, not spoken aloud):
Emotion tags: [sad], [thoughtful], [happy], [excited], [calm], [curious], [wistful], [matter-of-fact], [warm], [amused], [reflective], [lighthearted]
Delivery tags: [whispers], [speaking softly], [pause], [short pause], [sighs], [laughs], [light chuckle], [exhales]

Tag rules:
- Place immediately before the text they affect, no space between tag and word
- Use 2–4 tags per script — enough to shape the arc, not so many it feels mechanical
- Emotional arc: [relatable problem] → [curious/thoughtful discovery] → [warm result]
- Never stack more than 2 tags together
- CTA always feels [warm], never [excited]

Example (do NOT copy — for tone only):
[sad]I was waking up exhausted every single morning no matter how long I slept. [thoughtful]Tried this after seeing it recommended three times in the same week. Take two capsules thirty minutes before bed, wake up actually rested. [happy]Haven't touched my old sleep aids since. If you're tired of being tired, it's worth trying.

The product details and script type instructions will be in the user message."""

    return text


def generate_scripts(product: dict, output_dir: Path, n: int = 2, voice_persona: str | None = None) -> list[dict]:
    script_types = _load_script_types()
    chosen = random.sample(script_types, min(n, len(script_types)))

    scripts_dir = output_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    client = OpenAI(max_retries=5)
    results = []

    for i, script_type in enumerate(chosen):
        print(f"[scripts] generating '{script_type['name']}' ({i+1}/{len(chosen)})...")
        script_text, usage = _call_llm(client, product, script_type, voice_persona)

        result = {
            "script_type_id": script_type["id"],
            "script_type_name": script_type["name"],
            "script": script_text,
            "usage": {
                "input_tokens": usage.prompt_tokens,
                "output_tokens": usage.completion_tokens,
                "cache_read_input_tokens": 0,
                "cache_creation_input_tokens": 0,
            },
        }

        slug = script_type["id"]
        script_path = scripts_dir / f"script_{i+1:02d}_{slug}.json"
        with open(script_path, "w") as f:
            json.dump(result, f, indent=2)

        txt_path = scripts_dir / f"script_{i+1:02d}_{slug}.txt"
        txt_path.write_text(script_text)

        print(f"  saved → {script_path.name}")
        _log_usage(result["usage"])
        results.append(result)

    summary_path = scripts_dir / "scripts.json"
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)

    return results


def _call_llm(client: OpenAI, product: dict, script_type: dict, voice_persona: str | None = None) -> tuple[str, object]:
    user_message = _build_user_message(product, script_type, voice_persona)

    response = client.chat.completions.create(
        model="gpt-5.5",
        max_completion_tokens=2000,
        messages=[
            {"role": "system", "content": _build_system_prompt()},
            {"role": "user", "content": user_message},
        ],
    )

    return response.choices[0].message.content.strip(), response.usage


def _build_user_message(product: dict, script_type: dict, voice_persona: str | None = None) -> str:
    lines = [
        f"Product: {product['product_name']}",
        f"Price: {product['price']}",
        "",
        "Description:",
        product.get("description", "").strip(),
    ]

    reviews = product.get("reviews", [])
    if reviews:
        lines += ["", "Customer reviews:"]
        for r in reviews:
            author = r.get("author", "")
            rating = r.get("rating")
            prefix = f"{author}, {rating}/5 — " if author and rating else ""
            lines.append(f'"{prefix}{r["text"]}"')

    lines += [
        "",
        f"Script type: {script_type['name']}",
        f"Description: {script_type['description']}",
        "",
        f"Instruction: {script_type['instruction']}",
        "",
        f"Example of this style (do NOT copy, use for tone only): {script_type['example']}",
        "",
        f"CTA guidance: {script_type['cta_guidance']}",
    ]

    if voice_persona:
        lines += [
            "",
            f"Voice persona: {voice_persona} — write in their natural speaking style (word choice, cadence, hedging) as if they left this as a voice note.",
        ]

    lines += ["", "Write the voiceover script now."]

    return "\n".join(lines)


def _load_script_types() -> list[dict]:
    path = KNOWLEDGE_DIR / "script_types.json"
    with open(path) as f:
        return json.load(f)


def _log_usage(usage: dict) -> None:
    cache_read = usage.get("cache_read_input_tokens", 0)
    cache_create = usage.get("cache_creation_input_tokens", 0)
    inp = usage.get("input_tokens", 0)
    out = usage.get("output_tokens", 0)
    status = "CACHE HIT" if cache_read > 0 else ("CACHE WRITE" if cache_create > 0 else "no cache")
    print(f"  tokens: {inp} in / {out} out | {status} (read={cache_read}, write={cache_create})")
