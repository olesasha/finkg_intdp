#!/bin/bash

python 02_gfmag_get_text.py \
  --in-csv ../data/gfmag_econ_articles.csv \
  --out-csv ../data/gfmag_econ_articles.csv \
  
python 02_gfmag_get_text.py \
  --in-csv ../data/gfmag_trans_articles.csv \
  --out-csv ../data/gfmag_trans_articles.csv \

python 02_gfmag_get_text.py \
  --in-csv ../data/gfmag_cap_articles.csv \
  --out-csv ../data/gfmag_cap_articles.csv \

python 02_gfmag_get_text.py \
  --in-csv ../data/gfmag_emerging_articles.csv \
  --out-csv ../data/gfmag_emerging_articles.csv \

python 02_gfmag_get_text.py \
  --in-csv ../data/gfmag_sustainable_articles..csv \
  --out-csv ../data/gfmag_sustainable_articles.csv \

python 02_gfmag_get_text.py \
  --in-csv ../data/gfmag_banking_articles.csv \
  --out-csv ../data/gfmag_banking_articles.csv \

python 02_gfmag_get_text.py \
  --in-csv ../data/gfmag_tech_articles.csv \
  --out-csv ../data/gfmag_tech_articles.csv \

python 02_gfmag_get_text.py \
  --in-csv ../data/gfmag_cred_articles.csv \
  --out-csv ../data/gfmag_cred_articles.csv \

python 02_gfmag_get_text.py \
  --in-csv ../data/gfmag_insure_articles.csv \
  --out-csv ../data/gfmag_insure_articles.csv \
  