import pandas as pd
import torch
from pykeen.pipeline import pipeline
from pykeen.triples import TriplesFactory
from pykeen.evaluation import RankBasedEvaluator
import argparse
import json
from datetime import datetime

def create_tf(df):
    tf = TriplesFactory.from_labeled_triples(
        df.values,
        create_inverse_triples=True,
    )

    train_tf, val_tf, test_tf = tf.split(
        ratios=(0.8, 0.1, 0.1),
        random_state=11,
    )

    print("Dataset Stats:")
    print("Entities:", train_tf.num_entities)
    print("Relations (incl. inverse):", train_tf.num_relations)
    print("Train triples:", train_tf.num_triples)
    print("Validation triples:", val_tf.num_triples)
    print("Test triples:", test_tf.num_triples)

    return train_tf, val_tf, test_tf


def train_complex(train, val, test):

    result = pipeline(
        training=train,
        validation=val,
        testing=test,
        model="ComplEx",
        model_kwargs=dict(
            embedding_dim=128,
        ),
        training_kwargs=dict(
            num_epochs=150,
            batch_size=1024,
        ),
        optimizer="adam",
        optimizer_kwargs=dict(
            lr=1e-3,
        ),
        negative_sampler="basic",
        negative_sampler_kwargs=dict(
            num_negs_per_pos=25,
        ),
        evaluator_kwargs=dict(filtered=True),
        random_seed=11,
    )

    return result


def extract_metrics(result):

    metrics = result.metric_results.to_dict()

    realistic = metrics["both"]["realistic"]

    return {
        "MRR": realistic["inverse_harmonic_mean_rank"],
        "Hits@1": realistic["hits_at_1"],
        "Hits@3": realistic["hits_at_3"],
        "Hits@10": realistic["hits_at_10"],
        "Median Rank": realistic["median_rank"],
    }


def evaluate_target_relations(result, train_tf, test_tf):

    target_relations = ["invests_in", "acquires"]

    target_relation_ids = [
        train_tf.relation_to_id[r]
        for r in target_relations
        if r in train_tf.relation_to_id
    ]

    evaluator = RankBasedEvaluator(filtered=True)

    target_metrics = evaluator.evaluate(
        model=result.model,
        mapped_triples=test_tf.mapped_triples,
        additional_filter_triples=[train_tf.mapped_triples],
        restrict_relations=target_relation_ids,
    )

    realistic = target_metrics.to_dict()["both"]["realistic"]

    return {
        "MRR": realistic["inverse_harmonic_mean_rank"],
        "Hits@1": realistic["hits_at_1"],
        "Hits@3": realistic["hits_at_3"],
        "Hits@10": realistic["hits_at_10"],
        "Median Rank": realistic["median_rank"],
    }



def main():
    parser = argparse.ArgumentParser(description="Train ComplEx")
    parser.add_argument("--input", required=True, help="Path to triples CSV file")
    parser.add_argument("--output", required=True, help="Path to log JSON file")
    args = parser.parse_args()

    # Load data
    df = pd.read_csv(args.input)
    df = df[["entity1", "rel_type", "entity2"]]
    df = df.drop_duplicates(ignore_index=True)

    # create TF
    train_tf, val_tf, test_tf = create_tf(df)

    # train
    result = train_complex(train_tf, val_tf, test_tf)

    global_metrics = extract_metrics(result)

    # Extract invests/acquires metrics
    target_metrics = evaluate_target_relations(
        result, train_tf, test_tf
    )

    # print meaningful results
    print("\n=== Global Metrics ===")
    for k, v in global_metrics.items():
        print(f"{k}: {v:.6f}")

    print("\n=== invests_in / acquires Metrics ===")
    for k, v in target_metrics.items():
        print(f"{k}: {v:.6f}")

    # save log
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "num_entities": train_tf.num_entities,
        "num_relations": train_tf.num_relations,
        "train_triples": train_tf.num_triples,
        "global_metrics": global_metrics,
        "target_metrics": target_metrics,
    }

    with open(args.output, "w") as f:
        json.dump(log_data, f, indent=4)


if __name__ == "__main__":
    main()