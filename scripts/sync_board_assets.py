"""Copy the approved Blender exports into the frontend's self-contained asset pack."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output/blender/monopoly_atelier/game_ready"
DEST = ROOT / "frontend/public/board3d/v1"
DEST.mkdir(parents=True, exist_ok=True)
source = json.loads((SOURCE / "asset_manifest.json").read_text())
names = ["board_web", "house", "hotel", "jail_gate", "die", "player_red", "player_blue", "player_green", "player_gold"]
manifest = {key: source[key] for key in (
    "schema", "coordinates", "space_anchors", "development_anchors",
    "jail_gate_anchor_blender", "jail_player_anchors_blender", "status_markers", "player_scales"
)}
manifest["assets"] = {}
for name in names:
    asset = source["assets"][name]
    file = Path(asset["file"]).name
    shutil.copy2(SOURCE / asset["file"], DEST / file)
    manifest["assets"][name] = {"file": file, "bytes": (DEST / file).stat().st_size}
(DEST / "manifest.json").write_text(json.dumps(manifest, indent=2))
draco = ROOT / "frontend/node_modules/three/examples/jsm/libs/draco/gltf"
(DEST / "draco").mkdir(exist_ok=True)
for name in ("draco_decoder.wasm", "draco_wasm_wrapper.js", "draco_decoder.js"):
    shutil.copy2(draco / name, DEST / "draco" / name)
shutil.copy2(ROOT / "frontend/node_modules/three/LICENSE", DEST / "THREE-LICENSE.txt")
license_path = draco.parent / "README.md"
if license_path.is_file():
    shutil.copy2(license_path, DEST / "DRACO-README.md")
print(f"Prepared {len(names)} assets with local Draco decoders: {DEST}")
