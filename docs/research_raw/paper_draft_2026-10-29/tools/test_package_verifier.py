"""Ensure the manuscript verifier rejects the concrete round-3 regressions."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(folder):
    return subprocess.run([sys.executable, "tools/verify_draft.py", "--portable"],
                          cwd=folder, text=True, capture_output=True, check=False)


def main():
    results = []
    with tempfile.TemporaryDirectory(prefix="monopoly-verifier-test-") as tmp:
        copy = Path(tmp)
        for folder in ("data", "sections", "artifacts"):
            shutil.copytree(ROOT / folder, copy / folder)
        for name in ("manuscript.tex", "preamble.tex", "references.bib",
                     "protected_sources.json", "manuscript.pdf"):
            shutil.copy2(ROOT / name, copy / name)
        (copy / "tools").mkdir()
        shutil.copy2(ROOT / "tools/verify_draft.py", copy / "tools/verify_draft.py")
        shutil.copy2(ROOT / "tools/build_transcript_cards.py", copy / "tools/build_transcript_cards.py")
        (copy / "build").mkdir()
        shutil.copy2(ROOT / "build/manuscript.log", copy / "build/manuscript.log")
        baseline = run(copy)
        assert baseline.returncode == 0, baseline.stderr
        results.append({"case": "unaltered_package", "expected": "pass", "exit": 0})
        mutations = [
            ("resolution_conditions.json", ("counts", "Sol", "applied_end")),
            ("certificate_results.json", ("summary", "default_targets_reachable")),
            ("opportunity_ledger.json", ("rows", 0, "groups")),
            ("transcript_manifest.json", ("quotes", 0, "excerpts", 0, "text")),
        ]
        for name, keys in mutations:
            path = copy / "data" / name
            original = path.read_bytes()
            value = json.loads(original)
            node = value
            for key in keys[:-1]:
                node = node[key]
            node[keys[-1]] = 999999
            path.write_text(json.dumps(value))
            attempt = run(copy)
            assert attempt.returncode != 0, f"Mutation escaped: {name} {keys}"
            results.append({"case": name + ":" + ".".join(map(str, keys)),
                            "expected": "reject", "exit": attempt.returncode})
            path.write_bytes(original)
        for name, old, new in [
            ("sections/setup.tex", r"\ref{sec:claim-protocol}", r"\\ref{sec:claim-protocol}"),
            ("sections/end_provenance_table.tex", "Sol & 399 & 236", "Sol & 399 & 999999"),
            ("sections/transcript_quotes.tex", r"\$600, final.", r"\$650, final."),
        ]:
            path = copy / name
            original = path.read_text()
            assert old in original
            path.write_text(original.replace(old, new, 1))
            attempt = run(copy)
            assert attempt.returncode != 0, f"Mutation escaped: {name}"
            results.append({"case": name, "expected": "reject", "exit": attempt.returncode})
            path.write_text(original)
    report = {"status": "pass", "cases": results,
              "verifier_sha256": hashlib.sha256((ROOT / "tools/verify_draft.py").read_bytes()).hexdigest(),
              "scope": "One unaltered pass and seven isolated corrupted-copy rejections, including a changed quote and changed typeset quote; no canonical files edited."}
    (ROOT / "qa").mkdir(exist_ok=True)
    (ROOT / "qa/verifier_regression.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": "pass", "checks": len(results)}))


if __name__ == "__main__":
    main()
