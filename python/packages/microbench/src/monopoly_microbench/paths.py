from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "AGENTS.md").exists() and (parent / "contracts").exists():
            return parent
    return Path.cwd()


def contracts_micro_dir() -> Path:
    return repo_root() / "contracts" / "micro"


def scenarios_dir() -> Path:
    return contracts_micro_dir() / "scenarios"


def suites_dir() -> Path:
    return contracts_micro_dir() / "suites"


def default_runs_dir() -> Path:
    return Path(os.getenv("RUNS_DIR", str(repo_root() / "runs")))
