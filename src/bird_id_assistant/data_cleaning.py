import argparse
import glob
import logging
import os

from bs4 import BeautifulSoup
import html2text
from tqdm import tqdm

from bird_id_assistant.util import dir_path


logger = logging.getLogger(__name__)


def extract_main_content(html):
    soup = BeautifulSoup(html, "html.parser")
    main_content = soup.find("div", class_="mw-content-ltr")

    if main_content is None:
        logger.warning("Failed to extract main content from HTML")
        return main_content

    # Remove invisible short description (always "Species of bird")
    short_desc_div = main_content.find("div", class_="shortdescription")
    if short_desc_div:
        short_desc_div.clear()

    # Remove "[edit]" links
    edit_spans = main_content.find_all("span", class_="mw-editsection")
    if edit_spans:
        for span in edit_spans:
            span.clear()

    # Remove inline reference superscripts, e.g. "[1]"
    reference_sups = main_content.find_all("sup", class_="reference")
    if reference_sups:
        for sup in reference_sups:
            sup.clear()

    # Remove references section and all elements following it
    references_header = main_content.find("h2", {"id": "References"})
    if references_header:
        references_div = references_header.parent
        for elem in references_div.find_next_siblings():
            elem.clear()
        references_div.clear()

    return str(main_content)


def clean(html):
    cleaner = html2text.HTML2Text()
    cleaner.ignore_links = True
    cleaner.ignore_emphasis = True
    cleaner.ignore_images = True
    cleaned_text = cleaner.handle(html).strip()
    return cleaned_text


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_dir",
        metavar="input-dir",
        type=dir_path,
        help="Directory containing html files to be cleaned. Files should have .html-extension."
    )
    parser.add_argument(
        "output_dir",
        metavar="output-dir",
        type=dir_path,
        help="Directory where cleaned .txt files are written"
    )
    args = parser.parse_args()
    return args


def main(argv=None):
    args = parse_args(argv)
    in_paths = glob.glob(args.input + "/*.html")
    for in_path in tqdm(in_paths):
        with open(in_path, "r") as f_in:
            html = f_in.read()
        content = extract_main_content(html)
        if content is None:
            continue
        cleaned_content = clean(content)
        out_fn = in_path.rsplit("/")[-1].rsplit(".")[0] + ".txt"
        out_path = os.path.join(args.output, out_fn)
        with open(out_path, "w") as f_out:
            f_out.write(cleaned_content)


if __name__ == "__main__":
    main()
