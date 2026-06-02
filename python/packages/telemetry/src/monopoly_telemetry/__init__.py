from .analysis import write_trace_failure_artifacts
from .run_files import RunFiles, build_artifact_manifest, build_run_files, init_run_files
from .scorecard import build_scorecard, write_scorecard_artifacts
from .summary import build_summary
from .usage import build_usage_report, write_usage_artifacts
from .writer_jsonl import append_jsonl


def hello() -> str:
    return "Hello from monopoly_telemetry!"


__all__ = [
    "RunFiles",
    "append_jsonl",
    "hello",
    "init_run_files",
    "build_run_files",
    "build_artifact_manifest",
    "build_summary",
    "build_scorecard",
    "write_scorecard_artifacts",
    "build_usage_report",
    "write_usage_artifacts",
    "write_trace_failure_artifacts",
]
