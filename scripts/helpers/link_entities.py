import pandas as pd
from refined.inference.processor import Refined
from tqdm import tqdm

YAHOO_CSV = "../data/TRIPLETS_yahoo.csv"
GFMAG_CSV = "../data/TRIPLETS_ALL_gfmag.csv"
OUTPUT_CSV = "../data/TRIPLETS_final_linked.csv"

ENTITY_COLS = ["entity1", "entity2"]


print("Reading triplet files...")
yahoo = pd.read_csv(YAHOO_CSV)
gfmag = pd.read_csv(GFMAG_CSV)

df = pd.concat([yahoo, gfmag], ignore_index=True)

df = df.dropna()

print(f"Merged rows: {len(df)}")

unique_entities = pd.unique(df[ENTITY_COLS].values.ravel())

print(f"{len(unique_entities)} unique entities to link")

print("Loading ReFinED...")
refined = Refined.from_pretrained(
    model_name="wikipedia_model_with_numbers",
    entity_set="wikipedia"
)

entity_map = {}

for ent in tqdm(unique_entities, desc="Linking entities"):
    try:
        spans = refined.process_text(ent)

        if spans and spans[0].predicted_entity is not None:
            entity_map[ent] = spans[0].predicted_entity.wikipedia_entity_title
        else:
            entity_map[ent] = ent

    except Exception:
        entity_map[ent] = ent


for col in ENTITY_COLS:
    df[col] = df[col].map(entity_map)


df.to_csv(OUTPUT_CSV, index=False)

print(f"Saved linked triplets to {OUTPUT_CSV}")
