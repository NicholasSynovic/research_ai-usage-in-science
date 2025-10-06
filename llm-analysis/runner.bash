#!/bin/bash

MODELS="granite3.3:8b phi3:14b gemma3:27b gpt-oss:20b magistral:24b deepseek-r1:70b llama4:16x17b"

for MODEL in $MODELS; do
    SAFE_NAME=$(echo "$MODEL" | tr ':' '_')
    echo "=== Running all question scripts for model: $MODEL ==="

    for i in {0..3}; do
        SCRIPT="question_${i}.py"
        OUTPUT="${SAFE_NAME}_question_${i}_code.parquet"

        echo "→ Running $SCRIPT with model $MODEL"
        python "$SCRIPT" -m "$MODEL" -i ../data/prompt_testing_dataset.parquet -o "$OUTPUT"
    done

    echo
done
