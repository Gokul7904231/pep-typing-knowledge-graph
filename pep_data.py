"""
pep_data.py

This is me manually going through 8 typing-related PEPs and pulling out the structured bits 
— reading the actual Abstract, Rationale, and Rejected Ideas sections myself, then deciding what counts 
as a "concept" and what counts as an "objection." No NER tool, no auto-extraction, no LLM doing entity extraction 
for me — just me reading and tagging.
This file is the raw knowledge before build_knowledge.py turns it into the actual graph structure
"""

PEPS = [
    {
        "number": 3107,
        "title": "Function Annotations",
        "status": "Final",
        "summary": "Plumbing PEP. Legalizes annotation syntax but assigns "
                    "it zero built-in meaning — pure opt-in metadata slot. "
                    "484 is where the real payoff shows up.",
        "concepts_introduced": [
            "annotation_syntax",       # `:` after params, `->` before return
            "annotations_no_semantics",  # opt-in, no built-in meaning
            "opt_in_metadata"          # stored in func.__annotations__
        ],
        "depends_on": [318, 362],  # decorators precedent, Signature integration req
        "extends": [],
        "objections": [
            {"id": "obj_3107_1", "text": "Special syntax for generators was rejected as too ugly.", "status": "rejected"},
            {"id": "obj_3107_2", "text": "Stdlib objects for generic/higher-order functions were rejected due to too many thorny issues; left to third parties.", "status": "rejected"},
            {"id": "obj_3107_3", "text": "A standard type-parameterization syntax was punted despite considerable discussion, to let libraries figure it out first.", "status": "deferred"},
            {"id": "obj_3107_4", "text": "Standardizing interoperability across annotation tools was rejected as premature; conventions left to evolve organically.", "status": "rejected"},
            {"id": "obj_3107_5", "text": "Lambda annotations were rejected: parens around lambda params would be a backward-incompatible break, and lambdas are limited enough that a def rewrite is preferable.", "status": "rejected"},
        ],
    },
    {
        "number": 482,
        "title": "Literature Overview for Type Hints",
        "status": "Final",
        "summary": "Not a real proposal — an informational survey doc used "
                    "to justify design choices later made in 484. No syntax, "
                    "no mechanics to extend.",
        "concepts_introduced": [
            "typing_survey",
            "prior_art_research"
        ],
        "depends_on": [],
        "extends": [],
        "relates_to": [484],
        "objections": [],
    },
    {
        "number": 483,
        "title": "The Theory of Type Hints",
        "status": "Final",
        "summary": "The theoretical backbone behind 484's design choices — "
                    "gradual typing, variance — no syntax of its own.",
        "concepts_introduced": [
            "gradual_typing",
            "variance",
            "core_typing_primitives"  # Any, Union, Optional, Tuple, Callable
        ],
        "depends_on": [3107],
        "extends": [],
        "relates_to": [484],
        "objections": [
            {"id": "obj_483_1", "text": "Intersection types were cut from the core spec, with a note they might be added later.", "status": "deferred"},
            {"id": "obj_483_2", "text": "Python is naturally structural (duck typing), but the design leaned nominal for stricter checker control — acknowledged as a design tension, not a hard rejection.", "status": "tension"},
        ],
    },
    {
        "number": 484,
        "title": "Type Hints",
        "status": "Final",
        "summary": "The payoff PEP — gives PEP 3107's empty annotation "
                    "syntax actual meaning via the typing module. Everything "
                    "before this was setup; everything after is cleanup.",
        "concepts_introduced": [
            "typing_module",
            "static_analysis_support",
            "dynamic_typing_preserved"  # runtime checks stay optional
        ],
        "depends_on": [3107, 483, 482],
        "extends": [3107],
        "objections": [
            {"id": "obj_484_1", "text": "Evaluating hints offline-only was rejected — the interpreter can't distinguish a type hint from a random annotation without a defined meaning.", "status": "rejected"},
            {"id": "obj_484_2", "text": "A double-colon (::) syntax was rejected as ugly, not English-like, and would restrict support to Python 3.5+ only.", "status": "rejected"},
            {"id": "obj_484_3", "text": "New keywords such as where or requires were rejected since they would not work on earlier Python 3 versions.", "status": "rejected"},
            {"id": "obj_484_4", "text": "Using decorators or docstrings for typing was rejected as too verbose compared to plain annotations.", "status": "rejected"},
            {"id": "obj_484_5", "text": "Forward references to self-referencing classes remain a real friction point, requiring hacky string-literal annotations since names must exist before use.", "status": "limitation"},
        ],
    },
    {
        "number": 526,
        "title": "Syntax for Variable Annotations",
        "status": "Final",
        "summary": "Brings the same colon syntax to variables, not just "
                    "function params, and kills the `# type:` comment "
                    "workaround. Lots of rejected syntax here — a reminder "
                    "how much bikeshedding goes into 'just add a colon.'",
        "concepts_introduced": [
            "variable_annotation_syntax",
            "classvar_marker"  # distinguishes class-level vs instance-level vars
        ],
        "depends_on": [484],
        "extends": [484],
        "objections": [
            {"id": "obj_526_1", "text": "New keywords like var or local were rejected — var is too common as an identifier, local doesn't fit globals or class vars.", "status": "rejected"},
            {"id": "obj_526_2", "text": "Reusing def as a keyword was rejected since def already unambiguously means 'define function' to everyone.", "status": "rejected"},
            {"id": "obj_526_3", "text": "Tuple unpacking annotations (x, y: T) were rejected as ambiguous — unclear if both are T or T is distributed across them.", "status": "rejected"},
            {"id": "obj_526_4", "text": "Chained assignment annotations (x: int = y = 1) were rejected as hard to parse and ambiguous.", "status": "rejected"},
            {"id": "obj_526_5", "text": "Annotations inside with/for loop headers were rejected as likely to confuse the CPython parser.", "status": "rejected"},
            {"id": "obj_526_6", "text": "Auto-initializing unassigned annotated variables to None was rejected as messy and not worth a new singleton.", "status": "rejected"},
            {"id": "obj_526_7", "text": "Evaluating bare local annotations at runtime was rejected as costly, since it would populate a dict on every function call.", "status": "rejected"},
        ],
    },
    {
        "number": 544,
        "title": "Protocols: Structural subtyping (static duck typing)",
        "status": "Final",
        "summary": "Formalizes 'if it quacks like a duck' for static type "
                    "checkers — no explicit inheritance needed. A recurring "
                    "theme in its rejections is variance being a genuine "
                    "pain point across these PEPs.",
        "concepts_introduced": [
            "structural_subtyping",
            "protocol",
            "runtime_checkable_opt_in"
        ],
        "depends_on": [484, 483, 526],
        "extends": [483],  # formalizes the structural-typing tension noted in 483
        "objections": [
            {"id": "obj_544_1", "text": "Making every class a protocol by default was rejected — most classes have messy, implementation-heavy interfaces that are a bad fit.", "status": "rejected"},
            {"id": "obj_544_2", "text": "Allowing protocols to subclass normal classes was rejected because it breaks the transitivity of subtyping.", "status": "rejected"},
            {"id": "obj_544_3", "text": "Optional protocol members (as in TypeScript) were rejected to keep the design simple.", "status": "rejected"},
            {"id": "obj_544_4", "text": "Covariant subtyping of mutable attributes was rejected because it hides hard-to-spot bugs at runtime.", "status": "rejected"},
            {"id": "obj_544_5", "text": "Allowing manual overrides of inferred variance was rejected since it breaks transitivity and produces confusing error messages.", "status": "rejected"},
            {"id": "obj_544_6", "text": "Default isinstance() support was rejected as unreliable for structural checks, requiring an explicit @runtime_checkable opt-in instead.", "status": "rejected"},
        ],
    },
    {
        "number": 585,
        "title": "Type Hinting Generics In Standard Collections",
        "status": "Final",
        "summary": "Quality-of-life PEP: lets you write list[str] instead of "
                    "typing.List[str], retiring the duplicate typing "
                    "hierarchy. Its rejections are mostly about avoiding "
                    "scope creep into smarter isinstance() behavior.",
        "concepts_introduced": [
            "builtin_generic_subscription",
            "collection_typing_unification"
        ],
        "depends_on": [484, 526, 544],
        "extends": [484],  # replaces 484's parallel typing.List/Dict hierarchy
        "objections": [
            {"id": "obj_585_1", "text": "Doing nothing was rejected — forcing parallel imports from typing was seen as confusing and cumbersome.", "status": "rejected"},
            {"id": "obj_585_2", "text": "Full generics erasure at runtime was rejected since list[str] silently returning a bare list would break backward compatibility and introspection.", "status": "rejected"},
            {"id": "obj_585_3", "text": "Having isinstance(x, list[str]) silently ignore the generic parameter was rejected as misleading — it would look like a deep check but wouldn't be one.", "status": "rejected"},
            {"id": "obj_585_4", "text": "Having isinstance() perform real element-by-element runtime checks was rejected as potentially destructive on some collections and out of scope.", "status": "rejected"},
        ],
    },
    {
        "number": 604,
        "title": "Allow writing union types as X | Y",
        "status": "Final",
        "summary": "Syntactic sugar for Union via operator overload. "
                    "Conceptually the shortest PEP of the batch, but touches "
                    "core interpreter behavior, so the drama is mostly about "
                    "backport and compatibility risk rather than design.",
        "concepts_introduced": [
            "union_operator_syntax"
        ],
        "depends_on": [484, 526, 483],
        "extends": [484],  # replaces/simplifies 484's Union[X, Y] syntax
        "objections": [
            {"id": "obj_604_1", "text": "The new operator overload was argued against (not fully rejected) since it creates a dependency between the typing module and core builtins, complicating backports to older Python versions.", "status": "debated"},
            {"id": "obj_604_2", "text": "Extending isinstance()/issubclass() to accept the new syntax was argued against as requiring migrating parts of typing into builtins.", "status": "debated"},
            {"id": "obj_604_3", "text": "Classes that already implement a custom __or__ metaclass method will have that override the new union behavior — an acknowledged breaking-change risk.", "status": "limitation"},
        ],
    },
]
