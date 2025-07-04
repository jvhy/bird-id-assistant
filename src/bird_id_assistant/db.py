import os

import chromadb
from chromadb import QueryResult
from tqdm import tqdm


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
