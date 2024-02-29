#!/usr/bin/env python3
import argparse
import csv
import logging
import random
import textwrap
from pathlib import Path

from util.pylib import log


def main():
    log.started()
    args = parse_args()

    random.seed(args.seed)

    text_paths = {p.stem for p in args.text_dir.glob("*.txt")}
    openai_paths = {p.stem for p in args.openai_dir.glob("*.json")}
    traiter_paths = {p.stem for p in args.traiter_dir.glob("*.json")}
    reconciled_paths = {p.stem for p in args.reconciled_dir.glob("*.json")}

    paths = sorted(text_paths & openai_paths & traiter_paths & reconciled_paths)

    text = len(text_paths)
    reconciled = len(reconciled_paths)
    traiter = len(traiter_paths)
    openai = len(openai_paths)

    msg = (
        f"Text: {text}, "
        f"Reconciled: {reconciled}, "
        f"Traiter: {traiter}, "
        f"OpenAI: {openai}, "
        f"Intersection: {len(paths)}, "
    )
    logging.info(msg)

    sample = random.sample(paths, args.sample)

    with args.csv_file.open("w") as out:
        writer = csv.writer(out)
        writer.writerow(
            ["name", "ocr_text", "reconciled", "traiter_output", "gpt4_output"]
        )

        for stem in sample:
            path = args.text_dir / f"{stem}.txt"
            with path.open() as f:
                text = f.read()

            path = args.reconciled_dir / f"{stem}.json"
            with path.open() as f:
                reconciled = f.read()

            path = args.openai_dir / f"{stem}.json"
            with path.open() as f:
                openai = f.read()

            path = args.traiter_dir / f"{stem}.json"
            with path.open() as f:
                traiter = f.read()

            writer.writerow([stem, text, reconciled, traiter, openai])

    log.finished()


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@",
        description=textwrap.dedent(
            """Sample ChatGPT and Traiter results for comparison."""
        ),
    )

    arg_parser.add_argument(
        "--text-dir",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Directory containing the OCR result files.""",
    )

    arg_parser.add_argument(
        "--reconciled-dir",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Directory holding the reconciled output.""",
    )

    arg_parser.add_argument(
        "--openai-dir",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Directory holding the openai output.""",
    )

    arg_parser.add_argument(
        "--traiter-dir",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Get traiter JSON files from this directory.""",
    )

    arg_parser.add_argument(
        "--csv-file",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Output the data to this CSV file.""",
    )

    arg_parser.add_argument(
        "--sample",
        metavar="INT",
        type=int,
        default=200,
        help="""Number of paths to sample.""",
    )

    arg_parser.add_argument(
        "--seed",
        metavar="INT",
        type=int,
        default=4438,
        help="""Random number seed.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
