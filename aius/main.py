"""
Main entry point into AIUS.

Copyright 2025 (C) Nicholas M. Synovic

"""

from aius.cli import CLI
from argparse import Namespace
import sys


def main() -> None:
    cli: CLI = CLI()

    arguments: Namespace = cli.parse_cli()
    subparser_keyword: str = cli.get_subparser_keyword(args=arguments)
    argument_dictionary: dict = arguments.__dict__

    print(arguments)
    print(argument_dictionary["init.db"])
    quit(0)

    match subparser_keyword:
        case "init":
            initialize(
                fp=argument_dictionary["init.db"][0],
                force=argument_dictionary["init.force"],
            )
        case "search":
            search(
                fp=argument_dictionary["search.db"][0],
                journal=argument_dictionary["search.journal"][0],
            )
        case "ed":
            extractDocuments(fp=argument_dictionary["ed.db"][0])
        case "oa":
            getOpenAlexMetadata(
                fp=argument_dictionary["oa.db"][0],
                email=argument_dictionary["oa.email"][0],
            )
        case "filter":
            filterDocuments(fp=argument_dictionary["filter.db"][0])
        case "aa":
            addAuthorAgreement(
                dbFP=argument_dictionary["aa.db"][0],
                aaFP=argument_dictionary["aa.wb"][0],
            )
        case "stat":
            stats(dbFP=argument_dictionary["stat.db"][0], outputDir=Path("."))
        case "download":
            if (
                download(
                    dbFP=argument_dictionary["download.db"][0],
                    sample=argument_dictionary["download.sample"][0],
                    outputDir=argument_dictionary["download.output"][0],
                )
                == 0
            ):
                sys.exit(1)

        case _:
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
