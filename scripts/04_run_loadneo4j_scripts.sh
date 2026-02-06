#!/bin/bash

python 04_neo4j_dataloader.py \
    --csv ../data/  --out-path ../data/TRIPLETS_ALL.csv .csv \
    --env ../Neo4j_private.txt \
    --batch-size 1000 