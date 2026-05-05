"""CLI wrapper for the local hardware-interface demo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "source"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from isaaclab_quadruped.deployment.interface_demo import (  # noqa: E402
    format_plain_summary,
    run_interface_demo,
    write_demo_summary,
)

DEFAULT_JSON_OUT = PROJECT_ROOT / "results/demo/local_interface_demo.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the local policy/ROS 2 interface demo without simulator dependencies.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=DEFAULT_JSON_OUT,
        help="Path for the machine-readable JSON summary artifact.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary = run_interface_demo(
            policy_config_path=PROJECT_ROOT / "configs/deployment/go2_policy_interface.yaml",
            topics_config_path=PROJECT_ROOT / "configs/deployment/ros2_topics.yaml",
            json_out=args.json_out,
        )
        summary["json_out"] = str(args.json_out)
        write_demo_summary(args.json_out, summary)
    except Exception as exc:
        summary = {
            "final_status": "FAIL",
            "error": str(exc),
            "json_out": str(args.json_out),
        }
        write_demo_summary(args.json_out, summary)
        print(format_plain_summary(summary), file=sys.stderr)
        return 1

    print(format_plain_summary(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
