import pandas as pd
import torch

def load_graph_gcnn(csv_path, add_inverse=True):
    """
    Load the graph and adds inverse relationships for GCNN training. 
    """
    df = pd.read_csv(csv_path)
    df = df[
        ["entity1", "entity1_type",
         "rel_type",
         "entity2", "entity2_type",
         "sector"]
    ].dropna().drop_duplicates(ignore_index=True)

    df["sector"] = df["sector"].str.lower()

    # Entities
    entities = pd.concat([df["entity1"], df["entity2"]]).unique()
    entity2id = {e: i for i, e in enumerate(entities)}
    num_nodes = len(entity2id)

    df["h"] = df["entity1"].map(entity2id)
    df["t"] = df["entity2"].map(entity2id)

    # Entity Types 
    type_df = pd.concat([
        df[["entity1", "entity1_type"]].rename(
            columns={"entity1": "entity", "entity1_type": "type"}
        ),
        df[["entity2", "entity2_type"]].rename(
            columns={"entity2": "entity", "entity2_type": "type"}
        )
    ]).drop_duplicates()

    types = type_df["type"].unique()
    type2id = {t: i for i, t in enumerate(types)}
    num_types = len(type2id)

    entity_type_id = torch.zeros(num_nodes, dtype=torch.long)
    for _, row in type_df.iterrows():
        entity_type_id[entity2id[row["entity"]]] = type2id[row["type"]]

    # Relations
    relations = df["rel_type"].unique()
    relation2id = {r: i for i, r in enumerate(relations)}
    df["r"] = df["rel_type"].map(relation2id)
    num_relations = len(relation2id)

    # Sectors
    sectors = df["sector"].unique()
    sector2id = {s: i for i, s in enumerate(sectors)}
    df["s"] = df["sector"].map(sector2id)
    num_sectors = len(sector2id)

    # Edge tensors
    edge_index = torch.tensor(df[["h", "t"]].values.T, dtype=torch.long)
    edge_type = torch.tensor(df["r"].values, dtype=torch.long)
    edge_sector = torch.tensor(df["s"].values, dtype=torch.long)

    if add_inverse:
        inv_edge_index = edge_index.flip(0)
        inv_edge_type = edge_type + num_relations
        inv_edge_sector = edge_sector

        edge_index = torch.cat([edge_index, inv_edge_index], dim=1)
        edge_type = torch.cat([edge_type, inv_edge_type])
        edge_sector = torch.cat([edge_sector, inv_edge_sector])

        num_relations *= 2

    return {
        "edge_index": edge_index,
        "edge_type": edge_type,
        "edge_sector": edge_sector,
        "entity_type_id": entity_type_id,
        "num_nodes": num_nodes,
        "num_relations": num_relations,
        "num_sectors": num_sectors,
        "num_types": num_types,
        "df":df
    }