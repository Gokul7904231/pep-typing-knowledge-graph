# Python Typing PEP Knowledge Graph

A system that manually structures the design history of Python's typing
system into a knowledge graph, then reasons over that graph to react to
brand-new, unseen proposals — surfacing similar past PEPs and the
specific objections that were raised against them.

Built for the Calyb AI Engineering Intern Assignment (Domain A: Language
Evolution).

## The idea

Python's typing system evolved over ~8 years across a chain of connected
PEPs: PEP 3107 introduced bare annotation syntax with no meaning, PEP 483
and 484 gave it meaning and theory, and PEPs 526, 544, 585, and 604 each
extended or patched a specific limitation. That's a real decision graph —
proposals that build on, depend on, and get rejected in favor of one
another — not just a flat list of unrelated documents.

This project reads 8 of those PEPs by hand, extracts entities and
relationships from them manually (no NER libraries, no LLM-based
auto-extraction), and stores the result as an inspectable graph. A
reasoning engine then takes a new, never-before-seen proposal and
traverses that graph to answer: *has something like this been tried
before, and what happened to it?*

## How it works

**Two stages:**

1. **Build (offline, done once)** — `pep_data.py` contains hand-extracted
   notes for each PEP (concepts introduced, dependencies, objections
   raised). `build_knowledge.py` compiles this into a graph structure
   saved as `knowledge_state.json`.

2. **Reason (runtime, on new input)** — `reason.py` takes free-text
   describing a new idea, matches it against the graph using a
   hand-written keyword rule table, traverses related PEPs one hop out
   via their `extends`/`depends_on`/`relates_to` edges, and returns a
   structured JSON result: matched concepts, similar past proposals, the
   actual historical objections raised against them, and a
   recommendation.

No LLM is called anywhere in the pipeline. All matching, traversal, and
ranking is deterministic hand-written logic.

## Project structure

```
pep_project/
├── pep_data.py          # Manually extracted PEP notes (the raw knowledge)
├── build_knowledge.py   # Compiles pep_data.py into a graph → knowledge_state.json
├── reason.py             # Reasoning engine — run this with a new input
├── knowledge_state.json  # Serialized, inspectable knowledge graph (generated)
├── reading_notes.md      # Raw notes taken while reading each PEP
├── approach.md           # Design reasoning, tradeoffs, what's next (read first)
└── README.md             # This file
```

## Setup

Requires Python 3.8+. No external dependencies — standard library only.

```bash
git clone <this-repo-url>
cd pep_project
```

## Regenerate the knowledge state

```bash
python3 build_knowledge.py
```

This reads `pep_data.py` and writes `knowledge_state.json` fresh. Run
this any time `pep_data.py` changes (e.g. if more PEPs are added).

Expected output:
```
Wrote knowledge_state.json
  PEPs: 8
  Concepts: 19
  Objections: 32
  Edges: 74
```

## Give it a new input

```bash
python3 reason.py "your new proposal or idea, in plain English"
```

**Examples:**

```bash
python3 reason.py "What if we allowed a shorter union syntax like X | Y instead of Union[X, Y]"
```
→ surfaces PEP 604 directly, plus related precedent (PEP 483, 526, 484)
and the real objections raised against each at the time.

```bash
python3 reason.py "I want every class to automatically be treated as a protocol for structural duck typing"
```
→ surfaces PEP 544 and its six explicitly rejected alternatives.

```bash
python3 reason.py "I want a way to mark a function parameter as read-only or immutable"
```
→ correctly returns **no match** — this idea isn't covered by the 8 PEPs
modeled here, and the system reports that honestly instead of forcing a
false match.

Output is structured JSON, not prose — matched concepts, ranked similar
proposals, their objections, and a recommendation.

## Inspecting the knowledge base directly

`knowledge_state.json` is meant to be readable on its own, without
running any code. It contains three entity types (`peps`, `concepts`,
`objections`) and a flat `edges` list connecting them
(`introduces`, `depends_on`, `extends`, `relates_to`,
`raises_objection_against`). Open it in any JSON viewer or:

```bash
python3 -m json.tool knowledge_state.json | less
```

## Scope

8 PEPs covering the evolution of Python's typing system:
**3107, 482, 483, 484, 526, 544, 585, 604**.

Scoped narrowly on purpose — depth of extraction on a focused,
genuinely-connected set of PEPs, rather than shallow coverage of many.
See `approach.md` for the full reasoning behind this and every other
design decision (entity/relationship schema, tradeoffs, what would be
built next).

## Read this next

- **`approach.md`** — the design document: why this scope, why this
  schema, what tradeoffs were made, how the reasoning engine works, and
  what's next. Read this before the code.
- **`reading_notes.md`** — the raw, unedited notes taken while reading
  each PEP, showing the extraction process itself.
