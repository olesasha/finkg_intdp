# Exploring Financial Knowledge Graphs from Open-Source News

This repository contains a pipeline for building and analyzing a financial knowledge graph from financial news articles.

The core workflow is:

1. collect article URLs
2. scrape article text
3. extract structured triplets with an LLM
4. interact with Neo4j
5. run downstream analysis and modeling experiments

The project is inspired in part by prior work on **FinDKG** and uses the **ICKG LLM** as a starting point for financial knowledge graph construction.

## PROJECT GOAL

The goal of this project is to transform unstructured financial news into a structured knowledge graph that can be queried, visualized, and used for downstream tasks such as:

- graph analytics
- link prediction
- entity relationship exploration
- investment-related signal discovery

The repository currently supports:

- collecting article URLs from finance news sources
- scraping article text and metadata
- extracting entity-relation triplets from articles
- interacting with Neo4j
- experimenting with downstream graph models

## REPOSITORY STRUCTURE

Current repository layout:

```
.
├── README.md
├── requirements.txt
├── .gitignore
├── Neo4j_public.txt
├── queries.md
└── scripts/

scripts/
├── 01_run_urls_scraping.sh
├── 02_run_text_scraping.sh
├── 03_run_extraction_scripts.sh
├── 04_run_loadneo4j_scripts.sh
├── 01_gfmag_collect_urls.py
├── 02_get_text.py
├── 03_llm_extract_triplets.py
├── 04_neo4j_dataextractor.py
├── 05_neo4jData_to_PyG.py
├── 06_complex.py
├── helpers/
├── archive/
└── logs/
```


## SETUP

1. Clone the repository

git clone https://github.com/olesasha/finkg_intdp.git
cd finkg_intdp

2. Create a virtual environment

python -m venv .venv
source .venv/bin/activate


3. Install dependencies

pip install --upgrade pip
pip install -r requirements.txt


4. Create required directories

Some scripts expect these directories:

mkdir -p data
mkdir -p scripts/logs


## NEO4J CONFIGURATION

Neo4j credentials should NOT be committed.

Create Neo4j_private.txt with the same structure as Neo4j_public.txt

The Neo4j scripts reference the private file when connecting to the database.


## PIPELINE OVERVIEW

The pipeline contains following stages:

1. URL collection
2. text scraping
3. triplet extraction
4. Neo4j interaction
5. Model training and evaluation.

Each stage is executed via shell scripts.

### Step 1 — collect articles URLs

Run: ```bash 01_run_urls_scraping.sh from scripts/```
Output files are written to data/

### Step 2 - scrape article text

Run: ```bash 02_run_text_scraping.sh```
Output files are written to data/ with prefix "ARTICLES_", previous files are overwritten. 

### Step 3 - LLM triplet extraction

Run: ```bash 03_run_extraction.sh```
Output files are written to data/ with prefix "TRIPLETS_". 

Extraction relies on:

- a predefined ontology (ontology.py in helpers/)
- parser helpers (parsers.py in helpers/)
- an LLM extraction model inspired by the ICKG approach

### Step 4 — Neo4j data upload

Run: ```bash 04_run_loadneo4j.sh```
Inputs: Neo4j_private.txt <- make sure your credentials are correct here. 

### Step 5 — Train and evaluate ComplEx
Run: ```bash 05_train_complex.sh```

The results of the evaluation are saved in logs/
### Step 6 - Train and evaluate RGCN 
Run: ```bash 05_train_gcnn.sh```
The results of the evaluation are saved in logs/

## MAIN SCRIPTS

- 01_gfmag_collect_urls.py  
- 01_yahoo_collect_urls.py  

Collects article URLs from Global Finance Magazine and Yahoo respectively. 

- 02_get_text.py  
Scrapes article text from URLs.

- 03_llm_extract_triplets.py  
Extracts knowledge graph triplets using an LLM.

- 04_neo4j_dataextractor.py  
Exports graph data from Neo4j.

- 05_neo4j_dataloader.py
- 05_neo4j_dataextractor.py (only needed for extracting inferred relations from Neo4J, does not influence the pipeline)

- 05_train_complex.py  
Runs a ComplEx knowledge graph embedding experiment.

- 06_train_gcnn.py  
Runs a RGCNN model.

## REFERENCES

Li, X. V., Passino, F. S.  
FinDKG: Dynamic Knowledge Graphs with Large Language Models for Detecting Global Trends in Financial Markets.  
ACM International Conference on AI in Finance, 2024.

## LICENSE

This repository is intended for research and experimentation, not commercial use.