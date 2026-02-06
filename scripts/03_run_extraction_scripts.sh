#!/bin/bash

python 03_llm_extract.py \
  --in-path ../data/ARTICLES_gfmag_sustainable.csv \
  --out-path ../data/TRIPLETS_gfmag_sustainable.csv \
# > logs/sustainable.log 2>&1

python 03_llm_extract.py \
  --in-path ../data/ARTICLES_gfmag_trans.csv \
  --out-path ../data/TRIPLETS_gfmag_trans.csv \
#  > logs/trans.log 2>&1

python 03_llm_extract.py \
  --in-path ../data/ARTICLES_gfmag_tech.csv \
  --out-path ../data/TRIPLETS_gfmag_tech.csv \
#  > logs/tech.log 2>&1

python 03_llm_extract.py \
  --in-path ../data/ARTICLES_gfmag_cap.csv \
  --out-path ../data/TRIPLETS_gfmag_cap.csv \
#  > logs/cap.log 2>&1

python 03_llm_extract.py \
  --in-path ../data/ARTICLES_gfmag_econ.csv \
  --out-path ../data/TRIPLETS_gfmag_econ.csv \
#  > logs/econ.log 2>&1

python 03_llm_extract.py \
  --in-path ../data/ARTICLES_gfmag_emerging.csv \
  --out-path ../data/TRIPLETS_gfmag_emerging.csv \
#  > logs/emerging.log 2>&1

python 03_llm_extract.py \
  --in-path ../data/ARTICLES_gfmag_banking.csv \
  --out-path ../data/TRIPLETS_gfmag_banking.csv \
#  > logs/banking.log 2>&1

python 03_llm_extract.py \
  --in-path ../data/ARTICLES_gfmag_insure.csv \
  --out-path ../data/TRIPLETS_gfmag_insure.csv \
#  > logs/insure.log 2>&1

python 03_llm_extract.py \
  --in-path ../data/ARTICLES_gfmag_cred.csv \
  --out-path ../data/TRIPLETS_gfmag_cred.csv \
#  > logs/insure.log 2>&1