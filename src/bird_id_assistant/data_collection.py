from enum import Enum
import concurrent.futures
import logging
import os
import uuid

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

from bird_id_assistant.data_cleaning import extract_main_content, clean
from bird_id_assistant.util import dir_path


logger = logging.getLogger(__name__)
logging.basicConfig(filename='logs/data_collection.log', encoding='utf-8', level=logging.DEBUG)

BASE_URL = "https://en.wikipedia.org"
BIRD_LIST_URL = BASE_URL + "/wiki/List_of_birds_by_common_name"


class OutputFormat(str, Enum):
    TXT = "txt"
    HTML = "html"


def download_content(url, timeout):
    try:
        response = requests.get(url, timeout=timeout)
    except Exception as exc:
        logger.error("Error requesting content from %s: %s", url, exc)
        return
    return response.content


def collect_data(output_dir: str | os.PathLike, output_format: OutputFormat = "txt", num_threads: int = 8) -> None:
    """
    Collects Wikipedia articles of bird species, (optionally) cleans the HTML into plain text and writes the article contents to files.

    Args:
        output_dir:     Path to a directory where downloaded article files are saved.
        output_format:  Format of the article files (txt or html). If set to txt, downloaded HTML files are cleaned.
    """
    clean_output = (output_format == "txt")

    response = requests.get(BIRD_LIST_URL)
    html = response.content
    soup = BeautifulSoup(html, features="html.parser")

    # Species list elements are structured as follows:
    # <div class="div-col">
    #   <ul>
    #     <li>
    #       <a href="/wiki/species_name">Species name</a>
    #     </li>
    #   </ul>
    # </div>

    # flake8: noqa E131
    species_urls = [
        BASE_URL + a["href"]
            for div in soup.body.find_all("div", class_="div-col")
                for ul in div.find_all("ul")
                    for li in ul.find_all("li")
                        for a in li.find_all("a")
    ]

    # Make requests in parallel in n threads
    results = []
    with tqdm(total=len(species_urls)) as progress_bar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            future_to_url = (executor.submit(download_content, url, 10) for url in species_urls)
            for future in concurrent.futures.as_completed(future_to_url):
                data = future.result()
                results.append(data)
                progress_bar.update(1)

    for result in tqdm(results):
        if not result:
            continue
        if clean_output:
            content = extract_main_content(result)
            cleaned_content = clean(content)
            result = cleaned_content
        filename = uuid.uuid4().hex + "." + output_format  # creates a unique filename
        out_path = os.path.join(output_dir, filename)
        with open(out_path, "w") as f_out:
            f_out.write(result)
