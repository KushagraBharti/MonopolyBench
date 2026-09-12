# 3D board integration

The live and replay pages render the exported Blender city through Three.js. The surrounding spectator and research interface retains its existing design. The renderer uses authoritative snapshots for ownership, buildings, mortgages, player positions, bankruptcy, and jail occupancy. It never generates legal actions, dice outcomes, or Monopoly rules.

## Local use

After the repository's dependency setup, run `pwsh -File scripts/start-local.ps1` from the root on Windows (Node.js is required). Open http://127.0.0.1:5173/. The launcher preserves existing port listeners, starts missing services on 8000 and 5173, and stores logs under `output/local-site/`. It starts development servers, not a public deployment.

Choose **3D city** or **Classic** above the board. Drag to orbit, scroll to zoom, or select Reset view / Overhead. Click a space or use the keyboard-accessible selector to inspect its snapshot values. Motion can be disabled; the system reduced-motion preference is also respected. A failed asset load or lost WebGL context falls back to Classic with an option to retry.

## State and motion

- Building counts control reusable house and hotel visibility. Purchases rise into place; sales remove pieces; hotels replace houses.
- Players move toward snapshot positions. Jail occupancy controls player placement and the moving gate.
- New `CARD_DRAWN` and dice events trigger temporary presentations. Card faces use the existing frontend card catalog; dice show supplied outcomes.
- Initial loading, reconnects, run changes, and replay snapshot selection apply state immediately and clear transient animations. Seeking does not replay historical effects.
- The presentation cursor suppresses duplicate events. The transient queue retains at most eight pending effects, keeping a fast stream from creating an unbounded visual backlog. All canonical events remain available in the event feed and saved artifacts.

Saved replay rows are projected into the existing UI shape by `replayPresentation.ts`, supporting both flat rows and rows containing an `event` wrapper without rewriting saved files.

## Assets

The self-contained web pack lives in `frontend/public/board3d/v1/`: the city board, house, hotel, jail gate, die, four player models, placement manifest, and local Draco decoders. It requires no Blender connection or remote asset CDN at runtime.

To refresh the pack from the approved local Blender exports, run `python scripts/sync_board_assets.py` after installing frontend dependencies. Its source is `output/blender/monopoly_atelier/game_ready/`. Blender coordinates `(x, y, z)` map to browser coordinates `(x, z, -y)`; anchors and scale are preserved by the manifest. The source Blender projects and native trigger demonstration remain independent of the web renderer. Web lighting and glTF materials approximate the native scene; native compositor effects are not exported.

## Verification

`pwsh -File scripts/verify.ps1` includes presentation unit tests, frontend lint/build, and the existing benchmark verification. Focused frontend checks are `bun run test`, `bun run lint`, and `bun run build` in `frontend/`.

With Vite running, open http://127.0.0.1:5173/tests/board3d.html and choose **Run visual checks**. This dev-only harness uses synthetic snapshots and events to inspect rendered house/hotel visibility, player/jail poses, card lifetime, dice orientation/clearance, mortgages, duplicate suppression, and resets. It does not write to the API or run LLM agents and is not a production build entry.
