"""Result table helpers for README and report generation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd

SUMMARY_COLUMNS = [
    "policy",
    "task_id",
    "terrain",
    "randomization",
    "seed",
    "evaluation_seed",
    "episodes",
    "mean_return",
    "std_return",
    "mean_episode_length",
    "fall_rate",
    "checkpoint_path",
]


def evaluation_json_to_row(
    data: Mapping[str, Any],
    source_file: str | None = None,
) -> dict[str, Any]:
    """Normalize one evaluation JSON object into a summary-table row."""
    returns = _as_float_list(data.get("per_episode_returns", []))
    lengths = _as_float_list(data.get("per_episode_lengths", []))

    mean_return = data.get("mean_return")
    if mean_return is None and returns:
        mean_return = sum(returns) / len(returns)

    mean_episode_length = data.get("mean_episode_length")
    if mean_episode_length is None and lengths:
        mean_episode_length = sum(lengths) / len(lengths)

    row = {
        "policy": data.get("policy") or data.get("run_id") or data.get("name") or "unknown",
        "task_id": data.get("task_id", ""),
        "terrain": data.get("terrain", ""),
        "randomization": data.get("randomization", ""),
        "seed": data.get("seed", ""),
        "evaluation_seed": data.get("evaluation_seed", ""),
        "episodes": data.get("episodes") or len(returns) or "",
        "mean_return": mean_return,
        "std_return": data.get("std_return"),
        "mean_episode_length": mean_episode_length,
        "fall_rate": data.get("fall_rate"),
        "checkpoint_path": data.get("checkpoint_path", ""),
        "source_file": source_file or "",
    }
    return row


def rows_to_summary_frame(rows: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    """Create a stable summary dataframe from normalized rows."""
    frame = pd.DataFrame(rows)
    if frame.empty:
        return pd.DataFrame(columns=[*SUMMARY_COLUMNS, "source_file"])

    for column in [*SUMMARY_COLUMNS, "source_file"]:
        if column not in frame.columns:
            frame[column] = ""

    sort_columns = [
        column for column in ["policy", "terrain", "randomization", "seed"] if column in frame
    ]
    if sort_columns:
        frame = frame.sort_values(sort_columns, kind="stable")

    return frame.loc[:, [*SUMMARY_COLUMNS, "source_file"]].reset_index(drop=True)


def to_markdown_table(frame: pd.DataFrame, columns: Sequence[str] | None = None) -> str:
    """Convert a dataframe to a Markdown table without requiring tabulate."""
    if columns:
        table = frame.loc[:, [column for column in columns if column in frame.columns]]
    else:
        table = frame
    headers = [str(column) for column in table.columns]
    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    row_lines = [
        "| " + " | ".join(_format_markdown_cell(value) for value in row) + " |"
        for row in table.itertuples(index=False, name=None)
    ]
    return "\n".join([header_line, separator_line, *row_lines])


def _as_float_list(value: object) -> list[float]:
    if not isinstance(value, list):
        return []
    output = []
    for item in value:
        try:
            output.append(float(item))
        except (TypeError, ValueError):
            continue
    return output


def _format_markdown_cell(value: object) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    return str(value).replace("\n", " ")
