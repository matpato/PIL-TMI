#!/bin/bash
########################################################
## Shell Script to Execute all Process of the KB dataset 
########################################################
set -e

python3 calculate_similarity.py

python3 calculate_structural_similarity.py

python3 normalize_similarities.py 

python3 create_kbds.py