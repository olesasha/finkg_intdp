import pandas as pd
import torch
from torch_geometric.nn import RGCNConv
import torch.nn.functional as F
import torch.optim as optim
from collections import defaultdict
from tqdm import tqdm

def evaluate_per_relation(model,
                          edge_index, edge_type,
                          triples,
                          entity_type_id,
                          filter_dict,
                          num_nodes,
                          device):

    results = {}
    rel_ids = triples[:, 1].unique()

    for rel in rel_ids:

        mask = triples[:, 1] == rel
        rel_triples = triples[mask]

        metrics = evaluate_tail_only(
            model,
            edge_index,
            edge_type,
            rel_triples,
            entity_type_id,
            filter_dict,
            num_nodes,
            device
        )

        metrics["support"] = len(rel_triples)
        results[int(rel)] = metrics

    return results

@torch.no_grad()
def evaluate_tail_only(model,
                       edge_index, edge_type,
                       triples,
                       entity_type_id,
                       filter_dict,
                       num_nodes,
                       device):

    model.eval()
    node_repr = model(edge_index, edge_type)

    mrr = hits1 = hits3 = hits10 = 0

    for triple in tqdm(triples, leave=False):

        h, r, t, s = triple.to(device)

        candidates = torch.arange(num_nodes, device=device)

        scores = model.predictor.score(
            node_repr,
            h.repeat(num_nodes),
            r.repeat(num_nodes),
            candidates,
            s.repeat(num_nodes),
            entity_type_id
        )

        # Filtering
        true_tails = filter_dict.get(
            (int(h), int(r), int(s)), []
        )

        for tail in true_tails:
            if tail != int(t):
                scores[tail] = -1e9

        rank = (scores > scores[t]).sum().item() + 1

        mrr += 1.0 / rank
        hits1 += rank <= 1
        hits3 += rank <= 3
        hits10 += rank <= 10

    n = len(triples)

    return {
        "MRR": mrr / n,
        "Hits@1": hits1 / n,
        "Hits@3": hits3 / n,
        "Hits@10": hits10 / n
    }


def evaluate_per_relation_unaware(
    model,
    edge_index,
    edge_type,
    triples,
    filter_dict,
    num_nodes,
    device,
    type_aware=False,
    entity_type_id=None,
    sectors=None,
):
    results = {}
    rel_ids = triples[:, 1].unique()

    for rel in rel_ids:
        mask = triples[:, 1] == rel
        rel_triples = triples[mask]

        metrics = evaluate_tail_only(
            model,
            edge_index,
            edge_type,
            rel_triples,
            filter_dict,
            num_nodes,
            device,
            type_aware=type_aware,
            entity_type_id=entity_type_id,
            sectors=sectors,
        )

        metrics["support"] = len(rel_triples)
        results[int(rel)] = metrics

    return results

@torch.no_grad()
def evaluate_tail_only_unaware(
    model,
    edge_index,
    edge_type,
    triples,
    filter_dict,
    num_nodes,
    device,
    type_aware=False,
    entity_type_id=None,
    sectors=None,
):
    """
    Evaluates tail prediction for a batch of triples.
    type_aware: if True, uses entity_type_id and sectors in scoring
    """

    model.eval()
    node_repr = model(edge_index, edge_type)

    mrr = hits1 = hits3 = hits10 = 0

    for triple in tqdm(triples, leave=False):
        triple = triple.to(device)

        if type_aware:
            h, r, t, s = triple
            s_val = s if sectors is None else sectors[s]
        else:
            h, r, t = triple
            s_val = None

        candidates = torch.arange(num_nodes, device=device)

        scores = model.predictor.score(
            node_repr,
            h.repeat(num_nodes),
            r.repeat(num_nodes),
            candidates,
            sector=s_val,
            entity_type_id=entity_type_id,
        )

        # Filtering
        key = (int(h), int(r), int(s_val)) if type_aware else (int(h), int(r))
        true_tails = filter_dict.get(key, [])

        for tail in true_tails:
            if tail != int(t):
                scores[tail] = -1e9

        rank = (scores > scores[t]).sum().item() + 1
        mrr += 1.0 / rank
        hits1 += rank <= 1
        hits3 += rank <= 3
        hits10 += rank <= 10

    n = len(triples)
    return {
        "MRR": mrr / n,
        "Hits@1": hits1 / n,
        "Hits@3": hits3 / n,
        "Hits@10": hits10 / n,
    }