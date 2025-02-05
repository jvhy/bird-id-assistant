import argparse
import concurrent.futures
import logging
import os
import uuid

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

from bird_id_assistant.util import dir_path


logger = logging.getLogger(__name__)
logging.basicConfig(filename='logs/data_collection.log', encoding='utf-8', level=logging.DEBUG)

BASE_URL = "https://en.wikipedia.org"
BIRD_LIST_URL = BASE_URL + "/wiki/List_of_birds_by_common_name"


def download_content(url, timeout):
    try:
        response = requests.get(url, timeout=timeout)
    except Exception as exc:
        logger.error("Error requesting content from %s: %s", url, exc)
        return
    return response.content


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", metavar="output-dir", type=dir_path, help="Path to output directory where HTML pages are written")
    parser.add_argument("--num-threads", type=int, default=8, help="Number of threads used for making requests")
    args = parser.parse_args()
    return args


def main(argv=None):
    args = parse_args(argv)

    response = requests.get(BIRD_LIST_URL)
    html = response.content
    soup = BeautifulSoup(html)

    # Species list elements are structured as follows:
    # <div class="div-col">
    #   <ul>
    #     <li>
    #       <a href="/wiki/species_name">Species name</a>
    #     </li>
    #   </ul>
    # </div>

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
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.num_threads) as executor:
            future_to_url = (executor.submit(download_content, url, 10) for url in species_urls)
            for future in concurrent.futures.as_completed(future_to_url):
                data = future.result()
                results.append(data)
                progress_bar.update(1)

    for result in tqdm(results):
        if result:
            filename = uuid.uuid4().hex + ".html"  # creates a unique filename
            out_path = os.path.join(args.output_dir, filename)
            with open(out_path, "w") as f_out:
                f_out.write(result.decode())


if __name__ == "__main__":
    main()
