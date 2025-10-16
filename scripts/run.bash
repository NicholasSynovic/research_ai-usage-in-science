CURRENT_DATE=$(date +"%m-%d-%Y")
DB="aius_${CURRENT_DATE}.sqlite3"


aius load-llm-prompts --db $DB
aius search-plos --db $DB
aius identify-documents --db $DB

aius load-pilot-study \
    --db $DB \
    --input-fp ../data/pilot_study.csv

aius load-author-agreement \
    --db $DB \
    --input-fp ../data/author_agreement.csv

aius load-llm-prompt-engineering-papers --db $DB

aius openalex \
    --db $DB \
    --email $1

aius filter-documents --db $DB

nohup pandoc server 2>&1 &
aius retrieve-content \
    --db $DB \
    --input-fp ../data/all_of_plos.zip \
    --pandoc-url "http://localhost:3030"
pkill pandoc
