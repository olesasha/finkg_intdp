#!/bin/bash

python 04_neo4j_dataloader.py \
    --csv ../data/TRIPLETS_neo4j.csv \
    --env ../Neo4j_private.txt \
    --batch-size 10000
