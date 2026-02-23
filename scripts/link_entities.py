import pandas as pd
from refined.inference.processor import Refined
from tqdm import tqdm


INPUT_CSV = "../data/TRIPLETS_final.csv"   # input CSV path
OUTPUT_CSV = "../data/TRIPLETS_final_linked.csv"   # output CSV path
ENTITY_COLS = ["entity1", "entity2"]  # columns to link


df = pd.read_csv(INPUT_CSV)

unique_entities = pd.unique(df[ENTITY_COLS].values.ravel())


refined = Refined.from_pretrained(model_name='wikipedia_model_with_numbers',
                                  entity_set="wikipedia")

# Map original -> linked
entity_map = {}

for ent in tqdm(unique_entities, desc="Linking entities"):
    spans = refined.process_text(ent)
    if spans and spans[0].text is not None:
        # use the linked surface mention (span.text)
        entity_map[ent] = spans[0].text
    else:
        # keep original if no link found
        entity_map[ent] = ent

# Apply mapping to 
for col in ENTITY_COLS:
    df[col] = df[col].map(entity_map)

df.to_csv(OUTPUT_CSV, index=False)
print(f"Linked entities saved to {OUTPUT_CSV}")