import argparse
import asyncio

from bird_id_assistant.assistant import chat
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

    args = parser.parse_args()
    return args


def main(argv=None):
    args = parse_args(argv)
    kwargs = {k: v for k, v in vars(args).items() if k != "cmd"}
    match args.cmd:
        case "run":
            asyncio.run(chat())
        case "collect":
            collect_data(**kwargs)
        case _:
            raise ValueError("Unknown command")


if __name__ == "__main__":
    main()
