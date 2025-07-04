import argparse
import asyncio

from bird_id_assistant.assistant import chat
from bird_id_assistant.db import create_vector_db, query_vector_db
from bird_id_assistant.data_collection import collect_data
from bird_id_assistant.util import dir_path


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd")

    # Command for running Bird ID Assistant
    subparsers.add_parser(name="run", help="Start conversation with Bird ID Assistant")

    # Command for collecting articles
    parser_collect = subparsers.add_parser(
        name="collect",
        help="Collect dataset of Wikipedia articles about bird species"
    )
    parser_collect.add_argument(
        "output_dir",
        metavar="output-dir",
        type=dir_path,
        help="Path to output directory where collected articles are written"
    )
    parser_collect.add_argument(
        "--output-format",
        type=str,
        choices=["html", "txt"],
        default="txt",
        help="Output file format: html (raw) or txt (cleaned plain text) (default: %(default)s)"
    )
    parser_collect.add_argument(
        "--num-threads",
        type=int,
        default=8,
        help="Number of threads used for making requests (default: %(default)s)"
    )

    # Commands for creating/querying chroma db
    parser_db = subparsers.add_parser(
        name="db",
        help="Commands for interacting with the chroma vector database"
    )
    parser_db.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="ChromaDB client host URL (default: %(default)s)"
    )
    parser_db.add_argument("--port", type=int, default=8000, help="ChromaDB client port (default: %(default)s)")

    subparsers_db = parser_db.add_subparsers(dest="db_cmd")
    parser_db_create = subparsers_db.add_parser("create", help="Create vector database from text files in input dir")
    parser_db_create.add_argument(
        "input_doc_dir",
        type=dir_path,
        help="Directory containing text documents to store in vector database (default: %(default)s)"
    )
    parser_db_create.add_argument(
        "--collection-name",
        type=str,
        default="bia_data",
        help="Name of the collection where documents are inserted"
    )

    parser_db_query = subparsers_db.add_parser("query", help="Query documents from vector database")
    parser_db_query.add_argument("query", type=str, help="Query string")
    parser_db_query.add_argument(
        "-n", "--n_results",
        type=int,
        default=1,
        help="Number of closest matching documents to retrieve"
    )
    parser_db_query.add_argument(
        "--collection-name",
        type=str,
        default="bia_data",
        help="Name of the collection where documents are queried from (default: %(default)s)"
    )

    args = parser.parse_args()
    return args


def main(argv=None):
    args = parse_args(argv)
    kwargs = {k: v for k, v in vars(args).items() if "cmd" not in k}
    match args.cmd:
        case "run":
            asyncio.run(chat())
        case "collect":
            collect_data(**kwargs)
        case "db":
            match args.db_cmd:
                case "create":
                    create_vector_db(**kwargs)
                case "query":
                    print(query_vector_db(**kwargs)["documents"][0][0])
        case _:
            raise ValueError("Unknown command")


if __name__ == "__main__":
    main()
