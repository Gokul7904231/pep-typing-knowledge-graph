# Approach

Raw reading notes taken while extracting each PEP are included in
`reading_notes.md` — they show the extraction process (concepts spotted,
objections flagged, cross-PEP observations) before it was formalized into
the structured `pep_data.py` used to build the graph.

## Domain and scope

Domain A: Python's design history, via PEPs (Python Enhancement Proposals).

I narrowed to **8 PEPs covering the evolution of Python's typing system**:
3107, 482, 483, 484, 526, 544, 585, 604.

I picked typing specifically because it's one of the few areas in Python's
history where you can trace a genuinely continuous multi-year design
conversation: 3107 lays down syntax with no meaning, 483/482 supply the
theory and research behind giving it meaning, 484 is the payoff PEP that
actually defines the typing system, and 526/544/585/604 each extend or
patch a specific limitation of 484 in a different direction (variables,
structural typing, collection ergonomics, union syntax). That gives real
`extends` / `depends_on` edges to model, not just a flat list of unrelated
proposals.

I deliberately kept this to 8 rather than trying to cover all typing PEPs
(there are 20+). Reading each PEP's Abstract, Rationale, and Rejected
Ideas sections closely enough to extract genuine objections (not just
copy the summary) takes real time per PEP. Depth on 8 well-understood
PEPs produces a more defensible graph than shallow coverage of 20.

## Entities and relationships

**Entities:**
- `PEP` — number, title, status, a short summary I wrote after reading it
- `Concept` — a specific design idea a PEP introduces, named by me (e.g.
  `structural_subtyping`, `union_operator_syntax`), not extracted
  automatically. Concepts are deduplicated across PEPs so a later PEP can
  reference a concept an earlier one introduced.
- `Objection` — a single, specific argument or rejected alternative,
  pulled individually from a PEP's Rejected Ideas / Alternatives section.

**Relationships:**
- `introduces` (PEP → Concept)
- `depends_on` (PEP → PEP) — a hard prerequisite
- `extends` (PEP → PEP) — a PEP that specifically patches or builds on
  another PEP's mechanism (e.g. 585 extends 484 by replacing its
  parallel `typing.List`/`typing.Dict` hierarchy)
- `relates_to` (PEP → PEP) — a weaker connection (e.g. 482 is background
  research for 484, not a hard dependency)
- `raises_objection_against` (Objection → PEP)

**Why I split Objection into its own entity instead of a text field on
PEP:** early on I considered just storing objections as a list of
strings on each PEP dict (which is close to what I did in the raw notes).
But collapsing them loses two things: (1) the ability to tag each
objection with a status (`rejected` vs `deferred` vs `debated` vs
`limitation` — PEP 604's objections were explicitly *debated*, not
rejected outright, which is a real distinction the PEP text makes), and
(2) the ability for the reasoning engine to return objections as
individually addressable, gradeable evidence rather than one paragraph.
Making Objection a first-class node with its own id was the deciding
factor that let `reason.py` return "here are the 3 specific concerns
raised" instead of "here is one blob of concern text."

I did **not** model `Author` as an entity. Several PEPs in this set share
overlapping authors (Guido van Rossum in particular), but with only 8
PEPs the author graph would be trivial (mostly one hub node) and
wouldn't add real reasoning value for the "new input" use case, which is
about design precedent, not who to CC. I'd add this back if the scope
grew to include contested-authorship debates like PEP 572.

## How the knowledge representation was built

All extraction was manual: I read each PEP's Abstract, Rationale, and
Rejected Ideas/Alternatives sections directly and wrote down, in my own
words, what concept it introduced and what specific objections were
raised, with enough context to know *why* (e.g. "lambda annotations were
rejected because parens around lambda params would be a backward
incompatible break" — not just "lambda annotations: rejected").

No NER library, auto knowledge-graph tool, or LLM entity-extraction
prompt was used to produce `pep_data.py`. `build_knowledge.py` is purely
mechanical reshaping (dict → graph nodes/edges) — no interpretive
decisions happen in that script; all interpretive decisions were made by
hand while writing `pep_data.py`.

**Tradeoff:** this means the graph only knows what I personally decided
was worth recording. A different reader would draw slightly different
concept boundaries or catch different objections. I think this is
actually the right tradeoff for what's being evaluated here — the
judgment calls are the point — but it does mean the graph is not
exhaustive, and a truly complete graph of "everything ever debated about
Python typing" is out of scope for what one person can hand-extract in
a day.

## How the system reasons over a new input

`reason.py` takes free text (a new, unseen proposal) and:

1. Matches it against a **hand-written keyword table** (`CONCEPT_KEYWORDS`
   in `reason.py`) mapping phrases to concept names. This is the same
   kind of manual judgment used to build the graph, just applied at
   query time instead of build time — I decided which words signal which
   concept, rather than using a classifier or embedding similarity.
2. Finds which PEPs directly introduced the matched concepts (graph
   traversal via `introduces` edges).
3. Expands one hop outward via `extends` / `depends_on` / `relates_to`
   edges, so related precedent surfaces even if it doesn't share exact
   keywords (e.g. a union-syntax question also surfaces PEP 483, which
   defined `Union` in the first place, even though 483's summary doesn't
   use the word "pipe").
4. Pulls every `Objection` node attached to the resulting PEPs.
5. Ranks results (direct matches first, then by objection count, as a
   simple proxy for "how much real precedent exists here").
6. Returns structured JSON — not prose — with matched concepts, ranked
   similar proposals, their real historical objections, and a one-line
   recommendation.

No LLM is called anywhere in this pipeline. All matching and ranking is
deterministic and inspectable.

## What I'd build next

- **Weighted/fuzzy concept matching.** The keyword table is exact-substring
  matching, which is brittle to phrasing (a proposal that says "duck
  typing" but not "structural" would miss PEP 544 entirely unless I'd
  anticipated that phrasing). A hand-built synonym expansion or a small
  hand-labeled training set for a simple classifier (not a pretrained
  NER model) would make matching more robust while staying within the
  "no automatic extraction tool" constraint.
- **Recency/version weighting** in the ranking step — right now a PEP
  from 2014 and one from 2019 are weighted identically; PEPs that
  represent the *current* state of the language (e.g. 604 superseding
  484's Union syntax) should probably rank higher than the PEP they
  replaced.
- **Expand to 15-20 typing PEPs** (adding e.g. PEP 560, 563, 646, 675,
  695) now that the extraction workflow and schema are proven, to give
  the reasoning engine more precedent to draw from for a wider range of
  new proposals.
- **Objection resurfacing detection** — flag when a new proposal is
  likely to trigger an objection that recurred across *multiple* past
  PEPs (variance issues came up in both 483 and 544 in this dataset),
  since a recurring objection is stronger evidence than a one-off.
