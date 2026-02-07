import re
import ast
import pandas as pd
from helpers.ontology import ENTITY_TYPES, BASE_RELATIONS, ALLOWED_SECTORS, SECTOR_SYNONYMS, ENTITY_TYPE_SYNONYMS
import pycountry

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

def normalize_countries(name: str, entity_type: str):
    # clean name (punctuation + whitespace)
    if isinstance(name, str):
        cleaned = re.sub(r"[^\w\s]", "", name)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
    else:
        cleaned = name

    # try country lookup
    try:
        pycountry.countries.lookup(cleaned)
        is_country = True
    except Exception:
        is_country = False

    # case handling
    if is_country:
        return cleaned, "country"
    if entity_type == "country":
        return cleaned, "other"
    return cleaned, entity_type


def normalize_sector(raw_sector: str) -> str:
    if not raw_sector or not isinstance(raw_sector, str):
        return "other"

    raw = raw_sector.lower().replace(" ", "_").strip()

    if raw in ALLOWED_SECTORS:
        return raw

    if raw in SECTOR_SYNONYMS:
        return SECTOR_SYNONYMS[raw]

    return "other"


def normalize_relation(rel: str) -> str:
    rel_clean = rel.lower().replace(" ", "_").strip()
    if rel_clean in BASE_RELATIONS:
        return rel_clean
    return "relates_to"  
    
def safe_split(entity):
    """
    Safely splits 'name:type' into (name, type).
    Handles None, empty strings, and malformed input.
    """
    if entity is None:
        return "UNKNOWN", "other"

    if not isinstance(entity, str):
        return str(entity), "other"

    entity = entity.strip()
    if not entity:
        return "UNKNOWN", "other"

    parts = entity.rsplit(":", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    else:
        return parts[0], "other"


def validate_triple(triple):
    """
    Normalizes a candidate triple.
    Returns a dictionary with defined fields.
    Unknowns are mapped to 'other' or 'relates_to'.
    """
    e1, rel, e2, sector = triple

    # split name/type
    e1_name, e1_type = safe_split(e1)
    e2_name, e2_type = safe_split(e2)

    # normalize entity types (generic)
    e1_type = normalize_entity_type(e1_type)
    e2_type = normalize_entity_type(e2_type)

    # apply country normalization 
    e1_name, e1_type = normalize_countries(e1_name, e1_type)
    e2_name, e2_type = normalize_countries(e2_name, e2_type)

    # normalize relation and sector
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
