import argparse
import os


def dir_path(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"writable_dir: {path} is not a valid path")
    if not os.access(path, os.W_OK):
        raise argparse.ArgumentTypeError(f"writable_dir: {path} is not writable")
    return path
