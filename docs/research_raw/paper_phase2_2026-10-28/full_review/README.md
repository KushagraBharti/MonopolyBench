# Complete-game reading copies

Each `game-XX/manifest.json` lists the exact decision and attempt counts and the reading pages. Read every listed page in order. Old unlisted page files from an earlier preparation are not part of the current reading view. The pages concatenate to `behavior.json`.

`$same_as` means the value is exactly equal to an earlier JSON subtree at the given pointer. `$decoded_json_string` shows the complete parsed value of an originally serialized JSON string, including every public/private/tool argument. Formatting-only originals are in the matching JSON-string sidecar. Invalid JSON remains verbatim. No differing text is replaced with an equal-value reference.

The behavior view contains every applied action, canonical event payload, initial model observation and system instruction, every attempt prompt, every provider choice/message, assistant content, parsed tool call, validation error and response outcome. Billing/latency metadata and redundant response envelopes remain in `reading.json` and the original source packets. No behavior classification or candidate selection occurs in preparation.

The preparation script verifies byte-preserving restoration of original JSON string values and exact reconstruction of the complete source packet JSON. It separately verifies the behavior view round trip. Source paths, original line hashes and decision IDs are in the manifest. These checks establish preservation, not semantic review.

To inspect a reference, load `behavior.json`, use `decode` from `prepare_reading_chunks.py`, then follow the JSON pointer. To obtain exact original JSON text, use `restore` from `prepare_game_reading.py` and `behavior_json_strings.json`. Canonical source packets remain available for exposure, legal-menu, financing and provenance checks.

Review notes should be concise. Record coverage only after the entire decision and every available channel/attempt have actually been read. Keep important findings and full-game trajectories in the game note. Do not stop at page boundaries; keep using the next page until the complete assigned game and its final events have been reviewed.
