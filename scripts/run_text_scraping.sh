#!/bin/bash

python 02_gfmag_get_text.py \
  --in-csv gfmag_econ_urls.csv \
  --out-csv gfmag_econ_urls.csv \
  
python 02_gfmag_get_text.py \
  --in-csv gfmag_trans.csv \
  --out-csv gfmag_trans.csv \

python 02_gfmag_get_text.py \
  --in-csv gfmag_cap.csv \
  --out-csv gfmag_cap.csv \

python 02_gfmag_get_text.py \
  --in-csv gfmag_emerging.csv \
  --out-csv gfmag_emerging.csv \

python 02_gfmag_get_text.py \
  --in-csv gfmag_sustainable..csv \
  --out-csv gfmag_sustainable.csv \

python 02_gfmag_get_text.py \
  --in-csv gfmag_banking.csv \
  --out-csv gfmag_banking.csv \

python 02_gfmag_get_text.py \
  --in-csv gfmag_tech.csv \
  --out-csv gfmag_tech.csv \

python 02_gfmag_get_text.py \
  --in-csv gfmag_cred.csv \
  --out-csv gfmag_cred.csv \

python 02_gfmag_get_text.py \
  --in-csv gfmag_insure.csv \
  --out-csv gfmag_insure.csv \
  