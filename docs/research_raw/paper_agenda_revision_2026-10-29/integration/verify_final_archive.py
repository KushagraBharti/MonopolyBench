"""Rebuild the exact final manuscript archive outside its source checkout."""
import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

import pymupdf

HERE = Path(__file__).resolve().parent
DRAFT = HERE.parents[1] / "paper_draft_2026-10-29"
ARCHIVE = DRAFT / "monopolybench-revised-draft.zip"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    temp = Path(tempfile.mkdtemp(prefix="monopoly-final-manuscript-"))
    with zipfile.ZipFile(ARCHIVE) as archive:
        archive.extractall(temp)
    root = temp / "monopolybench-revised-draft"
    commands = []

    def run(args, expected=0):
        result = subprocess.run(args, cwd=root, text=True, capture_output=True, check=False)
        commands.append({"args": args, "exit": result.returncode,
                         "stdout": result.stdout, "stderr": result.stderr})
        assert (result.returncode == 0) == (expected == 0), result.stderr + result.stdout[-2000:]

    manifest = json.loads((root / "package_manifest.json").read_text())
    for name, digest in manifest.items():
        assert sha(root / name) == digest, name
    with zipfile.ZipFile(root / "artifacts/research-agenda-audit.zip") as source_archive:
        prefix = "docs/research_raw/paper_agenda_revision_2026-10-29/"
        source_manifest = json.loads(source_archive.read(prefix + "archive_manifest.json"))
        for name, digest in source_manifest.items():
            assert hashlib.sha256(source_archive.read(prefix + name)).hexdigest() == digest, name
    original_pdf = (root / "manuscript.pdf").read_bytes()
    nested = sha(root / "artifacts/historical-claim-audit.zip")
    assert nested == "bd0de225dc6e0ecb215326504d11afa51bb5ed8164da87b63c9fcc3072cc74f6"
    uv = shutil.which("uv")
    assert uv
    run([uv, "venv", "--python", "3.14.7", ".venv"])
    python = str(root / ".venv/bin/python")
    run([uv, "pip", "install", "--python", python, "-r", "requirements-manuscript.txt"])
    # Required-file omission must fail rather than silently produce a partial ZIP.
    (root / "README.md").rename(root / "README.held")
    try:
        run([python, "tools/package_draft.py"], expected=1)
    finally:
        (root / "README.held").rename(root / "README.md")
    run([python, "tools/build_exhibits.py"])
    run([python, "tools/build_adversarial_tables.py"])
    run([python, "tools/build_transcript_cards.py"])
    run([python, "tools/build_agenda_exhibits.py"])
    run(["bash", "build.sh"])
    run([python, "tools/verify_draft.py", "--portable"])
    run([python, "tools/test_package_verifier.py"])
    run([python, "tools/verify_agenda.py"])
    run([python, "tools/test_agenda_verifier.py"])
    before = pymupdf.open(stream=original_pdf, filetype="pdf")
    after = pymupdf.open(root / "manuscript.pdf")
    assert len(before) == len(after)
    equal = []
    for i, (a, b) in enumerate(zip(before, after, strict=True)):
        assert a.rect == b.rect and a.rotation == b.rotation, i
        assert a.get_text() == b.get_text(), i
        assert a.get_pixmap(dpi=100).samples == b.get_pixmap(dpi=100).samples, i
        equal.append(i + 1)
    report = {"status": "pass", "archive_sha256": sha(ARCHIVE),
              "archive_files": len(manifest) + 1, "extraction": str(root),
              "fresh_python_environment": True, "TeX_environment": "same installed TeX Live 2026",
              "pages_text_geometry_pixels_equal": equal,
              "pdf_bytes_equal": original_pdf == (root / "manuscript.pdf").read_bytes(),
              "required_file_omission_rejected": True,
              "agenda_source_archive_files_checked": len(source_manifest),
              "nested_artifact_sha256": nested,
              "nested_scope": "Byte-identical to the separately clean-executed and independently reviewed nine-test artifact; not re-executed by this manuscript check.",
              "commands": commands}
    (DRAFT / "final_package_verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in {"commands", "pages_text_geometry_pixels_equal"}}))


if __name__ == "__main__":
    main()
