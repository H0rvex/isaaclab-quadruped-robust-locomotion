"""Plotting helpers for local result artifacts."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_training_curve(
    frame: pd.DataFrame,
    x: str,
    y: str,
    output_path: str | Path,
    *,
    title: str | None = None,
    ylabel: str | None = None,
) -> Path:
    """Plot a single training curve from an existing metrics dataframe."""
    _require_columns(frame, [x, y])
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(frame[x], frame[y], linewidth=1.8)
    ax.set_xlabel(x)
    ax.set_ylabel(ylabel or y)
    if title:
        ax.set_title(title)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)
    return output


def plot_grouped_curve(
    frame: pd.DataFrame,
    x: str,
    y: str,
    group: str,
    output_path: str | Path,
    *,
    title: str | None = None,
) -> Path:
    """Plot one curve per group from an existing metrics dataframe."""
    _require_columns(frame, [x, y, group])
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for group_value, group_frame in frame.groupby(group):
        ax.plot(group_frame[x], group_frame[y], linewidth=1.6, label=str(group_value))
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    if title:
        ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)
    return output


def _require_columns(frame: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
