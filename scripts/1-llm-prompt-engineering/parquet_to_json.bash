#!/bin/bash

DATA_DIR="../../data/large_prompt_engineering"

for fp in $(ls $DATA_DIR | grep uses_dl.parquet); do
    python parquet_to_json.py \
        --input-fp "${DATA_DIR}/${fp}" \
        --model uses_dl
done

for fp in $(ls $DATA_DIR | grep uses_ptms.parquet); do
    python parquet_to_json.py \
        --input-fp "${DATA_DIR}/${fp}" \
        --model uses_ptms
done

for fp in $(ls $DATA_DIR | grep identify_ptms.parquet); do
    python parquet_to_json.py \
        --input-fp "${DATA_DIR}/${fp}" \
        --model identify_ptms
done

for fp in $(ls $DATA_DIR | grep identify_reuse.parquet); do
    python parquet_to_json.py \
        --input-fp "${DATA_DIR}/${fp}" \
        --model identify_reuse
done
