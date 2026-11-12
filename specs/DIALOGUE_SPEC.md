# DIALOGUE_SPEC — АЫАЫ: ПОСЛЕДНИЙ СКУФ
Version: 1.0-draft | Status: tone and direction approved | 2026-11-13

## 1. Creative brief
- Dialogue in colloquial Russian, **short, interrupted, occasionally mumbled, genuinely profane**, like friends talking in Vladikavkaz rather than an elevated action film.
- Rare, verified Ossetian expressions where natural. No invented transliterations, pretend authenticity, or constant ethnic stereotypes. Real expressions supplied by the group get priority; verify spelling, meaning, and register with a competent speaker before shipping.
- Frequent jokes, but preserve occasional genuinely serious scenes. Absurdity can be present even when an event has real stakes.
- Dialogue must reveal character motivation and redirect gameplay, not be a stream of catchphrases. Don't force profanity every sentence.
- The lines below are **fictional sample writing**, not quotes actually recorded from the people.

## 2. Character voices
| Speaker ID | Voice signature | Allowed known recurring phrase | Avoid |
|---|---|---|---|
| YAKUZA | Minimal responses, dodges accountability, breaks off for Zhinka's call | «АЫАЫ» | suddenly articulate gangster speeches |
| GABAR | Quick, analytical, sometimes exasperated; dry jokes, gaming and code | «ЕБАТЬ ЕБАТЬ», «Пашол нахуй», «ты блядун» | 24/7 gym sermons; infallible lecture machine |
| OLEZHKA | Young, usually grounded; occasionally imitates Gabar, snaps after persistent teasing | occasional Gabar phrases | constant hysteria / caricature |
| TIMKA | Soft-spoken, slow-to-anger, absurdly unbothered | «Я просто гасюсь», «ЗАРДА КАМ ИС МА СУПЕРКАСТЮМ», «Ма ма куы бахафай» | portraying Elyа as a controller |
| RYZHIK | Funny, friendly, protective; more severe if deceived | «Джабор, браат» (to Gabar) | nonstop shouting like Tega |
| TEGA | Grumpy, sleep-deprived, fast to snap at foolishness | «НУ ТЫ ДОЛБАЁЁЁБ!» | making every line the same scream |
| PASHA | Hyperactive, jumps topics; excited around computer/games and USA dream | «ГАБАР КИПИТ!» | actually incompetent at games; he plays PUBG well |
| KABAN | Ordinary, unpolished father in early acts; hard-edged later | No confirmed personal catchphrase | cartoon villain expositions early on |
| ELLANA | Everyday dialogue; calls about commitments; not mastermind | No confirmed phrase | making an actual person solely an abusive villain |
| ELYA | Kind, normal, not bossing Timka around | No confirmed phrase | conflating with Ellana |

## 3. Presentation contract
Reference style: side-by-side scene and *original* large pixel portrait; lower dialogue textbox; preserve top-down level scene while speaking. Camera may cut to expressive, cinematic pixel-art staging for chapter climaxes.
- Speaker portrait with state `neutral`, `angry`, `shocked`, etc. (IDs per character in Art Bible).
- Typewriter reveal (configurable speed, punctuation-aware pause), skip-to-end, next line, dialogue history and subtitles toggle. Subtitle accessibility: sufficient contrast, scalable text, no text embedded into art.
- Blink/mouth/idle portrait motion on limited pixel grid, no modern smooth brush painting; no face-swap photo plates in shipping game.
- Input: action key reveals line/advances; hold to speed; previously seen scenes may be skipped; user setting for instantaneous text.
- Audio: small 'voice blip' per speaker rather than full recorded voice acting; individual repeating meme samples only if separately approved, but default specification is **NO full VO**.
- On combat transition, duck adaptive music momentarily; ensure quick return to beat/bar aligned layer. Avoid audio stacking when dialogue is skipped.
- VHS distortion and camera shake should never compromise readability; provide reduced-motion and distortion toggles.

## 4. Dialogue data contract (Godot JSON or custom Resource)
```json
{
  "scene_id": "CYBERX_12_PASHA_GABAR_01",
  "event_id": "EV_CYBERX_ARCHIVE_DISCOVERY",
  "pov": "PASHA",
  "lines": [
    {"speaker": "PASHA", "emotion": "gabar_kipit", "text_ru": "ГАБАР КИПИТ!", "sound": "voice/pasha/excited"},
    {"speaker": "GABAR", "emotion": "annoyed", "text_ru": "Паша, что ты опять сделал?"},
    {"speaker": "PASHA", "emotion": "neutral", "text_ru": "Да ничего. Почти."}
  ],
  "entry_conditions": ["chapter_12_active"],
  "exit_actions": [{"type":"set_flag","name":"cyberx_archive_seen","value":true}]
}
```
Use structured gameplay flags rather than parsing Russian dialogue text to detect choices. Script revisions must preserve stable scene/event IDs. Provide internationalisation keys even when shipping Russian first.

## 5. Scene direction patterns
- In-level dialogue: sprite stays visible in gameplay background, portrait with 2–4 expression changes, quick line length.
- Hard cut: title card with date/place, limited-palette neon flashes, synth transition.
- Cinematic cutscene: 2–5 deliberate camera compositions with environmental motion; no long, non-skippable movies.
- Conflicting POV: same event_id, distinct authoring files with explicit perspective; preserve invariant facts while allowing unreliable narration.
- Memetic punchline: often one-line anticlimax after tense silence; do not explain jokes to the player.

## 6. Short original examples (to establish register; not final copy)
### SCENE `KIMONO_CONFRONTATION`
OLEZHKA: «Некит, какое кимоно?»
YAKUZA: «Ну, тебе надо было».
OLEZHKA: «Я на дзюдо не хожу, бля».
YAKUZA: «АЫАЫ».
OLEZHKA: «Да не аыаыкай, деньги где?»
[Phone vibrates: ЖИНЬКА. 0.8 sec pause.]
YAKUZA: «Ща, мне звонят».

### SCENE `CYBERX_ARCHIVE`
PASHA: «ГАБАР КИПИТ!»
GABAR: «ЕБАТЬ ЕБАТЬ. Что?»
PASHA: «Я их архив нашёл».
GABAR: «Ничего не отправляй».
PASHA: «А, поздно».
[Music ducks. Both portraits silent for 1.5 seconds.]
GABAR: «Ты блядун».

### SCENE `TEGA_NIGHT_SHIFT`
CUSTOMER: «Можно вас на секунду?»
TEGA: «Чё?»
CUSTOMER: «Здесь кто-то телефон забыл».
TEGA: «НУ ТЫ ДОЛБАЁЁЁБ! У МЕНЯ СМЕНА ЗАКОНЧИЛАСЬ!»

### SCENE `WIFE_CALLING_CLIMAX`
KABAN: «Некит, ты хоть один раз решишь сам?»
OLEZHKA: «Да постой ты уже».
[Incoming phone call: ЖИНЬКА; ambient sound muffles.]
YAKUZA: «Да. Щас еду».
OLEZHKA: «Куда?»
YAKUZA: «Домой».
[No punchline for 4 sec; then title: GO HOME.]

## 7. Ossetian/local-language QA
- Prefer expressions already supplied: «ЗАРДА КАМ ИС МА СУПЕРКАСТЮМ» and «Ма ма куы бахафай»; **do not treat the provided informal transliterations or translations as linguistically verified**.
- Before shipping, have speaker/translator verify original script, orthography, intended meaning, dialect (Iron where relevant), pronunciation, subtitles and whether the wording is appropriate in context.
- Keep local flavour in interactions and environmental details; avoid invented dialect and fake literal translations.

## 8. Mature content, access and distribution
- Optional content filters: profanity reduced only through authored alternative lines, not broken automatic replacements; violence controls handled separately.
- Clearly identify the entire story as a fictional parody; criminal allegations and humiliating scenes must not be presented as verified facts about the individuals portrayed.
- Collect consent from anyone whose photo, voice or identifiable fictional avatar appears in public builds. Private references should not be committed to public Git history.

## 9. Acceptance criteria
- 100% story dialogue in external structured resources, no hardcoded long scripts inside gameplay code.
- At least 2 distinctive voice samples / expression options per relevant lead in vertical slice; full VO is not required.
- Dialogue fast forward, skip, history, autosave/restore and accessibility controls verified.
- Correct character association: Elya ↔ Timka; Ellana/Zhinka ↔ Yakuza.
- Every branch conversation uses valid predicates and changes persistent state; no 'fake' consequential choices.
- Ossetian lines shipped only after explicit linguistic review; all exported story text proofread by a Russian native speaker.
- Timka, Tega, Gabar, Ryzhik, Pasha, Olezhka, Yakuza remain recognisable in wording without repetitive slogans.
