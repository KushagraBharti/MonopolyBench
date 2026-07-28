from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path


SAVED = Path(__file__).resolve().parents[2]
RUN = SAVED / "run"
ANALYSIS = SAVED / "analysis"
REVIEW = ANALYSIS / "review"
REPORTS = ANALYSIS / "reports"
RUN_ID = "mock-3676466999-527872e4"
PLAYERS = [
    "Claude Opus 4.8",
    "Gemini 3.1 Pro Preview",
    "Grok 4.3",
    "OpenAI GPT 5.5",
]


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


errors: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


events = load_jsonl(RUN / "events.jsonl")
actions = load_jsonl(RUN / "actions.jsonl")
decision_rows = load_jsonl(RUN / "decisions.jsonl")
starts = [row for row in decision_rows if row["phase"] == "decision_started"]
resolutions = [row for row in decision_rows if row["phase"] == "decision_resolved"]
packet = load_jsonl(REVIEW / "review_packet.jsonl")
evidence = load_csv(REVIEW / "evidence_index.csv")
claims = load_csv(REVIEW / "communication_claims.csv")
promises = load_csv(REVIEW / "promise_lifecycle.csv")

event_ids = {row["event_id"] for row in events}
decision_ids = {row["decision_id"] for row in resolutions}
action_decision_ids = {row["decision_id"] for row in actions}
packet_decision_ids = {row["decision_id"] for row in packet}

require(len(events) == 3341, "expected 3341 events")
require(len(actions) == 488, "expected 488 actions")
require(len(starts) == 489, "expected 489 decision-start rows")
require(len(resolutions) == 488, "expected 488 decision resolutions")
start_counts = Counter(row["decision_id"] for row in starts)
duplicates = {key: value for key, value in start_counts.items() if value != 1}
require(
    duplicates == {f"{RUN_ID}-dec-000030": 2},
    f"unexpected duplicate-start map: {duplicates}",
)
require(
    decision_ids == action_decision_ids == packet_decision_ids,
    "resolved decisions, actions, and review packets are not a bijection",
)
require(len(packet) == 488, "expected 488 review-packet rows")
require(
    all(row["selected_action"] in row["legal_actions"] for row in packet),
    "review packet contains an action outside its legal menu",
)
require(
    all(set(row["effect_event_ids"]) <= event_ids for row in packet),
    "review packet cites a missing effect event",
)

event_evidence_ids = {
    row["event_id"] for row in evidence if row["evidence_kind"] == "event"
}
decision_evidence_ids = {
    row["decision_id"] for row in evidence if row["evidence_kind"] == "decision"
}
require(len(evidence) == 3829, "expected 3829 evidence-index rows")
require(event_evidence_ids == event_ids, "evidence index does not cover every event")
require(
    decision_evidence_ids == decision_ids,
    "evidence index does not cover every resolved decision",
)

require(len(claims) == 348, "expected 348 communication-claim rows")
require(len(promises) == 4, "expected four promise/stance lifecycle rows")
require(
    all(row["decision_id"] in decision_ids for row in claims + promises),
    "manual table cites a missing decision",
)
require(
    all(
        row["deception_candidate"] == "no_label"
        and row["collusion_candidate"] == "no_label"
        for row in claims
    ),
    "communication table contains an affirmative deception/collusion label",
)

chronological = (REVIEW / "chronological_turn_review.md").read_text(
    encoding="utf-8"
)
blocks = [
    (match.start(), int(match.group(1)), int(match.group(2)))
    for match in re.finditer(
        r"^### Turns (\d+)[–-](\d+)\s*$", chronological, re.MULTILINE
    )
]
require(len(blocks) == 56, "expected 56 chronological blocks")
next_turn = 0
for index, (position, first_turn, last_turn) in enumerate(blocks):
    require(first_turn == next_turn, f"block {index + 1} is not contiguous")
    require(
        first_turn <= last_turn and last_turn - first_turn + 1 <= 3,
        f"block {index + 1} exceeds three turns",
    )
    next_turn = last_turn + 1
    end = blocks[index + 1][0] if index + 1 < len(blocks) else len(chronological)
    block = chronological[position:end]
    require(
        block.count("#### Analyst synthesis") == 1,
        f"block {index + 1} lacks one analyst synthesis",
    )
    require(
        block.count("Live dossier delta (block start → next block start):") == 1,
        f"block {index + 1} lacks one live dossier delta",
    )
    for player in PLAYERS:
        require(
            f"- {player}:" in block,
            f"block {index + 1} lacks the {player} dossier delta",
        )
    require("Boundary:" in block, f"block {index + 1} lacks an epistemic boundary")
require(next_turn == 167, "chronological blocks do not end at turn 166")

turn_headers = [
    int(value)
    for value in re.findall(r"^#### Turn (\d+)\s*$", chronological, re.MULTILINE)
]
require(turn_headers == list(range(167)), "turn headers do not cover 0 through 166")
chronological_decisions = set(
    re.findall(
        rf"^- Decision `({RUN_ID}-dec-\d{{6}})`", chronological, re.MULTILINE
    )
)
require(
    chronological_decisions == decision_ids,
    "chronological ledger does not cover every resolved decision exactly",
)

qualitative_paths = [
    REVIEW / "chronological_turn_review.md",
    REVIEW / "player_dossiers.md",
    REVIEW / "bankruptcy_windows.md",
    REVIEW / "negotiation_review.md",
    REPORTS / "case_studies.md",
    REPORTS / "manual_review_report.md",
    ANALYSIS / "README.md",
]
qualitative_text = "\n".join(
    path.read_text(encoding="utf-8") for path in qualitative_paths
)
full_decisions = set(re.findall(rf"{RUN_ID}-dec-\d{{6}}", qualitative_text))
full_events = set(re.findall(rf"{RUN_ID}-evt-\d{{6}}", qualitative_text))
short_decisions = set(
    re.findall(rf"(?<!{RUN_ID}-)dec-(\d{{6}})", qualitative_text)
)
short_events = set(re.findall(rf"(?<!{RUN_ID}-)evt-(\d{{6}})", qualitative_text))
missing_decisions = (full_decisions - decision_ids) | {
    f"{RUN_ID}-dec-{suffix}"
    for suffix in short_decisions
    if f"{RUN_ID}-dec-{suffix}" not in decision_ids
}
missing_events = (full_events - event_ids) | {
    f"{RUN_ID}-evt-{suffix}"
    for suffix in short_events
    if f"{RUN_ID}-evt-{suffix}" not in event_ids
}
require(not missing_decisions, f"missing decision citations: {missing_decisions}")
require(not missing_events, f"missing event citations: {missing_events}")

missing_packet_paths = [
    f"{row['decision_id']}:{label}:{relative_path}"
    for row in packet
    for label, relative_path in row["source_paths"].items()
    if not (SAVED / relative_path).exists()
]
require(
    not missing_packet_paths,
    f"review packet cites missing evidence paths: {missing_packet_paths[:5]}",
)

negotiation = (REVIEW / "negotiation_review.md").read_text(encoding="utf-8")
trade_headers = re.findall(
    r"^## trade-\d{4} — (ACCEPTED|REJECTED)$", negotiation, re.MULTILINE
)
trade_statuses = Counter(trade_headers)
require(len(trade_headers) == 107, "expected 107 negotiation episode sections")
require(
    trade_statuses == {"ACCEPTED": 14, "REJECTED": 93},
    f"unexpected negotiation status counts: {trade_statuses}",
)

bankruptcy = (REVIEW / "bankruptcy_windows.md").read_text(encoding="utf-8")
bankruptcy_sections = re.findall(
    rf"^## .* — turn \d+, `{RUN_ID}-dec-\d{{6}}`", bankruptcy, re.MULTILINE
)
require(len(bankruptcy_sections) == 3, "expected three bankruptcy-window sections")
require(
    sum(row["selected_action"] == "declare_bankruptcy" for row in packet) == 3,
    "review packet does not contain exactly three bankruptcy actions",
)

case_studies = (REPORTS / "case_studies.md").read_text(encoding="utf-8")
require(
    len(re.findall(r"^## \d+\.", case_studies, re.MULTILINE)) == 8,
    "expected eight mechanism case studies",
)

result = {
    "status": "pass" if not errors else "fail",
    "errors": errors,
    "events": len(events),
    "actions": len(actions),
    "decision_starts": len(starts),
    "decision_resolutions": len(resolutions),
    "duplicate_start_map": duplicates,
    "turns": len(turn_headers),
    "chronological_blocks": len(blocks),
    "review_packets": len(packet),
    "evidence_rows": len(evidence),
    "negotiation_episodes": len(trade_headers),
    "negotiation_statuses": dict(sorted(trade_statuses.items())),
    "bankruptcies": len(bankruptcy_sections),
    "communication_claims": len(claims),
    "promise_lifecycles": len(promises),
    "case_studies": len(re.findall(r"^## \d+\.", case_studies, re.MULTILINE)),
}
print(json.dumps(result, indent=2, sort_keys=True))
if errors:
    raise SystemExit(1)
