#!/bin/bash

#!/bin/bash

source optparse.bash
optparse.define short=d long=database desc="The database to output and read data from" variable=AIUS_DB default=aius.db
optparse.define short=a long=author-agreement desc="The author agreement Excel workbook file" variable=AUTHOR_AGREEMENT_WORKBOOK default=author_agreement.xlsx
optparse.define short=e long=email desc="Email to access OpenAlex polite pool" variable=EMAIL
source $( optparse.build )

./aius init --db $AIUS_DB
./aius search --db $AIUS_DB --journal nature
./aius search --db $AIUS_DB --journal plos
./aius search --db $AIUS_DB --journal science
./aius extract-documents --db $AIUS_DB
./aius openalex --db $AIUS_DB --email $EMAIL
./aius filter --db $AIUS_DB
./aius author-agreement --db $AIUS_DB --workbook $AUTHOR_AGREEMENT_WORKBOOK
