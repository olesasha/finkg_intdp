import os
import dotenv
from neo4j import GraphDatabase
import pandas as pd
import argparse
from tqdm import tqdm

def extract_from_neo4j(env_file: str, output_file: str):
    # load Neo4j credentials from .env
    dotenv.load_dotenv(env_file)
    URI = os.getenv("NEO4J_URI")
    USER = os.getenv("NEO4J_USERNAME")
    PWD = os.getenv("NEO4J_PASSWORD")

    driver = GraphDatabase.driver(URI, auth=(USER, PWD))

    query = """
    MATCH (e1)-[r]->(e2)
    RETURN 
        labels(e1)[0] AS entity1_type,
        e1.name AS entity1,
        labels(e2)[0] AS entity2_type,
        e2.name AS entity2,
        type(r) AS rel_type,
        r.sector AS sector
    """

    with driver.session() as session:
        result = session.run(query)
        # use tqdm to show progress while converting to list
        data = [record.data() for record in tqdm(result, desc="Extracting relationships")]

    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"Extracted {len(df)} relationships to {output_file}")

    driver.close()


def main():
    parser = argparse.ArgumentParser(description="Extract triplets from Neo4j to CSV")
    parser.add_argument("--env", required=True, help="Path to .env file with Neo4j credentials")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()

    extract_from_neo4j(args.env, args.output)


if __name__ == "__main__":
    main()