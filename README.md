# Python Typing PEP Knowledge System

A small system that structures the history and reasoning behind 8 core
Python typing PEPs into a graph, then reasons over that graph to react
to a brand-new (unseen) proposal.

## What it does

1. `pep_data.py` — manually extracted notes on 8 typing PEPs (concepts
   introduced, dependencies, objections raised, later extensions).
   This is the raw knowledge, written by hand from reading each PEP.
2. `build_knowledge.py` — compiles `pep_data.py` into a graph-structured
   `knowledge_state.json` (entities: PEPs, Concepts, Objections; edges:
   introduces, depends_on, extends, relates_to, raises_objection_against).
3. `reason.py` — takes a new proposal (text you type), matches it against
   the graph using a hand-written keyword rule table, traverses related
   PEPs, and returns a structured JSON output: similar past proposals,
   objections previously raised, and a recommendation.

## Setup

No dependencies beyond the Python standard library. Python 3.8+.

```bash
cd pep_project
```

## Regenerate the knowledge state

```bash
python3 build_knowledge.py
```

This reads `pep_data.py` and writes `knowledge_state.json`. Run this
whenever `pep_data.py` changes (e.g. if you add more PEPs).

## Run the reasoning engine on a new input

```bash
python3 reason.py "your new proposal or idea, in plain English"
```

Example:

```bash
python3 reason.py "What if we allowed a shorter pipe-based union syntax like X | Y"
```

Output is structured JSON: matched concepts, similar past PEPs (with the
real objections raised against them), and a recommendation.

## Files in this repo

| File | Purpose |
|---|---|
| `pep_data.py` | Manually extracted PEP notes (the raw knowledge) |
| `build_knowledge.py` | Compiles notes into graph JSON |
| `knowledge_state.json` | The serialized, inspectable knowledge graph |
| `reason.py` | Reasoning engine for new inputs |
| `approach.md` | Design reasoning and tradeoffs (read this first) |

## Scope

8 PEPs covering the evolution of Python's typing system: 3107, 482, 483,
484, 526, 544, 585, 604. See `approach.md` for why this scope was chosen.
