seq 0 999 | parallel \
  --bar
  aius analyze \
    --auth-key $1   \
    --backend openai \
    --db $2 \
    --index {} \
    --model-name "gpt-5.4-nano-2026-03-17" \
    --stride 1000 \
    --system-prompt-id "uses_dl"
