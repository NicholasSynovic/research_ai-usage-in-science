#!/bin/bash

# Available model options
MODELS="granite3.3:8b phi3:14b gemma3:27b gpt-oss:20b magistral:24b deepseek-r1:70b llama4:16x17b"

# Available prompt choices
PROMPTS="uses-dl uses-ptms identify-ptms usage-method"

# Input dataset
INPUT="../data/prompt_testing_dataset.parquet"

for MODEL in $MODELS; do
    SAFE_MODEL=$(echo "$MODEL" | tr ':' '_')

    for PROMPT in $PROMPTS; do
        OUTPUT="${SAFE_MODEL}_${PROMPT}_analysis.pkl"

        echo "=== Running analysis.py for model: $MODEL | prompt: $PROMPT ==="
        python analysis.py \
            -i "$INPUT" \
            -o "$OUTPUT" \
            -m "$MODEL" \
            -p "$PROMPT"
    done
done
