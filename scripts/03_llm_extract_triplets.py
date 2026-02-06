import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2" #only warnings and errors, no startup logs 

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

# customs ____
from helpers.parsers import validate_triple, extract_candidate_triples
from helpers.ontology import ENTITY_TYPES, BASE_RELATIONS, ALLOWED_SECTORS
#_____________

MODEL_NAME = "victorlxh/ICKG-v3.2"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
_pipe = None

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
        print(f"Loading {MODEL_NAME} on {DEVICE}...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        if DEVICE == "cuda":
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

def main(in_path, out_path, limit=None):
    master_rows = []

    with open(in_path, newline="", encoding="utf-8", errors="replace") as f_in:
        articles = list(csv.DictReader(f_in))

    if limit:
        articles = articles[:limit]

    print(f"Reading {len(articles)} articles from {in_path}")

    for article in tqdm(articles, desc="Processing articles"):
        text = (article.get("Text") or "").strip()
        if not text:
            continue

        date, url = article.get("Date", ""), article.get("Url", "")
        prompt = build_prompt(text)
        raw_output = generate(prompt)
        candidate_triples = extract_candidate_triples(raw_output)

        # Normalize and validate
        for triple in candidate_triples:
            # Keep originals for analysis
            original_sector = triple[3]  
            original_rel = triple[1] 
            original_e1 = triple[0]  
            original_e2 = triple[2]  
            normalized = validate_triple(triple)
            if normalized:
                normalized["url"] = url
                normalized["date"] = date
                normalized["original_rel"] = original_rel
                normalized["original_sector"] = original_sector
                normalized["original_e1"] = original_e1  
                normalized["original_e2"] = original_e2  
                master_rows.append(normalized)

    df = pd.DataFrame(master_rows)
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} triples to {out_path}")

            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract KG triples from articles using ICKG LLM")
    parser.add_argument("--in-path", required=True, help="Path to input CSV containing articles")
    parser.add_argument("--out-path", required=True, help="Path to output CSV for extracted triples")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit on number of articles")
    args = parser.parse_args()
    main(args.in_path, args.out_path, args.limit)
    
#python llm_extraction.py --in-path ../data/SCRAPED_gfmag_banking_1000_urls.csv --out-path ../data/gfmag_banking_triplets.csv --limit 10