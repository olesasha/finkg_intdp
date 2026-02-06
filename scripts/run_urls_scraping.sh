#!/bin/bash

python 01_gfmag_collect_urls.py \
  --category-path /category/economics-policy-regulation \ 
  --out-csv gfmag_econ_urls.csv \
  --max-articles 10000

python 01_gfmag_collect_urls.py \
  --category-path /category/transaction-banking \ 
  --out-csv gfmag_trans_urls.csv \
  --max-articles 10000

python 01_gfmag_collect_urls.py \
  --category-path /category/capital-raising-corporate-finance \ 
  --out-csv gfmag_cap_urls.csv \
  --max-articles 10000

python 01_gfmag_collect_urls.py \
  --category-path /category/emerging-frontier-markets \ 
  --out-csv gfmag_emerging_urls.csv \
  --max-articles 10000

python 01_gfmag_collect_urls.py \
  --category-path /category/sustainable-finance \ 
  --out-csv gfmag_sustainable_urls.csv \
  --max-articles 10000

python 01_gfmag_collect_urls.py \
  --category-path /category/banking \ 
  --out-csv gfmag_banking_urls.csv \
  --max-articles 10000

python 01_gfmag_collect_urls.py \
  --category-path /category/technology \ 
  --out-csv gfmag_tech_urls.csv \
  --max-articles 10000

python 01_gfmag_collect_urls.py \
  --category-path /category/private-credit \ 
  --out-csv gfmag_cred_urls.csv \
  --max-articles 10000

python 01_gfmag_collect_urls.py \
  --category-path /category/insurance \ 
  --out-csv gfmag_insure_urls.csv \
  --max-articles 10000
