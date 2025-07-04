import argparse
import asyncio

from bird_id_assistant.assistant import chat


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd")

    subparsers.add_parser(name="run", help="Start conversation with Bird ID Assistant")
    args = parser.parse_args()
    return args


def main(argv=None):
    args = parse_args(argv)
    match args.cmd:
        case "run":
            asyncio.run(chat())
        case _:
            raise ValueError("Unknown command")


if __name__ == "__main__":
    main()
