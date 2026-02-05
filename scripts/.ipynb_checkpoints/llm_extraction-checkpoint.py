import pandas as pd
import re
import json
import sys
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
from tqdm import tqdm
import argparse
import ast 

import csv
csv.field_size_limit(sys.maxsize)

MODEL_NAME = "victorlxh/ICKG-v3.2"

BASE_RELATIONS = [
    "acquires",
    "invests_in",
    "is_fined",
    "sues",
    "partners_with",
    "controls",
    "has_exposure",
    "is_competitor_of",
    "is_member_of",
    "supplies",
    "has_positive_impact",
    "has_negative_impact",
    "other"
]

ENTITY_TYPES = [
    "person",
    "company",
    "financial_institution",  # Banks, insurers, funds (subset of companies but explicit)
    "financial_instrument",   # Bonds, derivatives, stocks, loans (distinct tradable assets)
    "country",
    "city_region",
    "regulator",
    "disaster_event",         # Wars, hurricanes, political conflicts, pandemics
    "product_service",        # iPhone, AWS, Boeing 737
    "economic_indicator",     # GDP, CPI, unemployment, interest rates
    "other"
]

ALLOWED_SECTORS = {
    "financials",
    "technology",
    "healthcare",
    "real estate",
    "industrials",
    "transportation",
    "energy",
    "consumer goods and services",
    "natural resources",
    "public sector",
    "other"
}

_device = "cuda" if torch.cuda.is_available() else "cpu"
_pipe = None

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

def build_prompt(article_text: str, max_chars: int = 1200) -> str:
    """
    Builds a prompt for the LLM. 
    """
    if len(article_text) > max_chars:
        article_text = article_text[:max_chars] + "..."
    
    prompt = (
        "You are a business knowledge graph construction model. I will provide a news article labeled INPUT.\n"
        "Your task is to extract triplets of the form [head:type, relation, tail:type, sector].\n"
        f"Entities must be one of: {ENTITY_TYPES}. Relationships must be one of: {BASE_RELATIONS}. Sectors must be one of: {ALLOWED_SECTORS}.\n"
        "First, summarize the document briefly. Then extract main triplets. Find the best suitable entity and relation types out of the allowed. Avoid redundant ones, simplify to most general form (e.g. 'foreign trade tariffs' and 'international import tariffs' become 'import tariffs').\n"
        "Return ONLY valid JSON: a flat array of 4-element arrays like this:\n"
        '[["Apple Inc.:company", "acquires", "Beats Electronics:company", "technology"],\n'
        ' ["Google:company", "partners_with", "OpenAI:company", "AI"]]\n'
        "Format: [exact_entity_name:type, relation, exact_entity_name:type, sector]\n"
        "Use exact names from text. Sector from context or null.\n"
        f"INPUT:\n{article_text}\n\nJSON:\n"
    )
    return prompt


def get_pipeline():
    """
    Defines LLM extraction pipeline.
    """
    global _pipe
    if _pipe is None:
        print(f"Loading {MODEL_NAME} on {_device}...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        if _device == "cuda":
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                dtype=torch.float16,
                device_map="auto",
            )
            _pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
        else:
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                dtype=torch.float16,
            )
            _pipe = pipeline(
                "text-generation", model=model, tokenizer=tokenizer, device=-1
            )
    return _pipe

def generate(prompt: str, max_new_tokens: int = 256) -> str:
    """
    Generator for the tokens. 
    """
    pipe = get_pipeline()
    out = pipe(
        prompt,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        pad_token_id=pipe.tokenizer.eos_token_id,
    )
    return out[0]["generated_text"][len(prompt):]

def main(in_path, out_path, limit):
    """
    Reads and processes scraped text with ICKG LLM. 
    Removes malformed and duplicate triplets.
    Writes triplets and metadata to a pandas dataframe. 
    """
    master_rows = []

    with open(in_path, newline="", encoding="utf-8", errors="replace") as f_in:
        articles = list(csv.DictReader(f_in))

    if limit:
        articles = articles[:limit]

    print(f"Reading {len(articles)} articles from {in_path}")

    for article in tqdm(articles, desc="Processing articles"):
        article_text = (article.get("Text") or "").strip()
        if not article_text:
            continue

        date = article.get("Date", "")
        url = article.get("Url", "")

        prompt = build_prompt(article_text)
        raw = generate(prompt)
        clean = extract_candidate_triples(raw)

        if not clean:
            continue

        # deduplicate + validate
        clean = list({tuple(t) for t in clean})
        clean = [
            t for t in clean
            if t[1] in BASE_RELATIONS
            and t[0].rsplit(":", 1)[-1] in ENTITY_TYPES
            and t[2].rsplit(":", 1)[-1] in ENTITY_TYPES
        ]

        for e1, rel, e2, industry in clean:
        
            # Safe unpack function
            def safe_split(entity):
                parts = entity.rsplit(":", 1)
                if len(parts) == 2:
                    return parts[0], parts[1]
                else:
                    # If no colon, use UNKNOWN as type
                    return parts[0], "UNKNOWN"
        
            e1_name, e1_type = safe_split(e1)
            e2_name, e2_type = safe_split(e2)
        
            master_rows.append({
                "entity1": e1_name,
                "entity1_type": e1_type,
                "rel_type": rel,
                "entity2": e2_name,
                "entity2_type": e2_type,
                "industry": industry,
                "url": url,
                "date": date
            })

    df = pd.DataFrame(master_rows)
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} triples to {out_path}")

            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract KG triples from articles using ICKG LLM"
    )

    parser.add_argument(
        "--in-path",
        required=True,
        help="Path to input csv containing articles"
    )

    parser.add_argument(
        "--out-path",
        required=True,
        help="Path to output csv for extracted triples"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional: limit number of articles"
    )

    args = parser.parse_args()
    main(args.in_path, args.out_path, args.limit)
    
#python llm_extraction.py --in-path ../data/SCRAPED_gfmag_banking_1000_urls.csv --out-path ../data/gfmag_banking_triplets.csv --limit 10