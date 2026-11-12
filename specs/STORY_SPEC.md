# STORY_SPEC — АЫАЫ: ПОСЛЕДНИЙ СКУФ
Version: 1.0-draft | Status: requirements approved, narrative implementation pending | 2026-11-13

## 1. Contract
- Desktop single-player nonlinear top-down pixel-art action comedy set in a recognisable, *fictionalised* Vladikavkaz (2026).
- 70% local absurd humour / 30% consequential criminal thriller; absurdity can interrupt dangerous scenes. Certain emotional scenes remain wholly serious.
- 7 playable leads: Yakuza/Nekit (principal focal character), Gabar, Olezhka, Timka, Ryzhik, Tega, Pasha. Supporting: Elyа (Timka's girlfriend), Ellana/Zhinka (Yakuza's girlfriend), Denis 'Kaban' (father to Yakuza and Olezhka), Max 'Mentor', fictional supporting villains, Jack the dog, Akhshar.
- PREMISE: "PRIME Recovery System" purports to restore men's lost 'prime'; behind its public front are fraud and unlawful activity. The *fictional in-game version* of Denis 'Kaban' secretly runs PRIME; Max is its public face. Photos and real-life anecdotes are references for a fictional parody, NOT assertions about actual individuals' conduct.
- Core themes: pseudo-motivation scams, inflated self-image, financial shortcuts, family responsibility, separate lives, broken loyalties.
- Main intended ending: WIFE CALLING — Nekit abandons an unresolved confrontation to go home after Ellana's call. Multiple genuinely different endings must be reachable by actions across the campaign.

## 2. Character arc and motive invariants
| ID | Drive | Personal conflict | Distinct narrative function |
|---|---|---|---|
| YAKUZA | Earn money, satisfy Zhinka's requests, dodge accountability | Signs PRIME agreement, financial lies involving Olezhka and 'kimono' | Inciting bad choice; dominant POV; no late superhuman transformation |
| GABAR | Find what PRIME is doing, help Olezhka, protect his own open-source reputation | His publicly released parody software is reused without consent; suspected wrongly | Evidence/technical perspective, not omniscient hero |
| OLEZHKA | Protect himself and confront brother; loyalty to Gabar | Family loyalty vs honesty | Emotional pivot of choices |
| RYZHIK | Protect associates; resolve unpaid/overcharging grievance | Distrusts Yakuza for charging his acquaintance for a favour | Supplier/witness/alternative view on same incidents |
| PASHA | Escape debt and fund future move to USA | May try to monetise evidence, endangering CyberX | Erratic agent, unintended leaks |
| TEGA | End exhausting shifts and return to games | PRIME visitors intrude on hookah-bar workplace | Witness, finds device, reluctant ally |
| TIMKA | Keep peaceful life with Elyа and Jack | PRIME uses images of former gym 'prime'; dragged into mess | Morally kind witness, contrasts Yakuza |

Ellana is not the criminal mastermind. Elyа does not control Timka; his changes are voluntary. Neither woman should be made a scapegoat. Oleg is 18 and mostly sensible; his behaviour is not exaggerated beyond the approved 2/10 baseline despite overall exaggerated portrait style.

## 3. Story chronology vs presentation order
The story takes place across a past flashback period, the beginning of PRIME's promotional campaign, the escalation, and its downfall. Introduce *past* before *now* to establish contrasts; later re-contextualise scenes via other leads. Date/times must have a canonical event ID and timestamp, even when player sees scenes out of sequence.

### Canonical act slots (21 chapters; story events subject to authored variant scenes)
- Act I (1–4): 01 THE MISSED FIGHT [Yakuza, impossible-to-win toilet flashback]; 02 THE TITAN [Timka flashback]; 03 THE LAST ARMRESTLER [Tega flashback]; 04 THE FINAL SKUF [Yakuza recruited by PRIME].
- Act II (5–8): 05 THE ORIGINAL PRIME [Gabar/Olezhka scrutinise marketing]; 06 THE BREAKER [Ryzhik supplier dispute]; 07 THE AMERICAN PROGRAM [Pasha offered a dubious opportunity]; 08 WIFE APPROVAL [Yakuza training, takes delivery job].
- Act III (9–12): 09 THE NIGHT SHIFT [Tega overhears meeting, finds phone]; 10 THE KIMONO [Olezhka confronts Yakuza's false pretext]; 11 THE DOG WALKER [Timka witnesses transfer while walking Jack]; 12 CYBERX [Pasha's archive discovery, several POVs].
- Act IV (13–17): 13 NO REFUNDS [Ryzhik investigates supplier fraud]; 14 AGENT SWARM [Gabar links data; false implication via open-source code]; 15 THE SUPERSUIT [Timka confronts use of old photos]; 16 THE AMERICAN NIGHTMARE [Pasha discovers data misuse]; 17 BROTHERHOOD [Olezhka confronts Yakuza].
- Act V (18–21): 18 THE BETRAYAL [leaked GABAR PRIME ENGINE allegation causes group split]; 19 FOUNDING INVESTOR [Nekit's 15k ₽ 'investment' exposed; coercive paperwork]; 20 THE ARCHITECT [Denis/Kaban revealed, organiser confrontation]; 21 THE LAST CALL [branch-specific climax and epilogue].

The 21 chapter slots are a **planning baseline**, not a claim that content/levels are already finished. Each slot may contain cutscenes and differently playable scene variants; do not silently add 20 more full-sized combat levels.

### Misinterpretation/reveal pairs
- PRIME promotional video: Yakuza sees fame; Gabar sees misleading fitness claims.
- `THE KIMONO`: Yakuza portrays a family emergency; Olezhka reveals he never practised judo.
- CYBERX: Pasha views his file-copy as helping; Gabar's POV reveals it inadvertently exposes their location.
- `GABAR PRIME ENGINE`: appears to implicate Gabar; verified source-history proves his code was repurposed without permission.
- Opening Yakuza POV plays like a grim confrontation; witness POV undercuts pompous framing.

## 4. Causality and three-step reveal
1. Public face **Max Mentor** seems to be PRIME's owner; false but plausible clues.
2. `GABAR PRIME ENGINE` produces false suspicion of Gabar via misused open-source parody project; player can uncover proof of non-involvement.
3. **Denis 'Kaban'** is revealed as fictional PRIME founder and father of Yakuza/Olezhka. Further evidence: Yakuza invested 15,000 ₽ earlier through a suspicious offer, was put in paperwork and later selected as 'Patient Zero'. **Being in paperwork does not imply that he is legally guilty**; the scheme's operators exploit the ambiguity.

Avoid an unsupported leap where a 15k transfer 'automatically' makes Yakuza criminally culpable. Evidence must show Kaban's control through signed authorisations, witness testimony, and financial trails rather than resemblance/claims alone.

## 5. Genuine branching: state and gates
Events must use stable IDs; dialogue options and gameplay outcomes modify persistent flags and route eligibility. Branch selection is deterministic and replayable. A single late multiple-choice screen is insufficient.

### Persistent story state (authoritative)
```yaml
story:
  chapter_complete: {}            # Map chapter_id -> bool
  evidence:
    open_source_origin: false     # proof Gabar's code preceded PRIME and was reused
    founding_records: false      # early financing, coercive paperwork
    illegal_operations: false    # verified PRIME criminal evidence
    tegas_phone: false           # device clue
    pashas_backup: false         # surviving archive copy
  relationships:                  # each range -2..+2
    yakuza_olezhka: 0
    yakuza_ryzhik: 0
    gabar_pasha: 0
  choices:
    kimono_truth: false          # Yakuza admits use of Olezhka's name
    pasha_shared_evidence: false # instead of trying to sell it
    ryzhik_warned: false         # warning Ryzhik rather than running away
    gabar_exonerated: false
    yakuza_accepted_responsibility: false
  endings:
    unlocked: []                 # route IDs, not merely epilogue cosmetics
    completed: []
```

### Decision points and visible consequences
| ID | Player decision/action | Immediate consequence | Downstream divergence |
|---|---|---|---|
| D01 `KIMONO_TRUTH` | Yakuza admits the lie / doubles down | Olezhka reacts, bond changes | Olezhka helps/denies access in Act V; variant mission entry |
| D02 `PASHAS_BACKUP` | Preserve evidence for friends / try to monetise | CyberX exposure risk | Security/escape variant at 12/16; Pasha-Gabar trust |
| D03 `RYZHIK_WARNING` | Warn Ryzhik / conceal supplier connection | Supplier safe or exposed | Ryzhik rival-or-ally confrontation at 13/18 |
| D04 `OPEN_SOURCE_PROOF` | Acquire verifiable project history / leave it | Suspicions persist | Gabar questioned by group or publicly cleared at 18 |
| D05 `TEGA_PHONE` | Secure device in 09 and decode with evidence in 14 | Unlocks independent corroboration | Simplifies proof vs Kaban in 20; route to third ending |
| D06 `YAKUZA_RESPONSIBILITY` | Take responsibility for debt/consequences / deflect | Character dialogue and risk | Gates alternate climax choices at 21 |

### Ending contracts and real mission variants
- `ENDING_WIFE_CALLING` **default and canonical**: available regardless of state, but exact exit route/aftereffects depend on ally statuses. In chapter 21 Yakuza leaves after Zhinka's call. Chapter 21B remains playable as remaining six navigate evidence escape/public exposure. Relationship consequences and whether Kaban is exposed hinge on accumulated evidence. This is not simply 'press leave' to instantly skip the level.
- `ENDING_BROTHERHOOD`: unlocked if `kimono_truth`, `yakuza_accepted_responsibility`, and evidence `illegal_operations` are true; Olezhka supports Yakuza in variant 21A. Yakuza stays, helps expose father. Unique playable route and conversation, not just recoloured cinematic.
- `ENDING_FAMILY_BUSINESS`: available if Yakuza repeatedly conceals truth and lacks key evidence while reaching 21; he sides with father. Alternate playable escape/cover-up sequence; friends' fates differ. **Never portray this as a 'good' choice.**
- `ENDING_REAL_PRIME` (secret): requires `open_source_origin`, `founding_records`, `illegal_operations`, `tegas_phone`, `pashas_backup`, plus secrets/side stories (including Tega's absurd dream and kimono record). Adds unique bonus epilogue and optional rescue/mutual accountability scene; no contradiction with primary ending classification: treat it as a *post-story secret route*, not an arbitrary override.

### Ending matrix requirements
Each route must change at least: (a) one playable encounter/escape path, (b) one permanent relationship outcome, (c) distinct final dialogue and cutscene, (d) two character epilogue outcomes. QA shall test all gates, plus absent/partially complete evidence cases.

## 6. Secret missions
- `SECRET_SUPPOSITORY_CANNON`: Tega after sleep deprivation imagines shooting a medical suppository at his brother Akhshar; *surreal slapstick, not real physical harm*. The projectile ricochets into his own monitor. Unlock via three optional memorabilia; nonessential to canonical timeline.
- `SECRET_BROKEN_TOOTH`: Ryzhik's breakdance mishap.
- `SECRET_BATHROOM_INCIDENT`: drunk Pasha knocks a glass, domino effect breaks bidet; Gabar tries to give water.
- `SECRET_JACK_REVENGE`: Jack marking Timka.
- `SECRET_PRIME_PHOTOS`: photo album of past Timka and Yakuza, with fictionalised memories.

## 7. Character and real-world safeguards
- Names, images, personal relationships, and events based on real people: this is explicitly a fictional, exaggerated parody; **fraud, assault, criminal control and manipulation by Kaban/others are strictly fictional plot inventions**. Never market these as established real-world accusations.
- Before distributing builds beyond the closed friend group or publishing assets, collect permission to use identifiable likenesses and voice clips, and confirm suitability of personal jokes. Reference photos should be private and excluded from public repos by default.
- All game music, art and dialogue are original or properly licensed; no tracing/copying source-game art or music.

## 8. Narrative QA / acceptance criteria
- All seven playable leads have meaningful scenes, distinct motives and at least one explicit cross-POV reveal.
- Six decision points have persistence, reachable states, UI feedback when appropriate, and tests.
- Every ending differs via gameplay as well as prose; the primary route WIFE CALLING remains reachable.
- Chronology validated through a single event ledger: character cannot appear in incompatible simultaneous locations without flashback/time jump.
- Repeated scenes share canonical event IDs; dialogue differences are POV-specific, not timeline contradictions.
- Elya and Ellana are never mixed up. Timka's walking window 19:30–20:30 is respected or deviation explicitly explained.
- In-game fiction disclaimer is available in credits/about and appears before the game as appropriate.

## 9. Not yet locked
Exact mission maps, boss movesets, route charts, full scripts and chronology timestamps require production design and playtesting. The 21-chapter plan and ending flags are the approved starting target, not a substitute for per-chapter specs.
