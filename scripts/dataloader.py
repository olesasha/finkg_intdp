#!/usr/bin/env python3
import os
import dotenv
from neo4j import GraphDatabase
import pandas as pd
import argparse
from tqdm import tqdm

def batch_insert(tx, batch):
    for row in batch:
        query = """
        MERGE (e1:Entity {name: $e1_name})
        MERGE (e2:Entity {name: $e2_name})
        CREATE (e1)-[r:REL]->(e2)
        SET r.rel_type = $rel_type,
            r.sector = $sector,
            r.url = $url,
            r.date = $date,
            e1.type = $e1_type,
            e2.type = $e2_type
        """
        tx.run(
            query,
            e1_name=row["entity1"],
            e1_type=row["entity1_type"],
            e2_name=row["entity2"],
            e2_type=row["entity2_type"],
            rel_type=row["rel_type"],
            sector=row["sector"],
            url=row["url"],
            date=str(row["date"]),
        )


def load_to_neo4j(df: pd.DataFrame, env_file: str, batch_size: int = 1000):
    # Load credentials
    dotenv.load_dotenv(env_file)
    URI = os.getenv("NEO4J_URI")
    USER = os.getenv("NEO4J_USERNAME")
    PWD = os.getenv("NEO4J_PASSWORD")

    if not URI or not USER or not PWD:
        raise ValueError("Neo4j credentials not found in the env file!")

    driver = GraphDatabase.driver(URI, auth=(USER, PWD))

    # Drop rows with missing critical fields
    df = df.dropna(subset=['entity1','entity2','rel_type'])

    total_rows = len(df)
    print(f"Uploading {total_rows} triplets to Neo4j...")

    with driver.session() as session:
        batch = []
        pbar = tqdm(total=total_rows, desc="Uploading to Neo4j", unit="rows")

        for _, row in df.iterrows():
            batch.append({
                'entity1': row['entity1'],
                'entity1_type': row['entity1_type'],
                'entity2': row['entity2'],
                'entity2_type': row['entity2_type'],
                'rel_type': row['rel_type'],
                'sector': row['sector'],
                'url': row['url'],
                'date': str(row['date'])
            })
            if len(batch) == batch_size:
                session.execute_write(batch_insert, batch)
                pbar.update(len(batch))
                batch = []

        # Insert remaining rows
        if batch:
            session.execute_write(batch_insert, batch)
            pbar.update(len(batch))

        pbar.close()

    driver.close()
    print("Graph data loaded to Neo4j successfully.")

def main():
    parser = argparse.ArgumentParser(description="Upload triplets CSV to Neo4j Aura")
    parser.add_argument("--csv", required=True, help="Path to triplets CSV file")
    parser.add_argument("--env", required=True, help="Path to .env file with Neo4j credentials")
    parser.add_argument("--batch-size", type=int, default=1000, help="Number of rows per batch")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    if 'industry' in df.columns:
        df.rename(columns={"industry": "sector"}, inplace=True)

    load_to_neo4j(df, args.env, args.batch_size)

if __name__ == "__main__":
    main()

#python dataloader.py --csv ../data/gfmag_sustainable_triplets.csv --env ../Neo4j-6b4d3211-Created-2026-01-22.txt --batch-size 1000
