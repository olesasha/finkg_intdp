#!/bin/bash

python llm_extraction.py \
  --in-path ../data/SCRAPED_gfmag_sustainable_1000_urls.csv \
  --out-path ../data/gfmag_sustainable_triplets.csv \
  > logs/sustainable.log 2>&1

python llm_extraction.py \
  --in-path ../data/SCRAPED_gfmag_trans_1000_urls.csv \
  --out-path ../data/gfmag_trans_triplets.csv \
  > logs/trans.log 2>&1

python llm_extraction.py \
  --in-path ../data/SCRAPED_gfmag_tech_1000_urls.csv \
  --out-path ../data/gfmag_tech_triplets.csv \
  > logs/tech.log 2>&1

python llm_extraction.py \
  --in-path ../data/SCRAPED_gfmag_cap_1000_urls.csv \
  --out-path ../data/gfmag_cap_triplets.csv \
  > logs/cap.log 2>&1

python llm_extraction.py \
  --in-path ../data/SCRAPED_gfmag_econ_1000_urls.csv \
  --out-path ../data/gfmag_econ_triplets.csv \
  > logs/econ.log 2>&1

python llm_extraction.py \
  --in-path ../data/SCRAPED_gfmag_emerging_1000_urls.csv \
  --out-path ../data/gfmag_emerging_triplets.csv \
  > logs/emerging.log 2>&1

python llm_extraction.py \
  --in-path ../data/SCRAPED_gfmag_banking_1000_urls.csv \
  --out-path ../data/gfmag_banking_triplets.csv \
  > logs/banking.log 2>&1
