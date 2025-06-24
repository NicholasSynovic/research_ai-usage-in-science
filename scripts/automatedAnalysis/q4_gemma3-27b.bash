#!/bin/bash

$(OLLAMA_DEBUG="1" ollama serve 2>&1 | tee q3_gemma3-27b_ollama.log) &

find $(dirname "$0")/pdfs -name "*.pdf" -exec python automatedAnalysis.py -i {} -m "gemma3:27b" -p "For each pre-trained model, how was it reused: Conceptual Reuse: reimplementing and training model architectures based on original publications; Adaptation Reuse: fine-tuning downloaded models on domain-specific data; and Deployment Reuse: modifying models for integration within diverse computing environments" -t 600 --prediction-tokens 2000 --context-tokens 124000 >> q3_gemma3-27b.txt \;
