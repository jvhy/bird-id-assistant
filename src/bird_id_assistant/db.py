import argparse
import os

import chromadb
from chromadb import QueryResult
from tqdm import tqdm

from bird_id_assistant.util import dir_path


def create_vector_db(input_doc_dir: str, host="localhost", port=8000, collection_name="bia_data"):
    client = chromadb.HttpClient(host=host, port=port)
    collection = client.get_or_create_collection(collection_name)
    for fn in tqdm(os.listdir(input_doc_dir)):
        doc_path = os.path.join(input_doc_dir, fn)
        with open(doc_path, "r") as f:
            doc = f.read()
        collection.upsert(
            documents=[doc],
            ids=[fn.split(".")[0]]
        )


def query_vector_db(
        query: str,
        n_results: int,
        host="localhost",
        port=8000,
        collection_name="bia_data"
) -> list[QueryResult]:
    client = chromadb.HttpClient(host=host, port=port)
    collection = client.get_or_create_collection(collection_name)
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results


def get_documents(results: list[QueryResult]):
    return results["documents"][0]


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="localhost", help="ChromaDB client host URL")
    parser.add_argument("--port", type=int, default=8000, help="ChromaDB client port")
    subparsers = parser.add_subparsers(dest="cmd")

    parser_create = subparsers.add_parser("create", help="Create vector database from text files in input dir")
    parser_create.add_argument(
        "input_doc_dir",
        type=dir_path,
        help="Directory containing text documents to store in vector database"
    )

    parser_query = subparsers.add_parser("query", help="Query documents from vector database")
    parser_query.add_argument("query", type=str, help="Query string")
    parser_query.add_argument(
        "-n", "--n_results",
        type=int,
        default=1,
        help="Number of closest matching documents to retrieve"
    )

    args = parser.parse_args()
    return args


def main(argv=None):
    args = parse_args(argv)
    kwargs = {k: v for k, v in vars(args).items() if k != "cmd"}
    match args.cmd:
        case "create":
            create_vector_db(**kwargs)
        case "query":
            print([doc[:100] for doc in query_vector_db(**kwargs)["documents"][0]])
        case _:
            raise ValueError("Unknown command")


if __name__ == "__main__":
    main()
