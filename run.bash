#!/bin/bash

#!/bin/bash

source optparse.bash
optparse.define short=d long=database desc="The database to output and read data from" variable=AIUS_DB default=aius.db
optparse.define short=a long=author-agreement desc="The author agreement Excel workbook file" variable=AUTHOR_AGREEMENT_WORKBOOK default=author_agreement.xlsx
optparse.define short=e long=email desc="Email to access OpenAlex polite pool" variable=EMAIL
source $( optparse.build )

# ./dist/aius init --db $AIUS_DB
# ./dist/aius search --db $AIUS_DB --journal nature
# ./dist/aius search --db $AIUS_DB --journal plos
# ./dist/aius search --db $AIUS_DB --journal science
# ./dist/aius extract-documents --db $AIUS_DB
# ./dist/aius openalex --db $AIUS_DB --email $EMAIL
# ./dist/aius filter --db $AIUS_DB
./dist/aius author-agreement --db $AIUS_DB --workbook $AUTHOR_AGREEMENT_WORKBOOK
