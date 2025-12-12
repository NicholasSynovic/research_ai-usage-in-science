#!/bin/bash
# Throttled PBS job submission script
# Submits jobs for multiple models and index values (0–19)
# Keeps at most 10 jobs in the queue/running at once

MAX_JOBS=10
USER_ID="nsynovic"
POLL_INTERVAL=30  # seconds
PBS_SCRIPT="llm_paper_uses_ptms_analysis.pbs"

# Models to process
MODELS=(
  "gpt-oss:20b"
#   "magistral:24b"
#   "phi3:14b"
)

# Index range (0–19 inclusive)
INDICES=$(seq 0 19)

# Main submission loop
for MODEL in "${MODELS[@]}"; do
    for INDEX in $INDICES; do
        # Throttle logic
        while true; do
            CURRENT_JOBS=$(qstat | grep "$USER_ID" | wc -l)
            if (( CURRENT_JOBS < MAX_JOBS )); then
                echo "[$(date)] Submitting: qsub -v AIUS_MODEL=\"$MODEL\",AIUS_INDEX=$INDEX $PBS_SCRIPT"
                qsub -v AIUS_MODEL="$MODEL",AIUS_INDEX=$INDEX "$PBS_SCRIPT"
                break
            else
                echo "[$(date)] $CURRENT_JOBS jobs active. Waiting for slots..."
                sleep "$POLL_INTERVAL"
            fi
        done
    done
done

echo "[$(date)] ✅ All jobs submitted successfully."
