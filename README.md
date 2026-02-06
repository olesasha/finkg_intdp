# Discovering Investment Potential With Knowledge Graphs

This repository contains a pipeline for creating and analyzing financial knowledge graphs. 
The data sourced used is Global Finance Magazine (https://gfmag.com/).
Parts of the projects are inspired and supported by prior research, in particularn FinDKG, and the LLM associated with it, ICKG [1].

## Usage
1. `run_urls_scraping.sh` extracts urls from https://gfmag.com.
2. `run_text_scraping.sh` scrapes the article texts from the urls.
3. `run_extraction_scripts.sh` performs LLM-based triplet extraction from the articles' texts.
4. `run_loadneo4j_scripts.sh` loads the resulting triplets to the Neo4J database. 


## References 
[1] Li, X. V., & Sanna Passino, F. (2024). FinDKG: Dynamic Knowledge Graphs with Large Language Models for Detecting Global Trends in Financial Markets. In Proceedings of the 5th ACM International Conference on AI in Finance (pp. 573–581). ACM. ICAIF ’24: 5th ACM International Conference on AI in Finance. https://doi.org/10.1145/3677052.3698603