#!/bin/bash

python dataloader.py \
    --csv ../data/gfmag_sustainable_triplets.csv \
    --env ../Neo4j-6b4d3211-Created-2026-01-22.txt \
    --batch-size 1000 \

python dataloader.py \
    --csv ../data/gfmag_banking_triplets.csv \
    --env ../Neo4j-6b4d3211-Created-2026-01-22.txt \
    --batch-size 1000 \

python dataloader.py \
    --csv ../data/gfmag_cap_triplets.csv \
    --env ../Neo4j-6b4d3211-Created-2026-01-22.txt \
    --batch-size 1000 \

python dataloader.py \
    --csv ../data/gfmag_econ_triplets.csv \
    --env ../Neo4j-6b4d3211-Created-2026-01-22.txt \
    --batch-size 1000 \

python dataloader.py \
    --csv ../data/gfmag_emerging_triplets.csv \
    --env ../Neo4j-6b4d3211-Created-2026-01-22.txt \
    --batch-size 1000 \

python dataloader.py \
    --csv ../data/gfmag_trans_triplets.csv \
    --env ../Neo4j-6b4d3211-Created-2026-01-22.txt \
    --batch-size 1000 \

python dataloader.py \
    --csv ../data/gfmag_tech_triplets.csv \
    --env ../Neo4j-6b4d3211-Created-2026-01-22.txt \
    --batch-size 1000 \
