import argparse
import pandas as pd
from refined.inference.processor import Refined
from tqdm import tqdm


def merge_triplets(yahoo_path, gfmag_path):
    yahoo = pd.read_csv(yahoo_path)
    gfmag = pd.read_csv(gfmag_path)

    merged = pd.concat([yahoo, gfmag], ignore_index=True)
    return merged


def load_refined():
    print("Loading ReFinED entity linker...")
    return Refined.from_pretrained(
        model_name="wikipedia_model_with_numbers",
        entity_set="wikipedia"
    )


def link_entity(refined, text):
    if pd.isna(text):
        return text

    try:
        spans = refined.process_text(str(text))
        if spans and spans[0].predicted_entity:
            return spans[0].predicted_entity.wikipedia_entity_title
    except Exception:
        pass

    return text


def run_entity_linking(df, refined):
    tqdm.pandas()

    df["entity1"] = df["entity1"].progress_apply(lambda x: link_entity(refined, x))
    df["entity2"] = df["entity2"].progress_apply(lambda x: link_entity(refined, x))

    return df


def main(yahoo_path, gfmag_path, out_path):

    print("Merging triplet files...")
    df = merge_triplets(yahoo_path, gfmag_path)

    print(f"Merged rows: {len(df)}")

    refined = load_refined()

    print("Running entity linking...")
    df = run_entity_linking(df, refined)

    df.to_csv(out_path, index=False)

    print(f"Saved final linked triples → {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--yahoo-path", required=True)
    parser.add_argument("--gfmag-path", required=True)
    parser.add_argument("--out-path", required=True)

    args = parser.parse_args()

    main(args.yahoo_path, args.gfmag_path, args.out_path)
