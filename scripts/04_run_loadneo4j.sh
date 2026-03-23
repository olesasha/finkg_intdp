#!/bin/bash

python 04_neo4j_dataloader.py \
    --csv ../TRIPLETS_neo4j.csv \
    --env ../Neo4j_private.txt \
    --batch-size 10000
