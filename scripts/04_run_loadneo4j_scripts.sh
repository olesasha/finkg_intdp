#!/bin/bash

python 04_neo4j_dataloader.py \
    --csv ../data/TRIPLETS_final.csv \
    --env ../Neo4j_private.txt \
    --batch-size 1000 