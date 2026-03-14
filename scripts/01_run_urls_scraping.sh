#!/bin/bash

python 01_gfmag_collect_urls.py \
  --category-path /category/economics-policy-regulation \
  --out-csv ../data/ARTICLES_gfmag_econ.csv \
  --max-articles 10000 \

python 01_gfmag_collect_urls.py \
  --category-path /category/transaction-banking \
  --out-csv ../data/ARTICLES_gfmag_trans.csv \
  --max-articles 10000 \

python 01_gfmag_collect_urls.py \
  --category-path /category/capital-raising-corporate-finance \
  --out-csv ../data/ARTICLES_gfmag_cap.csv \
  --max-articles 10000 \

python 01_gfmag_collect_urls.py \
  --category-path /category/emerging-frontier-markets \
  --out-csv ../data/ARTICLES_gfmag_emerging.csv \
  --max-articles 10000 \

python 01_gfmag_collect_urls.py \
  --category-path /category/sustainable-finance \
  --out-csv ../data/ARTICLES_gfmag_sustainable.csv \
  --max-articles 10000 \

python 01_gfmag_collect_urls.py \
  --category-path /category/banking \
  --out-csv ../data/ARTICLES_gfmag_banking.csv \
  --max-articles 10000 \

python 01_gfmag_collect_urls.py \
  --category-path /category/technology \
  --out-csv ../data/ARTICLES_gfmag_tech.csv \
  --max-articles 10000 \

python 01_gfmag_collect_urls.py \
  --category-path /category/private-credit \
  --out-csv ../data/ARTICLES_gfmag_cred.csv \
  --max-articles 10000 \

python 01_gfmag_collect_urls.py \
  --category-path /category/insurance \
  --out-csv ../data/ARTICLES_gfmag_insure.csv \
  --max-articles 10000 \

python 01_yahoo_collect_urls.py
  
python helpers/deduplicate_urls.py \