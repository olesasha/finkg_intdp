import csv
from pathlib import Path
import sys
csv.field_size_limit(sys.maxsize)

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
from tqdm import tqdm

MODEL_NAME = "victorlxh/ICKG-v3.2"

BASE_RELATIONS = [
    "acquisition",
    "relates_to",
    "invests_in",
    "fine",
    "lawsuit",
    "partnership",
    "has_positive_impact",
    "has_negative_impact",
    "controls",
    "has_exposure",
    "is_competitor_of",
    "is_member_of",
    "other",
]

ENTITY_TYPES = [
    "person",
    "company",
    "country",
    "regulator",
    "event",
    "product",
    "financial_institution",
    "financial_instrument",
    "economic_indicator",
    "sector",
    "other",
]

_device = "cuda" if torch.cuda.is_available() else "cpu"
_pipe = None


def get_pipeline():
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
    pipe = get_pipeline()
    out = pipe(
        prompt,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        pad_token_id=pipe.tokenizer.eos_token_id,
    )
    return out[0]["generated_text"][len(prompt):]


def build_prompt(article_text: str, max_chars: int = 1200) -> str:
    if len(article_text) > max_chars:
        article_text = article_text[:max_chars] + "..."
    
    prompt = (
        "You are a business knowledge graph construction model. I will provide a news article labeled INPUT.\n"
        "Your task is to extract triplets of the form [head:type, relation, tail:type, sector].\n"
        f"Entities must be one of: {ENTITY_TYPES}. Relationships must be one of: {BASE_RELATIONS}.\n"
        "First, summarize the document briefly. Then extract main triplets. Find the best suitable entity and relation types out of the allowed. Avoid redundant ones, simplify to most general form (e.g. 'foreign trade tariffs' and 'international import tariffs' become 'import tariffs').\n"
        "Return ONLY valid JSON: a flat array of 4-element arrays like this:\n"
        '[["Apple Inc.:company", "acquisition", "Beats Electronics:company", "Technology"],\n'
        ' ["Google:company", "partnership", "OpenAI:company", "AI"]]\n'
        "Format: [exact_entity_name:type, relation, exact_entity_name:type, sector]\n"
        "Use exact names from text. Sector from context or null.\n"
        f"INPUT:\n{article_text}\n\nJSON:\n"
    )
    return prompt


def process_csv_to_txt(
    csv_path: str,
    output_txt_path: str,
    text_col: str = "Text",
    date_col: str = "Date",
    url_col: str = "Url",
    max_new_tokens: int = 256,
):
    output_path = Path(output_txt_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(csv_path, newline="", encoding="utf-8") as f_in, \
         open(output_path, "w", encoding="utf-8") as f_out:

        rows = list(csv.DictReader(f_in))

        for idx, row in enumerate(tqdm(rows, desc="Processing articles")):
            article_text = (row.get(text_col) or "").strip()
            if not article_text:
                continue

            date_val = row.get(date_col, "")
            url_val = row.get(url_col, "")

            prompt = build_prompt(article_text)
            raw = generate(prompt, max_new_tokens=max_new_tokens)

            # Dump everything as-is, plus simple header for traceability
            f_out.write(f"=== ARTICLE {idx} ===\n")
            f_out.write(f"DATE: {date_val}\n")
            f_out.write(f"URL: {url_val}\n")
            f_out.write("TRIPLETS_RAW:\n")
            f_out.write(raw.strip())
            f_out.write("\n\n")  # blank line between articles


if __name__ == "__main__":
    process_csv_to_txt(
        csv_path="../data/SCRAPED_gfmag_banking_1000_urls.csv",
        output_txt_path="../data/banking_kg_triplets_1000_raw.txt",
        text_col="Text",
        date_col="Date",
        url_col="Url",
        max_new_tokens=256,
    )
