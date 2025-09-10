#!/bin/bash

echo "run 1"
python 1_do_the_authors_use_deep_learning.py --pdf ../data/pdf_preprocessing.parquet --model gemma3:27b --output gemma_q1 --ollama localhost:11435

echo "run 2"
python 2_are_pre-trained_deep_learning_models_used.py --pdf ../data/pdf_preprocessing.parquet --model gemma3:27b --output gemma_q2 --ollama localhost:11435

echo "run 3"
python 3_what_pre_trained_deep_learning_models_are_used.py --pdf ../data/pdf_preprocessing.parquet --model gemma3:27b --output gemma_q2 --ollama localhost:11435

echo "run 4"
python 4_what_pre_trained_deep_learning_model_reuse_method_was_used.py --pdf ../data/pdf_preprocessing.parquet --model gemma3:27b --output gemma_q2 --ollama localhost:11435
