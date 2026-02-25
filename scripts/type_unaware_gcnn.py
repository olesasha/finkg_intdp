import pandas as pd
import torch
from torch_geometric.nn import RGCNConv
import torch.nn.functional as F
from helpers.dataloader import load_graph_gcnn
from helpers.eval import evaluate_per_relation, evaluate_tail_only, evaluate_per_relation_unaware, evaluate_tail_only_unaware
import torch.optim as optim
from collections import defaultdict
from tqdm import tqdm
import torch.nn as nn

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

df_path = "../data/TRIPLETS_final_linked.csv"
data = load_graph_gcnn(df_path, add_inverse=True)

edge_index = data["edge_index"]
edge_type = data["edge_type"]

num_nodes = data["num_nodes"]
num_relations = data["num_relations"]
num_types = data["num_types"]

df = data["df"]

triples = torch.tensor(
    df[["h", "r", "t"]].values,  # remove 's'
    dtype=torch.long
)

seed = 11
torch.manual_seed(seed)
torch.cuda.manual_seed(seed)

perm = torch.randperm(len(triples))
triples = triples[perm]

n = len(triples)
train_triples = triples[:int(0.8*n)]
val_triples   = triples[int(0.8*n):int(0.9*n)]
test_triples  = triples[int(0.9*n):]


class RGCNEncoder(torch.nn.Module):
    def __init__(self, num_nodes, num_relations, hidden_dim):
        super().__init__()

        self.emb = torch.nn.Embedding(num_nodes, hidden_dim)
        self.conv1 = RGCNConv(hidden_dim, hidden_dim, num_relations)
        self.conv2 = RGCNConv(hidden_dim, hidden_dim, num_relations)

    def forward(self, edge_index, edge_type):
        x = self.emb.weight
        x = self.conv1(x, edge_index, edge_type)
        x = F.relu(x)
        x = self.conv2(x, edge_index, edge_type)
        return x

class LinkPredictor(nn.Module):
    def __init__(self, num_relations, hidden_dim, num_sectors=None, num_types=None, type_aware=False):
        super().__init__()
        self.rel_emb = nn.Embedding(num_relations, hidden_dim)
        self.type_aware = type_aware
        if type_aware:
            self.sector_emb = nn.Embedding(num_sectors, hidden_dim)
            self.type_emb = nn.Embedding(num_types, hidden_dim)

    def score(self, node_repr, head, rel, tail, sector=None, entity_type_id=None):
        h = node_repr[head]
        t = node_repr[tail]
        r = self.rel_emb(rel)
        if self.type_aware:
            h = h + self.type_emb(entity_type_id[head])
            t = t + self.type_emb(entity_type_id[tail])
            r = r + self.sector_emb(sector)
        return torch.sum(h * r * t, dim=1)

class FullModel(nn.Module):
    def __init__(self, encoder, num_relations, hidden_dim):
        super().__init__()
        self.encoder = encoder
        self.predictor = LinkPredictor(num_relations, hidden_dim)

    def forward(self, edge_index, edge_type):
        return self.encoder(edge_index, edge_type)

def build_filter_dict(all_triples):
    d = defaultdict(list)
    for h, r, t in all_triples:  # no s anymore
        d[(int(h), int(r))].append(int(t))
    return d

# Training Step (Tail Corruption Only)

def train_epoch(model, edge_index, edge_type, train_triples, optimizer, num_nodes, device):
    model.train()
    total_loss = 0

    for batch in torch.split(train_triples, 1024):
        batch = batch.to(device)

        node_repr = model(edge_index, edge_type)

        h = batch[:, 0]
        r = batch[:, 1]
        t = batch[:, 2]

        pos_scores = model.predictor.score(node_repr, h, r, t)

        t_neg = torch.randint(0, num_nodes, t.size(), device=device)
        neg_scores = model.predictor.score(node_repr, h, r, t_neg)

        loss = torch.mean(
            F.softplus(-pos_scores) + F.softplus(neg_scores)
        )

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    return total_loss


# Full Training Loop

def run_training(model,
                 edge_index, edge_type,
                 train_triples,
                 val_triples,
                 test_triples,
                 num_nodes,
                 device,
                 epochs=50,
                 lr=1e-3):

    model.to(device)
    edge_index = edge_index.to(device)
    edge_type = edge_type.to(device)

    optimizer = optim.Adam(model.parameters(), lr=lr)

    # Build filter dict using ALL triples
    all_triples = torch.cat(
        [train_triples, val_triples, test_triples],
        dim=0
    )
    filter_dict = build_filter_dict(all_triples)

    for epoch in range(1, epochs + 1):

        loss = train_epoch(
            model,
            edge_index, edge_type,
            train_triples,
            optimizer,
            num_nodes,
            device
        )

        print(f"\nEpoch {epoch} | Loss: {loss:.4f}")

        if epoch % 5 == 0:

            print("Validation:")
            val_metrics = evaluate_tail_only_unaware(
                model,
                edge_index, edge_type,
                val_triples,
                filter_dict,
                num_nodes,
                device, 
                type_aware=False
            )
            print(val_metrics)

    print("\nFinal Test Evaluation:")
    test_metrics = evaluate_tail_only_unaware(
        model,
        edge_index, edge_type,
        test_triples,
        filter_dict,
        num_nodes,
        device,
        type_aware=False

    )

    print("\n=== Global Test Metrics ===")
    print(test_metrics)

    print("\n=== Per-Relation Test Metrics ===")
    per_rel = evaluate_per_relation_unaware(
        model,
        edge_index, edge_type,
        test_triples,
        filter_dict,
        num_nodes,
        device,
        type_aware=False

    )

    for rel_id, metrics in per_rel.items():
        print(f"\nRelation {rel_id}")
        print(metrics)

    return test_metrics, per_rel


# Config and run 
        
hidden_dim = 200

encoder = RGCNEncoder(num_nodes, num_relations, hidden_dim)

model = FullModel(encoder, num_relations, hidden_dim)

run_training(
    model,
    edge_index,
    edge_type,
    train_triples=train_triples,
    val_triples=val_triples,
    test_triples=test_triples,
    num_nodes=num_nodes,
    device=device,
    epochs=50,
    lr=1e-3
)
import pandas as pd
import torch
from torch_geometric.nn import RGCNConv
import torch.nn.functional as F
from helpers.dataloader import load_graph_gcnn
from helpers.eval import evaluate_per_relation, evaluate_tail_only, evaluate_per_relation_unaware, evaluate_tail_only_unaware
import torch.optim as optim
from collections import defaultdict
from tqdm import tqdm
import torch.nn as nn

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

df_path = "../data/TRIPLETS_final_linked.csv"
data = load_graph_gcnn(df_path, add_inverse=True)

edge_index = data["edge_index"]
edge_type = data["edge_type"]

num_nodes = data["num_nodes"]
num_relations = data["num_relations"]
num_types = data["num_types"]

df = data["df"]

triples = torch.tensor(
    df[["h", "r", "t"]].values,  # remove 's'
    dtype=torch.long
)

seed = 11
torch.manual_seed(seed)
torch.cuda.manual_seed(seed)

perm = torch.randperm(len(triples))
triples = triples[perm]

n = len(triples)
train_triples = triples[:int(0.8*n)]
val_triples   = triples[int(0.8*n):int(0.9*n)]
test_triples  = triples[int(0.9*n):]


class RGCNEncoder(torch.nn.Module):
    def __init__(self, num_nodes, num_relations, hidden_dim):
        super().__init__()

        self.emb = torch.nn.Embedding(num_nodes, hidden_dim)
        self.conv1 = RGCNConv(hidden_dim, hidden_dim, num_relations)
        self.conv2 = RGCNConv(hidden_dim, hidden_dim, num_relations)

    def forward(self, edge_index, edge_type):
        x = self.emb.weight
        x = self.conv1(x, edge_index, edge_type)
        x = F.relu(x)
        x = self.conv2(x, edge_index, edge_type)
        return x

class LinkPredictor(nn.Module):
    def __init__(self, num_relations, hidden_dim, num_sectors=None, num_types=None, type_aware=False):
        super().__init__()
        self.rel_emb = nn.Embedding(num_relations, hidden_dim)
        self.type_aware = type_aware
        if type_aware:
            self.sector_emb = nn.Embedding(num_sectors, hidden_dim)
            self.type_emb = nn.Embedding(num_types, hidden_dim)

    def score(self, node_repr, head, rel, tail, sector=None, entity_type_id=None):
        h = node_repr[head]
        t = node_repr[tail]
        r = self.rel_emb(rel)
        if self.type_aware:
            h = h + self.type_emb(entity_type_id[head])
            t = t + self.type_emb(entity_type_id[tail])
            r = r + self.sector_emb(sector)
        return torch.sum(h * r * t, dim=1)

class FullModel(nn.Module):
    def __init__(self, encoder, num_relations, hidden_dim):
        super().__init__()
        self.encoder = encoder
        self.predictor = LinkPredictor(num_relations, hidden_dim)

    def forward(self, edge_index, edge_type):
        return self.encoder(edge_index, edge_type)

def build_filter_dict(all_triples):
    d = defaultdict(list)
    for h, r, t in all_triples:  # no s anymore
        d[(int(h), int(r))].append(int(t))
    return d

# Training Step (Tail Corruption Only)

def train_epoch(model, edge_index, edge_type, train_triples, optimizer, num_nodes, device):
    model.train()
    total_loss = 0

    for batch in torch.split(train_triples, 1024):
        batch = batch.to(device)

        node_repr = model(edge_index, edge_type)

        h = batch[:, 0]
        r = batch[:, 1]
        t = batch[:, 2]

        pos_scores = model.predictor.score(node_repr, h, r, t)

        t_neg = torch.randint(0, num_nodes, t.size(), device=device)
        neg_scores = model.predictor.score(node_repr, h, r, t_neg)

        loss = torch.mean(
            F.softplus(-pos_scores) + F.softplus(neg_scores)
        )

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    return total_loss


# Full Training Loop

def run_training(model,
                 edge_index, edge_type,
                 train_triples,
                 val_triples,
                 test_triples,
                 num_nodes,
                 device,
                 epochs=50,
                 lr=1e-3):

    model.to(device)
    edge_index = edge_index.to(device)
    edge_type = edge_type.to(device)

    optimizer = optim.Adam(model.parameters(), lr=lr)

    # Build filter dict using ALL triples
    all_triples = torch.cat(
        [train_triples, val_triples, test_triples],
        dim=0
    )
    filter_dict = build_filter_dict(all_triples)

    for epoch in range(1, epochs + 1):

        loss = train_epoch(
            model,
            edge_index, edge_type,
            train_triples,
            optimizer,
            num_nodes,
            device
        )

        print(f"\nEpoch {epoch} | Loss: {loss:.4f}")

        if epoch % 5 == 0:

            print("Validation:")
            val_metrics = evaluate_tail_only_unaware(
                model,
                edge_index, edge_type,
                val_triples,
                filter_dict,
                num_nodes,
                device, 
                type_aware=False
            )
            print(val_metrics)

    print("\nFinal Test Evaluation:")
    test_metrics = evaluate_tail_only_unaware(
        model,
        edge_index, edge_type,
        test_triples,
        filter_dict,
        num_nodes,
        device,
        type_aware=False

    )

    print("\n=== Global Test Metrics ===")
    print(test_metrics)

    print("\n=== Per-Relation Test Metrics ===")
    per_rel = evaluate_per_relation_unaware(
        model,
        edge_index, edge_type,
        test_triples,
        filter_dict,
        num_nodes,
        device,
        type_aware=False

    )

    for rel_id, metrics in per_rel.items():
        print(f"\nRelation {rel_id}")
        print(metrics)

    return test_metrics, per_rel


# Config and run 
        
hidden_dim = 200

encoder = RGCNEncoder(num_nodes, num_relations, hidden_dim)

model = FullModel(encoder, num_relations, hidden_dim)

run_training(
    model,
    edge_index,
    edge_type,
    train_triples=train_triples,
    val_triples=val_triples,
    test_triples=test_triples,
    num_nodes=num_nodes,
    device=device,
    epochs=50,
    lr=1e-3
)
