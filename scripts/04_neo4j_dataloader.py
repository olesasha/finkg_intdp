#!/usr/bin/env python3
import os
import dotenv
from neo4j import GraphDatabase
import pandas as pd
import argparse
from tqdm import tqdm

def load_to_neo4j(csv_file, env_file: str, batch_size: int = 1000):
    df = pd.read_csv(csv_file)
    df["sector"] = df["sector"].str.lower()
    df = df.dropna(subset=["entity1", "entity2"])
    # load Aura credentials
    dotenv.load_dotenv(env_file)
    URI = os.getenv("NEO4J_URI")
    USER = os.getenv("NEO4J_USERNAME")
    PWD = os.getenv("NEO4J_PASSWORD")

    driver = GraphDatabase.driver(URI, auth=(USER, PWD))

    # batch insert function
    def batch_insert(tx, batch):
        for row in batch:
            rel_type = row['rel_type'].replace('`', '')  # sanitize
            entity1_type = row['entity1_type'].replace('`', '')
            entity2_type = row['entity2_type'].replace('`', '')
            
            query = f"""
            MERGE (e1:`{entity1_type}` {{name: $e1_name}})
            MERGE (e2:`{entity2_type}` {{name: $e2_name}})
            MERGE (e1)-[r:`{rel_type}` {{sector: $sector}}]->(e2)
            SET r.history = coalesce(r.history, []) + [$url + "|" + $date]
            """
            tx.run(query,
                   e1_name=row['entity1'],
                   e2_name=row['entity2'],
                   sector=row['sector'],
                   url=row['url'],
                   date=str(row['date'])  # ensure string
                   )

    # main session loop
    with driver.session() as session:
        batch = []
        for _, row in tqdm(df.iterrows(), total=len(df), desc="Adding triplets"):
            batch.append({
                'entity1': row['entity1'],
                'entity1_type': row['entity1_type'],
                'entity2': row['entity2'],
                'entity2_type': row['entity2_type'],
                'rel_type': row['rel_type'],
                'sector': row['sector'],
                'url': row['url'],
                'date': row['date'],
            })
            if len(batch) == batch_size:
                session.execute_write(batch_insert, batch)
                batch = []
        if batch:
            session.execute_write(batch_insert, batch)

    driver.close()
    print("Graph data loaded to Neo4j successfully.")


def main():
    parser = argparse.ArgumentParser(description="Upload triplets CSV to Neo4j Aura")
    parser.add_argument("--csv", required=True, help="Path to triplets CSV file")
    parser.add_argument("--env", required=True, help="Path to .env file with Neo4j credentials")
    parser.add_argument("--batch-size", type=int, default=1000, help="Number of rows per batch")
    args = parser.parse_args()

    load_to_neo4j(args.csv, args.env, args.batch_size)

if __name__ == "__main__":
    main()

#python neo4j_dataloader.py --csv ../data/gfmag_sustainable_triplets.csv --env ../Neo4j_private.txt --batch-size 1000
