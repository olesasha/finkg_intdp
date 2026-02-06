#!/bin/bash

python 01_gfmag_collect_urls.py \
  --category-path /category/economics-policy-regulation \
  --out-csv ../data/gfmag_econ_articles.csv \
  --max-articles 10000 \

python 01_gfmag_collect_urls.py \
  --category-path /category/transaction-banking \
  --out-csv ../data/gfmag_trans_articles.csv \
  --max-articles 10000 \

python 01_gfmag_collect_urls.py \
  --category-path /category/capital-raising-corporate-finance \
  --out-csv ../data/gfmag_cap_articles.csv \
  --max-articles 10000 \

python 01_gfmag_collect_urls.py \
  --category-path /category/emerging-frontier-markets \
  --out-csv ../data/gfmag_emerging_articles.csv \
  --max-articles 10000 \

python 01_gfmag_collect_urls.py \
  --category-path /category/sustainable-finance \
  --out-csv ../data/gfmag_sustainable_articles.csv \
  --max-articles 10000 \

python 01_gfmag_collect_urls.py \
  --category-path /category/banking \
  --out-csv ../data/gfmag_banking_articles.csv \
  --max-articles 10000 \

python 01_gfmag_collect_urls.py \
  --category-path /category/technology \
  --out-csv ../data/gfmag_tech_articles.csv \
  --max-articles 10000 \

python 01_gfmag_collect_urls.py \
  --category-path /category/private-credit \
  --out-csv ../data/gfmag_cred_articles.csv \
  --max-articles 10000 \

python 01_gfmag_collect_urls.py \
  --category-path /category/insurance \
  --out-csv ../data/gfmag_insure_articles.csv \
  --max-articles 10000 \
