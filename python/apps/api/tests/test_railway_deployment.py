"""Guard the packaging failures observed on Railway's hosted Docker builder."""
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[4]


def test_railway_recipe_supports_hosted_builder_and_persistent_runtime():
    config = json.loads((ROOT / "railway.json").read_text())
    recipe = (ROOT / config["build"]["dockerfilePath"]).read_text()
    assert config["deploy"]["numReplicas"] == 1
    assert config["deploy"]["healthcheckPath"] == "/api/health"
    assert config["deploy"]["startCommand"] == "python -m monopoly_api.serve"
    # Railway rejects bind and secret mounts before the build even starts.
    assert all(kind == "cache" for kind in re.findall(r"--mount=type=([^,\s]+)", recipe))
    assert "COPY --from=provenance /build_info.json ./build_info.json" in recipe
    assert "--git-sha" in recipe and 'ARG MB_GIT_SHA=""' in recipe
    assert "uv sync --frozen --all-packages --no-dev" in recipe
    assert "VITE_MB_MODE=cloud npm run build" in recipe
    # The hosted recipe must retain the local image's process/lifecycle contract.
    local = (ROOT / "deploy/Dockerfile").read_text()
    assert recipe[recipe.index("ENV MB_MODE="):] == local[local.index("ENV MB_MODE="):]


def test_railway_upload_includes_build_inputs_and_excludes_artifacts(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text((ROOT / ".railwayignore").read_text())
    included = ["railway.json", ".dockerignore", "deploy/Dockerfile.railway",
                "scripts/build_manifest.py", "python/uv.lock", "frontend/package-lock.json",
                "contracts/schemas/action.schema.json", "campaigns/example.json"]
    excluded = ["saved_games/example/run/decisions.jsonl", "runs/example/events.jsonl",
                "MonopolyBench Showcase.mp4", "python/.venv/bin/python",
                "frontend/node_modules/example/index.js", "frontend/dist/index.html",
                ".env", "python/.env", "python/__pycache__/example.pyc"]
    for name in included + excluded:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    result = subprocess.run(["git", "check-ignore", "--no-index", "--stdin"], cwd=tmp_path,
                            input="\n".join(included + excluded) + "\n", text=True,
                            capture_output=True, check=False)
    assert result.returncode == 0, result.stderr
    assert set(result.stdout.splitlines()) == set(excluded)
