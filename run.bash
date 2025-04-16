#!/bin/bash

AIUS_DB="./aius.db"
AUTHOR_AGREEMENT_WORKBOOK="./author_agreement.xlsx"

./aius init --db $AIUS_DB
./aius search --db $AIUS_DB --journal nature
./aius search --db $AIUS_DB --journal plos
./aius search --db $AIUS_DB --journal science
./aius extract-documents --db $AIUS_DB
./aius openalex --db $AIUS_DB --email $1
./aius filter --db $AIUS_DB
./aius author-agreement --db $AIUS_DB --workbook $AUTHOR_AGREEMENT_WORKBOOK
