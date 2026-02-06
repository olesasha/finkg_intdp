import re
import ast
import pandas as pd
from helpers.ontology import ENTITY_TYPES, BASE_RELATIONS, ALLOWED_SECTORS, SECTOR_SYNONYMS, ENTITY_TYPE_SYNONYMS

def extract_candidate_triples(text: str):
    """
    Ensure that there are 4 elements in each list. 
    Filters out malformed output of the LLM.
    """
    pattern = r"\[[^\[\]]+\]"
    matches = re.findall(pattern, text)

    triples = []
    for m in matches:
        try:
            val = ast.literal_eval(m)
            if isinstance(val, list) and len(val) == 4:
                triples.append(val)
        except Exception:
            continue

    return triples

def normalize_entity_type(raw_type: str) -> str:
    raw = raw_type.lower().strip()
    if raw in ENTITY_TYPES:
        return raw
    return ENTITY_TYPE_SYNONYMS.get(raw, "other")

def normalize_sector(raw_sector: str) -> str:
    """
    Normalizes raw sector string from LLM.
    Converts spaces → underscores, lowercases, and maps synonyms.
    Falls back to 'other' if unknown.
    """
    if not raw_sector:
        return "other"

    # lowercase and replace spaces with underscores
    raw = raw_sector.lower().replace(" ", "_").strip()

    # first check if it matches a canonical sector
    if raw in ALLOWED_SECTORS:
        return raw

    # then check synonyms
    return SECTOR_SYNONYMS.get(raw, "other")


def normalize_relation(rel: str) -> str:
    rel_clean = rel.lower().replace(" ", "_").strip()
    if rel_clean in BASE_RELATIONS:
        return rel_clean
    return "relates_to"  
    
def safe_split(entity: str):
    parts = entity.rsplit(":", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    else:
        return parts[0], "UNKNOWN"

def validate_triple(triple):
    """
    Normalizes a candidate triple.
    Returns a dictionary with canonical fields.
    Unknowns are mapped to 'other' or 'relates_to'.
    """
    e1, rel, e2, sector = triple

    e1_name, e1_type = safe_split(e1)
    e2_name, e2_type = safe_split(e2)

    e1_type = normalize_entity_type(e1_type)
    e2_type = normalize_entity_type(e2_type)
    rel = normalize_relation(rel)
    sector = normalize_sector(sector)

    return {
        "entity1": e1_name,
        "entity1_type": e1_type,
        "rel_type": rel,
        "entity2": e2_name,
        "entity2_type": e2_type,
        "sector": sector
    }

def log_fallback(triple):
    # simple print/log for now
    print(f"Fallback detected: {triple}")
