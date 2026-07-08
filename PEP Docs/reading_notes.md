# PEP Reading Notes

Raw notes taken while reading each of the 8 PEPs directly, before formalizing
them into `pep_data.py`. Kept unedited/informal on purpose — this is the
actual extraction process, not a polished summary.

---

## 1. PEP 3107 — Function Annotations

TL;DR: pure syntax, zero semantics.

`def f(x: int) -> str:` just populates a dict. Does nothing by itself.

**New idea:**
- new syntax: `:` after params, `->` before return type
- evaluated once at def-time, stuffed into `func.__annotations__` dict
- NO built-in meaning — fully opt-in. up to 3rd party libs to actually use it (type checking, RPC marshaling, etc.)
- ex:
```python
def compile(source: str, filename, mode='eval') -> Code: ...
# compile.__annotations__ == {'source': str, 'return': Code}
```

**Depends on:**
- PEP 318 (decorators) → ppl were already hacking decorators to bolt metadata onto fns, this PEP standardizes that pattern properly
- PEP 362 (Signature objects) → hard integration req, not optional — Signature objs must expose these annotations

**Rejected (bikeshedding city):**
- special syntax for generators — Guido: "too ugly"
- stdlib objects for gen/higher-order fns — "too many thorny issues" for stdlib → left to 3rd party
- standard type-parameterization syntax — despite "considerable discussion" → punted so libs could figure it out first
- standardizing interop across annotation tools — called "premature", let conventions evolve organically instead of forcing one
- lambda annotations — no. reasons:
  - parens around lambda params = backward-incompat break
  - lambdas "neutered anyway" (lmao ok)
  - just rewrite as `def` if you need annotations

**Later fixed/extended by:**
- PEP 484 → gives the syntax actual meaning (type hints system). 3107 = empty container, 484 = fills it in
- PEP 526 → extends the same `:` syntax to var annotations (local + class vars, not just fn params)

*(summary: 3107 = plumbing PEP. Legalizes syntax, does nothing on its own — 484 is where the real payoff shows up.)*

---

## 2. PEP 482 — Literature Overview for Type Hints

TL;DR: not a real PEP, just a survey doc. no code, no syntax.

**New idea:**
- literally none — informational only, no lang features
- surveys other langs (TypeScript, Dart, Hack, ActionScript) + existing py tools (mypy, PyCharm) to justify choices made in 484

**Depends on:**
- companion/background doc for PEP 484 (the real spec)

**Rejected:** none — it's just a lit review, nothing to argue about

**Later fixed/extended by:** n/a, no mechanics to extend

*(sum: basically 484's research appendix.)*

---

## 3. PEP 483 — The Theory of Type Hints

TL;DR: the math/theory backbone. no syntax, just concepts (gradual typing, variance).

**New idea:**
- formalizes gradual typing + variance (covariant/contravariant)
- introduces core building blocks: Any, Union, Optional, Tuple, Callable

**Depends on:**
- theoretical backbone for PEP 484
- assumes syntax already laid down by PEP 3107

**Rejected:**
- intersection types — "might add" later, but cut from core for now
- nominal vs structural subtyping — acknowledged python is naturally structural (duck typing) but leaned nominal for stricter checker control (not a hard rejection, more a design tension)

**Later fixed/extended by:**
- PEP 544 → fully formalizes structural subtyping (protocols)
- PEP 604 → upgrades the Union syntax defined here

*(Note: pure theory PEP. this is the "why" behind 484's design choices.)*

---

## 4. PEP 484 — Type Hints

TL;DR: THE big one. gives PEP 3107's empty syntax actual meaning via typing module.

**New idea:**
- standard typing module
- offline static analysis + generics
- python stays dynamically typed — zero mandatory runtime checks

**Depends on:**
- PEP 3107 (annotation syntax)
- PEP 483 (theory)
- PEP 482 (lit review)

**Rejected:**
- hints evaluated offline only — breaks backward compat, interpreter can't tell hint vs random annotation
- `::` double-colon syntax — "ugly", not English-like, limits to 3.5+ only
- new keywords (where/requires) — won't work on earlier py3 versions
- decorators/docstrings for typing — too verbose vs plain annotations
- forward declarations — big friction point: self-referencing classes need hacky string literals (e.g. 'Tree') since names must exist before use

**Later fixed/extended by:**
- PEP 526 → adds variable annotations, kills `# type:` comments
- PEP 585 → deprecates parallel collection hierarchy (typing.List etc)
- PEP 604 → simplifies verbose Union syntax

*(Note: the payoff PEP. everything before this was setup, everything after is cleanup.)*

---

## 5. PEP 526 — Syntax for Variable Annotations

TL;DR: brings `:` annotation syntax to variables (not just fn params). kills `# type:` comments.

**New idea:**
- direct colon syntax for globals/locals/class vars/instance vars
- ClassVar to mark class-level vs instance-level vars

**Depends on:**
- expands directly on PEP 484

**Rejected:**
- new keywords var/local — var too common as a name, local doesn't fit globals/class vars
- using def as keyword — def = "define function" to everyone, confusing overload
- tuple unpacking annotations (x, y: T) — ambiguous: both are T? or T distributed across?
- chained assignment annotations (x: int = y = 1) — hard to parse, ambiguous
- annotations in with/for loops — would confuse CPython parser
- auto-init unassigned vars to None/JS-style undefined — messy, new singleton not worth it
- evaluating bare local annotations — costly, would populate dicts on every fn call

**Later fixed/extended by:**
- nothing explicit overrides it, but becomes baseline syntax for protocol vars in PEP 544

*(Note: lots of rejected syntax here — good reminder how much bikeshedding goes into "just add a colon.")*

---

## 6. PEP 544 — Protocols: Structural subtyping (static duck typing)

TL;DR: formalizes "if it quacks like a duck" for static type checkers. no explicit inheritance needed.

**New idea:**
- Protocols = structural subtyping
- class matches protocol if it has the right methods/attrs, no explicit ABC inheritance required

**Depends on:**
- complements nominal typing from PEP 484 + PEP 483
- uses PEP 526 syntax for protocol variable definitions

**Rejected:**
- every class = protocol by default — most classes have messy impl-heavy interfaces, bad fit
- protocols subclassing normal classes — breaks transitivity of subtyping
- optional protocol members — TS has these, but rejected to keep it simple
- covariant subtyping of mutable attrs — hides hard-to-spot bugs at runtime
- overriding inferred variance — breaks transitivity + messes up error msgs
- isinstance() support by default — structural instance checks unreliable → needs explicit @runtime_checkable opt-in

**Later fixed/extended by:** none listed

*(Notes: lots of "rejected because breaks transitivity" — variance clearly a recurring pain point across these PEPs.)*

---

## 7. PEP 585 — Type Hinting Generics In Standard Collections

TL;DR: lets you write list[str] instead of typing.List[str]. kills the duplicate typing hierarchy.

**New idea:**
- built-in collections (list, dict, tuple) parameterizable directly via `__class_getitem__`
- no more need for parallel typing.List, typing.Dict, etc.

**Depends on:**
- builds on PEP 484, 526, 544, 560, 563 incrementally

**Rejected:**
- do nothing — forcing parallel imports from typing is confusing/cumbersome
- generics erasure — list[str] just returning bare list at runtime breaks backward compat + kills runtime introspection
- isinstance(x, list[str]) ignoring generics silently — returning True here is misleading, looks like deep check but isn't
- isinstance doing actual runtime type checks — iterating every element to verify = destructive on some collections, way out of scope

**Later fixed/extended by:**
- itself is a fix/extension of PEP 484's old parallel hierarchy (not extended further)

*(Note: straightforward QoL PEP. mostly rejecting "make isinstance smarter" ideas — scope creep avoided.)*

---

## 8. PEP 604 — Allow writing union types as X | Y

TL;DR: X | Y instead of Union[X, Y]. syntactic sugar via operator overload.

**New idea:**
- overloads `|` (bitwise OR) for types → `X | Y == Union[X, Y]`
- also valid inside isinstance()/issubclass() calls

**Depends on:**
- heavily modifies Union syntax from PEP 484 + PEP 526

**Rejected:**
- (argued against, not fully rejected) new operator — creates dependency between typing module and core builtins, hard to backport to older py versions
- (argued against) extending isinstance/issubclass — requires migrating all of typing into builtins
- metaclass override friction — acknowledged breaking change: metaclasses already implementing `__or__` will just override this new behavior

**Later fixed/extended by:**
- none — this is the final/ultimate fix for Union's clunky syntax

*(Note: shortest PEP of the batch conceptually, but touches core interpreter behavior (operator overloading) so drama is mostly about backport/compat risk, not design.)*
