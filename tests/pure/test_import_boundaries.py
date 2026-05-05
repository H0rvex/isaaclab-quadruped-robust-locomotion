from pathlib import Path

FORBIDDEN_IMPORTS = (
    "import isaaclab",
    "import isaacsim",
    "import omni",
    "import pxr",
    "from pxr",
    "import rclpy",
    "from rclpy",
)


def test_package_import_does_not_require_isaac_stack() -> None:
    import isaaclab_quadruped

    assert isaaclab_quadruped.__version__


def test_source_modules_do_not_import_isaac_stack() -> None:
    source_root = Path("source/isaaclab_quadruped")
    for path in source_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert not any(forbidden in text for forbidden in FORBIDDEN_IMPORTS), path
