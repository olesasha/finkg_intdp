from pathlib import Path
import pandas as pd

DATA_DIR = Path("../data")
OUTPUT_CSV = DATA_DIR / "ARTICLES_ALL.csv"
URL_COLUMN = "Url"


def main():
    files = sorted(DATA_DIR.glob("ARTICLES_*.csv"))

    if not files:
        raise RuntimeError("No ARTICLES_*.csv files found")

    df = pd.concat(
        (pd.read_csv(f) for f in files),
        ignore_index=True
    )

    df = df.drop_duplicates(subset=URL_COLUMN)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)

    print(f"Merged {len(files)} files → {len(df)} unique articles")
    print(f"Output: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
