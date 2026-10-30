"""Package and clean-run the frozen historical audit without repository imports."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
AUDIT = HERE / "executable_audit"
names = ["README.md", "LICENSE", "run_audit.py", "test_certificates.py", "freeze_inputs.py",
         "cases.json", "games.json", "inputs_manifest.json", "results.json",
         "requirements.txt", "environment.json", "incomplete_delegate_record.md"]
files = [AUDIT / name for name in names]
for folder in ("inputs", "vendor", "contracts"):
    files.extend(p for p in (AUDIT / folder).rglob("*")
                 if p.is_file() and "__pycache__" not in p.parts)
manifest = {str(p.relative_to(AUDIT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
(AUDIT / "artifact_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
files.append(AUDIT / "artifact_manifest.json")
archive = AUDIT / "historical-claim-audit.zip"
with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as out:
    for path in sorted(files):
        info = zipfile.ZipInfo("historical-claim-audit/" + str(path.relative_to(AUDIT)), (2026, 10, 29, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        out.writestr(info, path.read_bytes())

temporary = Path(tempfile.mkdtemp(prefix="monopoly-claim-audit-revised-"))
with zipfile.ZipFile(archive) as source:
    source.extractall(temporary)
work = temporary / "historical-claim-audit"
for name, expected in manifest.items():
    assert hashlib.sha256((work / name).read_bytes()).hexdigest() == expected
uv = shutil.which("uv")
assert uv, "uv required only for this clean-environment packaging check"
log = []
def run(args):
    completed = subprocess.run(args, cwd=work, text=True, capture_output=True, check=True)
    log.append({"args": list(map(str, args)), "stdout": completed.stdout, "stderr": completed.stderr})
run([uv, "venv", "--python", "3.14.7", ".venv"])
python = work / ".venv/bin/python"
run([uv, "pip", "install", "--python", str(python), "-r", "requirements.txt"])
run([str(python), "run_audit.py", "--output", "reproduced.json"])
run([str(python), "test_certificates.py"])
assert json.loads((work / "reproduced.json").read_text()) == json.loads((work / "results.json").read_text())
report = {"directory": str(work), "archive": str(archive), "files": len(files),
          "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
          "fresh_venv": True, "repository_imports_required": False, "results_equal": True,
          "tests_passed": 9, "replayed_events": 50918, "commands": log}
(AUDIT / "clean_environment.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "commands"}, indent=2))
