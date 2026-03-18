from pathlib import Path


def run():
    return Path("README.md").read_text(encoding="utf-8")
