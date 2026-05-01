"""CLI — Dashboard Salários Tech."""

import argparse
import io
import logging
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"


def _parse():
    p = argparse.ArgumentParser(description="Tech Salaries Dashboard — Data Science Jobs")
    p.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    p.add_argument("--log-level", default="INFO",
                   choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return p.parse_args()


def main():
    args = _parse()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )

    from .ingest import carregar, resumo
    from .analysis import analisar
    from .report import imprimir

    df = carregar()
    resumo(df)

    resultado = analisar(df)
    imprimir(resultado, len(df), df["salary_in_usd"].median(), args.output_dir)


if __name__ == "__main__":
    main()
