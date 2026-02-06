#!/bin/bash

python 01_gfmag_collect_urls.py \
  --category_path /category/economics-policy-regulation \
  --out_csv gfmag_econ_urls.csv \
  --max_articles 10000 \

python 01_gfmag_collect_urls.py \
  --category_path /category/transaction-banking \
  --out_csv gfmag_trans_urls.csv \
  --max_articles 10000 \

python 01_gfmag_collect_urls.py \
  --category_path /category/capital-raising-corporate-finance \
  --out_csv gfmag_cap_urls.csv \
  --max_articles 10000 \

python 01_gfmag_collect_urls.py \
  --category_path /category/emerging-frontier-markets \
  --out_csv gfmag_emerging_urls.csv \
  --max_articles 10000 \

python 01_gfmag_collect_urls.py \
  --category_path /category/sustainable-finance \
  --out_csv gfmag_sustainable_urls.csv \
  --max_articles 10000 \

python 01_gfmag_collect_urls.py \
  --category_path /category/banking \
  --out_csv gfmag_banking_urls.csv \
  --max_articles 10000 \

python 01_gfmag_collect_urls.py \
  --category_path /category/technology \
  --out_csv gfmag_tech_urls.csv \
  --max_articles 10000 \

python 01_gfmag_collect_urls.py \
  --category_path /category/private-credit \
  --out_csv gfmag_cred_urls.csv \
  --max_articles 10000 \

python 01_gfmag_collect_urls.py \
  --category_path /category/insurance \
  --out_csv gfmag_insure_urls.csv \
  --max_articles 10000 \
