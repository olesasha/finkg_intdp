#!/usr/bin/env python3
import os
import dotenv
from neo4j import GraphDatabase
import pandas as pd
import argparse
from tqdm import tqdm

REL_TYPE_MAP = {
    "acquires": "ACQUIRES",
    "invests_in": "INVESTS_IN",
    "is_fined": "IS_FINED",
    "sues": "SUES",
    "partners_with": "PARTNERS_WITH",
    "controls": "CONTROLS",
    "has_exposure": "HAS_EXPOSURE",
    "is_competitor_of": "IS_COMPETITOR_OF",
    "is_member_of": "IS_MEMBER_OF",
    "supplies": "SUPPLIES",
    "has_positive_impact": "HAS_POSITIVE_IMPACT",
    "has_negative_impact": "HAS_NEGATIVE_IMPACT",
    "other": "OTHER"
}

def batch_insert(tx, batch):
    for row in batch:
        rel_label = REL_TYPE_MAP[row["rel_type"]]  # trusted input

        query = f"""
        MERGE (e1:Entity {{name: $e1_name}})
        ON CREATE SET e1.type = $e1_type
        MERGE (e2:Entity {{name: $e2_name}})
        ON CREATE SET e2.type = $e2_type
        MERGE (e1)-[r:{rel_label}]->(e2)
        SET r.sector = $sector,
            r.url = $url,
            r.date = $date
        """

        tx.run(
            query,
            e1_name=row["entity1"],
            e1_type=row["entity1_type"],
            e2_name=row["entity2"],
            e2_type=row["entity2_type"],
            sector=row["sector"],
            url=row["url"],
            date=str(row["date"]),
        )


def load_to_neo4j(csv_file, env_file: str, batch_size: int = 1000):
    df = pd.read_csv(csv_file)
    df["sector"] = df["sector"].str.lower()
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
            query = f"""
            MERGE (e1:Entity {{name: $e1_name, type: $e1_type}})
            MERGE (e2:Entity {{name: $e2_name, type: $e2_type}})
            MERGE (e1)-[r:`{rel_type}`]->(e2)
            SET r.sector = $sector,
                r.url = $url,
                r.date = $date
            """
            tx.run(query,
                   e1_name=row['entity1'],
                   e1_type=row['entity1_type'],
                   e2_name=row['entity2'],
                   e2_type=row['entity2_type'],
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

#python neo4j_dataloader.py --csv ../data/gfmag_sustainable_triplets.csv --env ../Neo4j-6b4d3211-Created-2026-01-22.txt --batch-size 1000
