"""
reason.py

Simply feed it a brand-new proposal (not in the original PEP dataset) and it checks 
that idea against everything logged in knowledge_state.json. Comes back with: which past 
PEPs it resembles, whether something similar got rejected before (and why), and which concepts it touches.

Matching is just a hand-written keyword table (CONCEPT_KEYWORDS) — no NER, no LLM extraction. 
Same manual judgment call used to build the graph itself, just automated at query time.

Run:
    python reason.py "your new proposal text here"
"""

import json
import sys
from collections import defaultdict

# ---------------------------------------------------------------------
# Manually authored keyword -> concept mapping. This is hand-designed
# domain knowledge, not output from an automatic extraction tool.
# Each concept name here must match a concept "name" in pep_data.py.
# ---------------------------------------------------------------------
CONCEPT_KEYWORDS = {
    "annotation_syntax": ["annotation", "annotate", "colon syntax", ":"],
    "annotations_no_semantics": ["opt-in", "optional meaning", "no meaning"],
    "opt_in_metadata": ["metadata", "opt-in"],
    "typing_survey": ["survey", "literature", "other languages"],
    "prior_art_research": ["prior art", "other languages", "typescript", "compare"],
    "gradual_typing": ["gradual typing", "gradual", "partial typing"],
    "variance": ["variance", "covariant", "contravariant", "invariant"],
    "core_typing_primitives": ["union", "optional", "any type", "callable type"],
    "typing_module": ["typing module", "type hint", "type hints", "type checker"],
    "static_analysis_support": ["static analysis", "static checker", "mypy"],
    "dynamic_typing_preserved": ["dynamic typing", "runtime check", "optional runtime"],
    "variable_annotation_syntax": ["variable annotation", "annotate a variable", "class variable"],
    "classvar_marker": ["classvar", "class-level", "instance-level"],
    "structural_subtyping": ["structural", "duck typing", "protocol", "quacks like"],
    "protocol": ["protocol", "interface", "structural interface"],
    "runtime_checkable_opt_in": ["runtime checkable", "isinstance check", "runtime check"],
    "builtin_generic_subscription": ["built-in generic", "list[", "dict[", "subscriptable"],
    "collection_typing_unification": ["collection type", "typing.list", "parallel hierarchy"],
    "union_operator_syntax": ["union", "pipe syntax", "|", "or syntax", "x | y"],
    # Extra domain concepts not tied 1:1 to a single PEP, for matching
    # ideas that touch a broader theme (parameter constraints, readonly, etc.)
    "parameter_constraints": ["read-only", "readonly", "immutable parameter",
                               "immutable", "constant parameter", "frozen parameter"],
}


def load_knowledge(path="knowledge_state.json"):
    with open(path) as f:
        return json.load(f)


def match_concepts(new_input_text, knowledge):
    """
    Hand-written keyword matching (not NER, not an LLM call).
    Returns list of (concept_id, concept_name, match_count).
    """
    text_lower = new_input_text.lower()
    known_concept_names = {c["name"] for c in knowledge["entities"]["concepts"]}

    scored = []
    for concept_name, keywords in CONCEPT_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw.lower() in text_lower)
        if hits > 0:
            # find the concept's id if it exists in the graph
            concept_id = next(
                (c["id"] for c in knowledge["entities"]["concepts"] if c["name"] == concept_name),
                None
            )
            scored.append({
                "concept_name": concept_name,
                "concept_id": concept_id,  # may be None if it's an "extra" theme concept
                "score": hits,
                "in_graph": concept_id is not None,
            })

    scored.sort(key=lambda x: -x["score"])
    return scored


def find_peps_for_concepts(matched_concepts, knowledge):
    """Graph traversal: concept -> which PEPs introduce it."""
    concept_ids = {m["concept_id"] for m in matched_concepts if m["concept_id"]}
    pep_ids = set()
    for edge in knowledge["edges"]:
        if edge["type"] == "introduces" and edge["to"] in concept_ids:
            pep_ids.add(edge["from"])
    return pep_ids


def expand_related_peps(pep_ids, knowledge):
    """
    Graph traversal: walk extends/depends_on/relates_to edges one hop
    out from the directly matched PEPs, so we also surface PEPs that
    build on or relate to the matched ones (not just exact matches).
    """
    related = set(pep_ids)
    for edge in knowledge["edges"]:
        if edge["type"] in ("extends", "depends_on", "relates_to"):
            if edge["from"] in pep_ids:
                related.add(edge["to"])
            if edge["to"] in pep_ids:
                related.add(edge["from"])
    return related


def get_objections_for_peps(pep_ids, knowledge):
    """Graph traversal: PEP <- raises_objection_against <- Objection."""
    obj_by_pep = defaultdict(list)
    obj_lookup = {o["id"]: o for o in knowledge["entities"]["objections"]}
    for edge in knowledge["edges"]:
        if edge["type"] == "raises_objection_against" and edge["to"] in pep_ids:
            obj = obj_lookup.get(edge["from"])
            if obj:
                obj_by_pep[edge["to"]].append(obj)
    return obj_by_pep


def reason(new_input_text, knowledge):
    matched_concepts = match_concepts(new_input_text, knowledge)
    direct_pep_ids = find_peps_for_concepts(matched_concepts, knowledge)
    related_pep_ids = expand_related_peps(direct_pep_ids, knowledge)
    objections_by_pep = get_objections_for_peps(related_pep_ids, knowledge)

    pep_lookup = {p["id"]: p for p in knowledge["entities"]["peps"]}

    similar_proposals = []
    for pep_id in related_pep_ids:
        pep = pep_lookup.get(pep_id)
        if not pep:
            continue
        similar_proposals.append({
            "pep": f"PEP {pep['number']} — {pep['title']}",
            "status": pep["status"],
            "why_relevant": "directly matched" if pep_id in direct_pep_ids else "related via graph traversal",
            "objections_raised": [o["text"] for o in objections_by_pep.get(pep_id, [])],
        })

    # simple ranking: directly matched PEPs first, then by number of objections (more precedent = more useful)
    similar_proposals.sort(key=lambda p: (p["why_relevant"] != "directly matched", -len(p["objections_raised"])))

    return {
        "input": new_input_text,
        "matched_concepts": [
            {"concept": m["concept_name"], "keyword_hits": m["score"]}
            for m in matched_concepts
        ],
        "similar_past_proposals": similar_proposals,
        "recommendation": (
            f"Found {len(similar_proposals)} related PEP(s). Review the objections listed "
            f"above before drafting — several concern overlapping design territory."
            if similar_proposals else
            "No close precedent found in this knowledge base (typing PEPs only). "
            "This may be a genuinely novel area, or outside the scope of the 8 PEPs modeled here."
        ),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reason.py \"your new proposal text here\"")
        sys.exit(1)

    input_text = " ".join(sys.argv[1:])
    knowledge = load_knowledge()
    result = reason(input_text, knowledge)
    print(json.dumps(result, indent=2))
