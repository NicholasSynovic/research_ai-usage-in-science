#!/bin/bash

# Get your access token
access_token=$(python alcf_inference_token.py get_access_token)

while true
    do
        # Get status of specific batch
        batch_id="72ab6925-4a0a-4eab-86f9-28065b66afd7"
        curl -X GET "https://inference-api.alcf.anl.gov/resource_server/v1/batches/${batch_id}/result" \
            -H "Authorization: Bearer ${access_token}"
        sleep 10
    done
