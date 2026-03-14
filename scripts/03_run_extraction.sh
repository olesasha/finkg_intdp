#!/usr/bin/env bash
python 03_llm_extract_triplets.py \
  --in-path ../data/ARTICLES_yahoo.csv \
  --out-path ../data/TRIPLETS_yahoo.csv

python 03_llm_extract_triplets.py \
  --in-path ../data/ARTICLES_ALL.csv \
  --out-path ../data/TRIPLETS_ALL_gfmag.csv

python helpers/link_entities.py
