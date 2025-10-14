#!/bin/bash

# NOTE: Stide = 20, so:
# the minimum AIUS_INDEX == 1, and
# the maximum AIUS_INDEX == 19

# GPT-OSS (computes values in approximately 16 minutes)
qsub -v AIUS_MODEL="gpt-oss:20b",AIUS_INDEX=0 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="gpt-oss:20b",AIUS_INDEX=1 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="gpt-oss:20b",AIUS_INDEX=2 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="gpt-oss:20b",AIUS_INDEX=3 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="gpt-oss:20b",AIUS_INDEX=4 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="gpt-oss:20b",AIUS_INDEX=5 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="gpt-oss:20b",AIUS_INDEX=6 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="gpt-oss:20b",AIUS_INDEX=7 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="gpt-oss:20b",AIUS_INDEX=8 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="gpt-oss:20b",AIUS_INDEX=9 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="gpt-oss:20b",AIUS_INDEX=10 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="gpt-oss:20b",AIUS_INDEX=11 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="gpt-oss:20b",AIUS_INDEX=12 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="gpt-oss:20b",AIUS_INDEX=13 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="gpt-oss:20b",AIUS_INDEX=14 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="gpt-oss:20b",AIUS_INDEX=15 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="gpt-oss:20b",AIUS_INDEX=16 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="gpt-oss:20b",AIUS_INDEX=17 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="gpt-oss:20b",AIUS_INDEX=18 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="gpt-oss:20b",AIUS_INDEX=19 llm_paper_uses_dl_analysis.pbs

# Magistral
qsub -v AIUS_MODEL="magistral:24b",AIUS_INDEX=0 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="magistral:24b",AIUS_INDEX=1 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="magistral:24b",AIUS_INDEX=2 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="magistral:24b",AIUS_INDEX=3 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="magistral:24b",AIUS_INDEX=4 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="magistral:24b",AIUS_INDEX=5 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="magistral:24b",AIUS_INDEX=6 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="magistral:24b",AIUS_INDEX=7 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="magistral:24b",AIUS_INDEX=8 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="magistral:24b",AIUS_INDEX=9 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="magistral:24b",AIUS_INDEX=10 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="magistral:24b",AIUS_INDEX=11 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="magistral:24b",AIUS_INDEX=12 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="magistral:24b",AIUS_INDEX=13 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="magistral:24b",AIUS_INDEX=14 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="magistral:24b",AIUS_INDEX=15 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="magistral:24b",AIUS_INDEX=16 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="magistral:24b",AIUS_INDEX=17 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="magistral:24b",AIUS_INDEX=18 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="magistral:24b",AIUS_INDEX=19 llm_paper_uses_dl_analysis.pbs

# Phi 3
qsub -v AIUS_MODEL="phi3:14b",AIUS_INDEX=0 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="phi3:14b",AIUS_INDEX=1 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="phi3:14b",AIUS_INDEX=2 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="phi3:14b",AIUS_INDEX=3 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="phi3:14b",AIUS_INDEX=4 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="phi3:14b",AIUS_INDEX=5 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="phi3:14b",AIUS_INDEX=6 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="phi3:14b",AIUS_INDEX=7 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="phi3:14b",AIUS_INDEX=8 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="phi3:14b",AIUS_INDEX=9 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="phi3:14b",AIUS_INDEX=10 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="phi3:14b",AIUS_INDEX=11 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="phi3:14b",AIUS_INDEX=12 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="phi3:14b",AIUS_INDEX=13 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="phi3:14b",AIUS_INDEX=14 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="phi3:14b",AIUS_INDEX=15 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="phi3:14b",AIUS_INDEX=16 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="phi3:14b",AIUS_INDEX=17 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="phi3:14b",AIUS_INDEX=18 llm_paper_uses_dl_analysis.pbs
qsub -v AIUS_MODEL="phi3:14b",AIUS_INDEX=19 llm_paper_uses_dl_analysis.pbs
