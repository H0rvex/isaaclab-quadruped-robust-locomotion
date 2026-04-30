#!/usr/bin/env python3
"""Aggregate evaluation JSON files into portfolio summary tables."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_ROOT / "source"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from isaaclab_quadruped.utils.result_io import iter_json_files, read_json  # noqa: E402
from isaaclab_quadruped.utils.tables import (  # noqa: E402
    SUMMARY_COLUMNS,
    evaluation_json_to_row,
    rows_to_summary_frame,
    to_markdown_table,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    default_results_dir = Path.cwd() / "results"
    parser.add_argument(
        "--eval-dir",
        type=Path,
        default=default_results_dir / "eval",
        help="Directory containing evaluation JSON files.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=default_results_dir / "tables",
        help="Directory for Markdown and CSV summary tables.",
    )
    return parser


def summarize(eval_dir: Path, out_dir: Path) -> tuple[Path, Path, int]:
    rows = []
    for json_path in iter_json_files(eval_dir):
        data = read_json(json_path)
        rows.append(evaluation_json_to_row(data, source_file=str(json_path)))

    if not rows:
        raise FileNotFoundError(f"No evaluation JSON files found under {eval_dir}")

    frame = rows_to_summary_frame(rows)
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / "summary.csv"
    markdown_path = out_dir / "summary.md"
    legacy_csv_path = out_dir / "evaluation_summary.csv"
    legacy_markdown_path = out_dir / "evaluation_summary.md"
    frame.to_csv(csv_path, index=False)
    frame.to_csv(legacy_csv_path, index=False)
    markdown = to_markdown_table(frame, columns=SUMMARY_COLUMNS) + "\n"
    markdown_path.write_text(markdown, encoding="utf-8")
    legacy_markdown_path.write_text(markdown, encoding="utf-8")
    return csv_path, markdown_path, len(frame)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        csv_path, markdown_path, row_count = summarize(args.eval_dir, args.out_dir)
    except FileNotFoundError as exc:
        parser.error(str(exc))
    print(f"Wrote {row_count} rows to {csv_path}")
    print(f"Wrote Markdown summary to {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
