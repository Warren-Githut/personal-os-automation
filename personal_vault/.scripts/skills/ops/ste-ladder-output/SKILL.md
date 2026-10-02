---
name: ste-ladder-output
description: "Pick the output modality: STE100, diagram, HTML, or video."
version: 1.0.0
author: GG (Hermes)
license: MIT
category: ops
metadata:
  hermes:
    tags:
      - warren
      - modality
      - ste100
      - diagram
      - html
      - video
      - deliverable
      - non-it
      - vietnamese
    related_skills:
      - warren-visual-ops
      - warren-minimal-artifact
      - explain-operations-math
      - ops-architect
      - chartjs-offline-dashboard
      - humanizer
tags:
  - warren
  - modality
  - ste100
  - diagram
  - html
  - video
  - deliverable
  - non-it
  - vietnamese
trigger: >
  Bố asks for an explanation as a deliverable, says a topic is hard to follow in
  text, asks for a diagram/one-pager/video, says 'giải thích dễ hiểu' or 'làm
  cho dễ hiểu hơn' on something already explained in prose. Also fires when GG is
  about to write a long prose answer containing a process, a comparison, or a
  number Bố has to remember.
related_skills:
  - warren-visual-ops
  - warren-minimal-artifact
  - explain-operations-math
  - ops-architect
  - chartjs-offline-dashboard
  - humanizer
---

# ste-ladder-output — The Modality Ladder

## When to Use

- Bố asks for an explanation as a **deliverable**, not an answer.
- Bố says something already explained is **hard to follow**.
- Bố asks for a diagram, one-pager, dashboard or video by name.
- Bố says "giải thích dễ hiểu" / "làm cho dễ hiểu hơn" on existing prose.
- GG is about to write **long prose holding a process, a comparison, or a
  number** Bố would otherwise have to remember.
- Bố needs to **show or train someone else** (handover, onboarding, a meeting).

**Do not use** for: a single number ("AC tuần này bao nhiêu"), a yes/no
question, or anything Bố reads once and discards. Rung 1 is correct there.

---

> **One rule:** match the output format to how Bố will actually absorb the
> content. Prose is the cheapest format and the worst for anything structural.
> Escalate one rung at a time, and only when the rung below has genuinely
> failed.

---

## The ladder

| Rung | Format | Use when | Warren skill that already does it |
|---|---|---|---|
| **1** | **Prose** | One fact, one opinion, a short answer. Bố reads it once and moves on. | — |
| **2** | **STE100 prose** | The content is a procedure, a rule set, or technical text Bố will re-read. | this skill, `references/ste100-80.md` |
| **3** | **Diagram / SVG** | There is a shape: a flow, a map, a causal chain, a comparison of 3+ things. | `warren-visual-ops` (HTML+SVG, never Excalidraw), `architecture-diagram` |
| **4** | **HTML page** | Bố will interact, filter, or navigate. More than ~8 numbers, or any "let me poke at this". | `warren-visual-ops`, `chartjs-offline-dashboard`, `warren-minimal-artifact`, `sketch`, `claude-design` |
| **5** | **Narrated video** | Bố needs to *show* someone else (training, handover, a meeting) or must absorb it while doing something else. | this skill, `scripts/build_explainer.py` |

**Read the table bottom-up when choosing.** Rung 1 is the default and is correct
most of the time. Do not start at rung 3.

### Do not confuse this with the Solution Ladder

`ops-architect` has a **Solution Ladder**: 3 tiers of *solutions to a problem*
(effort / root cause / scalability). This skill has the **Modality Ladder**:
5 tiers of *output format for the same content*. Same word, unrelated thing.
When Bố says "ladder", ask which one.

---

## Trigger policy

**Propose, do not build.** When the content belongs on rung 3+ but was delivered
as prose, append ONE line offering the upgrade:

```
📐 Bậc cao hơn: con dựng bản HTML/diagram cho <topic> nếu Bố cần. Không cần thì bỏ qua.
```

Rules:
- Never build rung 3+ unprompted. Bố decides.
- One offer per topic. If Bố ignores it, stop offering for that topic.
- Do not offer rung 5 (video) unless Bố has said he needs to show or train
  someone. Video is the most expensive rung and the easiest to over-use.

---

## Rung 2 — STE100 at 80%, in Vietnamese

ASD-STE100 is an English standard with no Vietnamese edition. Do **not** claim
STE100 compliance for Vietnamese output. Apply the *shape* at ~80%:

1. **One idea per sentence.** If a sentence has "và" joining two actions, split it.
2. **≤20 words per sentence** for procedures. ≤25 for descriptions.
3. **Imperative voice for actions.** "Đóng van." not "Van nên được đóng."
4. **Active voice.** Drop the actor when the actor is obvious from context.
5. **Plainest word that is correct.** No jargon, no loanword where a Vietnamese
   word exists.
6. **One topic per paragraph.** ≤6 sentences.
7. **Max 3 nouns stacked** as a modifier before a head noun.

Full rules with English examples and sources: `references/ste100-80.md`.

**Bố-specific overrides on top of STE100:**
- Vietnamese outranks rule 5 — a correct English loanword beats a clumsy
  Vietnamese calque, but a plain Vietnamese word wins over both.
- Numbers are never rounded, never paraphrased (A3, `warren-minimal-artifact`).
- Every claim still needs a confidence tag `[HIGH]/[MOD]/[LOW]` (SOUL §4).

---

## Rung 5 — narrated video

### When it is the right answer
- Training a new floor/shift member who will not read a document.
- A handover video before someone goes on leave.
- Sending a number or a process to someone outside the ops chain.

### When it is the wrong answer
- Bố wants to *read* it → rung 2 or 4. Video cannot be skimmed or searched.
- The content has more than ~8 numbers → rung 4. Video is lossy for data.
- The topic is still moving. A video is expensive to redo; markdown is not.
- Bố needs to *act* on the number right now → give the dashboard link instead.

### Build it

```bash
python scripts/build_explainer.py manifest.json
```

`scripts/build_explainer.py` renders a narrated MP4 end to end on this machine:
scene manifest → per-scene HTML → Chrome headless PNG frames → Edge TTS
narration → ffmpeg segments → concat. Each scene's on-screen duration is driven
by its own narration length, so the picture cannot drift out of sync with the
voice.

Manifest shape and all options: `templates/manifest.example.json`.
Runnable end-to-end example: `templates/manifest.lu7.json`.

### Toolchain — verified present on this machine

| Tool | Path / status |
|---|---|
| Chrome | `C:/Program Files/Google/Chrome/Application/chrome.exe` — headless screenshot works |
| ffmpeg | `C:/Users/khoans/AppData/Local/hermes/tools/ffmpeg-9.0.1-win32-x64/bin/ffmpeg` — libx264 + aac |
| Edge TTS | `edge_tts` in the Hermes venv — Vietnamese voices `vi-VN-HoaiMyNeural`, `vi-VN-NamMinhNeural` |

**No API key and no paid service is involved.** Edge TTS is free.

### What is NOT available — do not promise it

- **`manim` is not installed and there is no LaTeX on this machine.** A true
  3b1b-style animation video is therefore **not** buildable here. The skill
  `manim-video` is bundled but unusable on this box — say so rather than
  starting a build that will fail at the LaTeX step.
- **ElevenLabs is not configured.** Use `edge_tts`. If Bố wants a better voice,
  that is a separate decision to raise, not a silent swap.

### Voice rules for Vietnamese narration

- Write the narration **with full diacritics**. `edge-tts` handles them; the
  earlier failure mode was ASCII text, not the engine.
- One fact per narration line. Aim for 12–20 Vietnamese words — longer than
  English because Vietnamese syllables are longer.
- Numbers read as units, never symbol soup. "69 nghìn đồng" not "69k".
- `edge_tts` intermittently returns `NoAudioReceived` under burst load. The
  script retries 5× with backoff — a first-attempt failure is **not** a real
  failure.

---

## Pitfalls

- **Do not skip rungs 3–4 and jump to video.** Warren already has 94 HTML
  dashboards in the vault. Check what exists before building anything new
  (`warren-visual-ops` rule 2, inventory-first).
- **Video is not searchable and not skimmable.** For anything Bố will need to
  look up later, rung 4 wins even though video feels more impressive.
- **Chrome screenshot paths must be native Windows** (`C:/...`). An MSYS path
  (`/c/...`) fails with no error and no file — the script raises a pointed
  error, do not "fix" it by adding retries.
- **`edge_tts` needs a short gap between scenes.** Bursting six lines at once
  triggers throttling. The script sleeps 0.6s between scenes; do not remove it.
- **A scene with no narration becomes a 0.9s silent still.** That is almost
  never what Bố wants — it means the narration text is missing from the
  manifest, not that the scene should be silent.
- **Do not claim "ASD-STE100 compliant" for Vietnamese output.** The standard
  has no Vietnamese edition. Say "STE100-style" or "80% STE100".
- **Do not rebuild an existing dashboard as a diagram.** Read
  `00_DASHBOARDS.md` first; link to what is already there.

---

## Verify before telling Bố it works

1. `ffprobe` the output and report duration, resolution, and codecs.
2. Extract one frame from the middle with `ffmpeg -ss` and read it back — this
   is how you confirm the text and the diacritics actually rendered.
3. Confirm the audio stream exists and is non-zero length. A silent MP4 with a
   picture looks like success and is not.

Report the three numbers to Bố. "Video xong" without a duration is not a
result.