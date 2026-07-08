"""
build_knowledge.py

This one's just plumbing — it takes the manually extracted notes from pep_data.py and reshapes them into a proper graph: entities + edges, all in one knowledge_state.json file.
No extraction happens here. All the actual reading-and-judgment work already happened by hand in pep_data.py. This script's only job is to take that raw data and lay it out as an 
explicit graph so reason.py can traverse it easily, and so anyone can pop open the JSON and inspect it on their own.

Run:
    python build_knowledge.py
Produces:
    knowledge_state.json
"""

import json
from pep_data import PEPS


def build():
    entities = {
        "peps": [],
        "concepts": [],
        "objections": [],
    }
    edges = []

    seen_concepts = {}  # concept_name -> concept_id, dedup across PEPs

    for pep in PEPS:
        pep_id = f"PEP-{pep['number']}"

        entities["peps"].append({
            "id": pep_id,
            "number": pep["number"],
            "title": pep["title"],
            "status": pep["status"],
            "summary": pep["summary"],
        })
        for concept_name in pep["concepts_introduced"]:
            if concept_name not in seen_concepts:
                concept_id = f"CONCEPT-{len(seen_concepts) + 1:03d}"
                seen_concepts[concept_name] = concept_id
                entities["concepts"].append({
                    "id": concept_id,
                    "name": concept_name,
                })
            else:
                concept_id = seen_concepts[concept_name]

            edges.append({
                "from": pep_id,
                "type": "introduces",
                "to": concept_id,
            })

   
        for dep_number in pep.get("depends_on", []):
            dep_id = f"PEP-{dep_number}"
            edges.append({
                "from": pep_id,
                "type": "depends_on",
                "to": dep_id,
            })

        for ext_number in pep.get("extends", []):
            ext_id = f"PEP-{ext_number}"
            edges.append({
                "from": pep_id,
                "type": "extends",
                "to": ext_id,
            })

        # relates_to edges (weaker link than extends/depends_on)
        for rel_number in pep.get("relates_to", []):
            rel_id = f"PEP-{rel_number}"
            edges.append({
                "from": pep_id,
                "type": "relates_to",
                "to": rel_id,
            })

        for obj in pep.get("objections", []):
            entities["objections"].append({
                "id": obj["id"],
                "text": obj["text"],
                "status": obj["status"],  
            })
            edges.append({
                "from": obj["id"],
                "type": "raises_objection_against",
                "to": pep_id,
            })

    knowledge_state = {
        "entities": entities,
        "edges": edges,
        "meta": {
            "domain": "Python PEPs — typing evolution",
            "pep_count": len(entities["peps"]),
            "concept_count": len(entities["concepts"]),
            "objection_count": len(entities["objections"]),
            "edge_count": len(edges),
        },
    }

    with open("knowledge_state.json", "w") as f:
        json.dump(knowledge_state, f, indent=2)

    print(f"Wrote knowledge_state.json")
    print(f"  PEPs: {knowledge_state['meta']['pep_count']}")
    print(f"  Concepts: {knowledge_state['meta']['concept_count']}")
    print(f"  Objections: {knowledge_state['meta']['objection_count']}")
    print(f"  Edges: {knowledge_state['meta']['edge_count']}")


if __name__ == "__main__":
    build()
