from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
SAVED_GAMES_ROOT = REPO_ROOT / "saved_games"
DEFAULT_BOARD_PATH = REPO_ROOT / "contracts" / "data" / "board.json"
ANALYZER_VERSION = "negotiation-tactics-v1"
OFFER_EVENTS = {"TRADE_PROPOSED", "TRADE_COUNTERED"}
TERMINAL_EVENTS = {"TRADE_ACCEPTED", "TRADE_REJECTED", "TRADE_EXPIRED"}


def _entry(
    family: str, description: str, method: str, confidence: str, review: bool = False
) -> dict[str, Any]:
    return {
        "family": family,
        "description": description,
        "method": method,
        "confidence": confidence,
        "requires_manual_review": review,
    }


def _patterns(*values: str) -> tuple[re.Pattern[str], ...]:
    return tuple(re.compile(value, re.I) for value in values)


TACTIC_CODEBOOK: dict[str, dict[str, Any]] = {
    "INITIAL_ANCHOR": _entry(
        "structural", "First structured offer.", "episode_position", "high"
    ),
    "COUNTEROFFER": _entry(
        "structural", "Structured counteroffer.", "event_type", "high"
    ),
    "MULTI_ISSUE_PACKAGE": _entry(
        "structural", "At least three asset components.", "terms", "high"
    ),
    "CASH_SWEETENER": _entry(
        "structural", "Cash plus a non-cash asset.", "terms", "high"
    ),
    "CONCESSION": _entry(
        "derived", "Lower face-value net ask.", "face_value", "medium"
    ),
    "HARDENING": _entry(
        "derived", "Higher face-value net ask.", "face_value", "medium"
    ),
    "REPEATED_POSITION": _entry(
        "derived", "Unchanged face-value net ask.", "face_value", "medium"
    ),
    "FAIRNESS_FRAMING": _entry(
        "language", "Fairness or mutual-benefit frame.", "regex", "medium", True
    ),
    "VALUE_FRAMING": _entry(
        "language", "Value or monopoly frame.", "regex", "medium", True
    ),
    "RECIPROCITY_APPEAL": _entry(
        "language", "Reciprocal-help frame.", "regex", "medium", True
    ),
    "CONDITIONAL_CONCESSION": _entry(
        "language", "Conditional concession.", "regex", "medium", True
    ),
    "TAKE_IT_OR_LEAVE_IT": _entry(
        "language", "Final or non-negotiable terms.", "regex", "medium", True
    ),
    "URGENCY_OR_SCARCITY": _entry(
        "language", "Time or scarcity pressure.", "regex", "medium", True
    ),
    "LEADER_TARGETING_OR_COALITION": _entry(
        "language", "Joint action against a leader.", "regex", "medium", True
    ),
    "THREAT_OR_RETALIATION": _entry(
        "language", "Threat or retaliation.", "regex", "medium", True
    ),
    "INFORMATION_ELICITATION": _entry(
        "language", "Request for acceptable terms.", "regex", "medium", True
    ),
    "RATIONALE_DISCLOSURE": _entry(
        "language", "Explicit reason for terms.", "regex", "medium", True
    ),
    "ASSERTIVE_CLAIM_CANDIDATE": _entry(
        "language", "Absolute claim needing review.", "regex", "low", True
    ),
}

LANGUAGE_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "FAIRNESS_FRAMING": _patterns(
        r"\b(?:fair|balanced|equal|reasonable|win[- ]win|mutually beneficial)\b"
    ),
    "VALUE_FRAMING": _patterns(
        r"\b(?:value|worth|rent|income|return|roi|monopoly|color set)\b"
    ),
    "RECIPROCITY_APPEAL": _patterns(
        r"\b(?:reciprocat\w*|return the favou?r|owe (?:me|you))\b"
    ),
    "CONDITIONAL_CONCESSION": _patterns(
        r"\bif you\b.{0,100}\b(?:i(?:'ll| will)|then|we can|i can)\b",
        r"\b(?:provided that|on the condition that|in exchange for)\b",
    ),
    "TAKE_IT_OR_LEAVE_IT": _patterns(
        r"\b(?:take it or leave it|final offer|best and final|non[- ]negotiable|only offer)\b"
    ),
    "URGENCY_OR_SCARCITY": _patterns(
        r"\b(?:last chance|act now|before it(?:'s| is) too late|limited time|won't offer this again)\b"
    ),
    "LEADER_TARGETING_OR_COALITION": _patterns(
        r"\b(?:team up|work together|join forces|stop the leader|against the leader|shared threat)\b"
    ),
    "THREAT_OR_RETALIATION": _patterns(
        r"\b(?:retaliat\w*|punish\w*|make you pay|target you|you(?:'ll| will) regret)\b"
    ),
    "INFORMATION_ELICITATION": _patterns(
        r"\b(?:what would you (?:accept|want|take)|would you accept|what are your terms|counterproposal)\b"
    ),
    "RATIONALE_DISCLOSURE": _patterns(
        r"\b(?:because|since|so that|the reason|this gives you)\b"
    ),
    "ASSERTIVE_CLAIM_CANDIDATE": _patterns(
        r"\b(?:guaranteed|definitely|best possible|cannot lose|can't lose|no chance|certain to)\b"
    ),
}


def read_json(path: Path, default: Any = None) -> Any:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"Expected an object at {path}:{line_number}")
        rows.append(value)
    return rows


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(dict.fromkeys(key for row in rows for key in row)) or ["empty"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _csv_value(row.get(key)) for key in fieldnames})


def _csv_value(value: Any) -> Any:
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(
            value, separators=(",", ":"), sort_keys=True, ensure_ascii=True
        )
    if isinstance(value, bool):
        return int(value)
    return "" if value is None else value


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def normalize_property_key(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", value.upper()).strip("_")


def load_property_values(board_path: Path) -> dict[str, int]:
    values: dict[str, int] = {}
    for item in _list(_dict(read_json(board_path, {})).get("spaces")):
        space = _dict(item)
        if isinstance(space.get("name"), str) and isinstance(
            space.get("price"), (int, float)
        ):
            values[normalize_property_key(space["name"])] = int(space["price"])
    return values


def bundle_value(
    bundle: dict[str, Any], values: dict[str, int], jail_card_value: int
) -> tuple[int, list[str]]:
    unknown: list[str] = []
    total = (
        _int(bundle.get("cash"))
        + _int(bundle.get("get_out_of_jail_cards")) * jail_card_value
    )
    for value in _list(bundle.get("properties")):
        key = normalize_property_key(str(value))
        if key in values:
            total += values[key]
        else:
            unknown.append(str(value))
    return total, unknown


def resolve_source(source: str | Path) -> tuple[Path | None, Path]:
    candidate = Path(source)
    if not candidate.exists():
        candidate = SAVED_GAMES_ROOT / str(source)
    candidate = candidate.resolve()
    if (candidate / "events.jsonl").exists():
        return (candidate.parent if candidate.name == "run" else None), candidate
    if (candidate / "run" / "events.jsonl").exists():
        return candidate, candidate / "run"
    raise FileNotFoundError(f"Could not find events.jsonl under {source}")


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decision_indexes(
    decisions: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    by_id: dict[str, dict[str, Any]] = {}
    by_event: dict[str, dict[str, Any]] = {}
    for decision in decisions:
        decision_id = decision.get("decision_id")
        if isinstance(decision_id, str) and isinstance(
            decision.get("final_action"), dict
        ):
            by_id[decision_id] = decision
        for event_id in _list(decision.get("emitted_event_ids")):
            if isinstance(event_id, str):
                by_event[event_id] = decision
    return by_id, by_event


def decision_for_event(
    event: dict[str, Any],
    by_id: dict[str, dict[str, Any]],
    by_event: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    event_id = event.get("event_id")
    if isinstance(event_id, str) and event_id in by_event:
        return by_event[event_id]
    seq = event.get("seq")
    if isinstance(seq, int):
        for decision in by_id.values():
            start = decision.get("emitted_event_seq_start")
            end = decision.get("emitted_event_seq_end")
            if isinstance(start, int) and isinstance(end, int) and start <= seq <= end:
                return decision
    return {}


def actor_player_id(event: dict[str, Any]) -> str:
    actor_id = _dict(event.get("actor")).get("player_id")
    if isinstance(actor_id, str):
        return actor_id
    initiator = _dict(event.get("payload")).get("initiator_player_id")
    return (
        initiator
        if event.get("type") == "TRADE_PROPOSED" and isinstance(initiator, str)
        else ""
    )


def _run_id(
    run_dir: Path, events: list[dict[str, Any]], decisions: list[dict[str, Any]]
) -> str:
    for row in [*events, *decisions]:
        value = row.get("run_id")
        if isinstance(value, str) and value:
            return value
    return run_dir.name


def extract_episodes(
    run_dir: Path,
    property_values: dict[str, int],
    jail_card_value: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    events = sorted(
        read_jsonl(run_dir / "events.jsonl"), key=lambda row: _int(row.get("seq"))
    )
    decisions = read_jsonl(run_dir / "decisions.jsonl")
    by_id, by_event = decision_indexes(decisions)
    run_id = _run_id(run_dir, events, decisions)
    offers: list[dict[str, Any]] = []
    episodes: list[dict[str, Any]] = []
    warnings: list[str] = []
    active: dict[str, Any] | None = None
    episode_number = 0

    for event in events:
        event_type = str(event.get("type") or "")
        if event_type not in OFFER_EVENTS | TERMINAL_EVENTS:
            continue
        if event_type == "TRADE_PROPOSED":
            if active is not None:
                active["outcome"] = "INTERRUPTED_BY_NEW_PROPOSAL"
                episodes.append(active)
                warnings.append(f"Closed unterminated {active['episode_id']}")
            episode_number += 1
            payload = _dict(event.get("payload"))
            active = _new_episode(run_id, episode_number, event, payload)
        if active is None:
            warnings.append(f"Ignored orphan {event_type} at seq {event.get('seq')}")
            continue

        decision = decision_for_event(event, by_id, by_event)
        if event_type in OFFER_EVENTS:
            offer = _offer_row(
                active, event, decision, property_values, jail_card_value
            )
            active["offers"].append(offer)
            offers.append(offer)
        if event_type in TERMINAL_EVENTS:
            active["outcome"] = event_type
            active["terminal_seq"] = event.get("seq")
            active["terminal_turn_index"] = event.get("turn_index")
            active["terminal_decision_id"] = decision.get("decision_id")
            episodes.append(active)
            active = None

    if active is not None:
        active["outcome"] = "UNTERMINATED"
        episodes.append(active)
        warnings.append(f"Episode {active['episode_id']} has no terminal event")
    return offers, episodes, warnings


def _new_episode(
    run_id: str, number: int, event: dict[str, Any], payload: dict[str, Any]
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "episode_id": f"{run_id}-neg-{number:06d}",
        "initiator_player_id": payload.get("initiator_player_id"),
        "counterparty_player_id": payload.get("counterparty_player_id"),
        "start_seq": event.get("seq"),
        "start_turn_index": event.get("turn_index"),
        "outcome": None,
        "terminal_seq": None,
        "terminal_decision_id": None,
        "offers": [],
    }


def _other_party(episode: dict[str, Any], player_id: str) -> str:
    initiator = str(episode.get("initiator_player_id") or "")
    counterparty = str(episode.get("counterparty_player_id") or "")
    return counterparty if player_id == initiator else initiator


def _offer_row(
    episode: dict[str, Any],
    event: dict[str, Any],
    decision: dict[str, Any],
    property_values: dict[str, int],
    jail_card_value: int,
) -> dict[str, Any]:
    payload = _dict(event.get("payload"))
    offered = _dict(payload.get("offer"))
    requested = _dict(payload.get("request"))
    offer_value, offer_unknown = bundle_value(offered, property_values, jail_card_value)
    request_value, request_unknown = bundle_value(
        requested, property_values, jail_card_value
    )
    action = _dict(decision.get("final_action"))
    offerer = actor_player_id(event)
    net_ask = request_value - offer_value
    initiator = str(episode.get("initiator_player_id") or "")
    offer_index = len(_list(episode.get("offers")))
    return {
        "schema_version": "v1",
        "run_id": episode["run_id"],
        "episode_id": episode["episode_id"],
        "offer_id": f"{episode['episode_id']}-offer-{offer_index:03d}",
        "offer_index": offer_index,
        "event_id": event.get("event_id"),
        "seq": event.get("seq"),
        "turn_index": event.get("turn_index"),
        "event_type": event.get("type"),
        "exchange_index": payload.get("exchange_index"),
        "decision_id": decision.get("decision_id"),
        "offerer_player_id": offerer,
        "counterparty_player_id": _other_party(episode, offerer),
        "model_id": decision.get("openrouter_model_id") or offerer,
        "model_display_name": decision.get("model_display_name")
        or decision.get("player_name")
        or offerer,
        "action_name": action.get("action"),
        "public_message": action.get("public_message")
        if isinstance(action.get("public_message"), str)
        else "",
        "offer_cash": _int(offered.get("cash")),
        "offer_properties": [str(item) for item in _list(offered.get("properties"))],
        "offer_jail_cards": _int(offered.get("get_out_of_jail_cards")),
        "request_cash": _int(requested.get("cash")),
        "request_properties": [
            str(item) for item in _list(requested.get("properties"))
        ],
        "request_jail_cards": _int(requested.get("get_out_of_jail_cards")),
        "offer_face_value": offer_value,
        "request_face_value": request_value,
        "net_ask_face_value": net_ask,
        "initiator_net_ask_face_value": net_ask if offerer == initiator else -net_ask,
        "unknown_property_values": sorted(set(offer_unknown + request_unknown)),
        "previous_own_net_ask_face_value": None,
        "concession_face_value": None,
        "is_initial_offer": event.get("type") == "TRADE_PROPOSED",
        "is_final_submitted_offer": False,
        "is_accepted_offer": False,
    }


def finalize_episodes(raw_episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for episode in raw_episodes:
        episode_offers = [_dict(item) for item in _list(episode.get("offers"))]
        previous_by_actor: dict[str, int] = {}
        for offer in episode_offers:
            actor = str(offer.get("offerer_player_id"))
            current = _int(offer.get("net_ask_face_value"))
            if actor in previous_by_actor:
                previous = previous_by_actor[actor]
                offer["previous_own_net_ask_face_value"] = previous
                offer["concession_face_value"] = previous - current
            previous_by_actor[actor] = current
        if episode_offers:
            episode_offers[-1]["is_final_submitted_offer"] = True
            if episode.get("outcome") == "TRADE_ACCEPTED":
                episode_offers[-1]["is_accepted_offer"] = True
        rows.append(_episode_row(episode, episode_offers))
    return rows


def _episode_row(
    episode: dict[str, Any], offers: list[dict[str, Any]]
) -> dict[str, Any]:
    first = offers[0] if offers else {}
    final = offers[-1] if offers else {}
    initial_ask = first.get("initiator_net_ask_face_value")
    final_ask = final.get("initiator_net_ask_face_value")
    return {
        "schema_version": "v1",
        "run_id": episode.get("run_id"),
        "episode_id": episode.get("episode_id"),
        "initiator_player_id": episode.get("initiator_player_id"),
        "counterparty_player_id": episode.get("counterparty_player_id"),
        "start_seq": episode.get("start_seq"),
        "terminal_seq": episode.get("terminal_seq"),
        "start_turn_index": episode.get("start_turn_index"),
        "terminal_turn_index": episode.get("terminal_turn_index"),
        "terminal_decision_id": episode.get("terminal_decision_id"),
        "outcome": episode.get("outcome"),
        "accepted": episode.get("outcome") == "TRADE_ACCEPTED",
        "offer_count": len(offers),
        "counteroffer_count": max(0, len(offers) - 1),
        "initial_offer_id": first.get("offer_id"),
        "initial_offerer_player_id": first.get("offerer_player_id"),
        "initial_initiator_net_ask_face_value": initial_ask,
        "final_offer_id": final.get("offer_id"),
        "final_offerer_player_id": final.get("offerer_player_id"),
        "final_initiator_net_ask_face_value": final_ask,
        "initiator_net_ask_change": _int(final_ask) - _int(initial_ask)
        if first and final
        else None,
    }


def classify_tactics(offers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for offer in offers:
        detected: list[tuple[str, str]] = []
        if offer.get("is_initial_offer"):
            detected.append(("INITIAL_ANCHOR", "offer_index=0"))
        if offer.get("event_type") == "TRADE_COUNTERED":
            detected.append(("COUNTEROFFER", "event_type=TRADE_COUNTERED"))
        components = _component_count(offer)
        if components >= 3:
            detected.append(("MULTI_ISSUE_PACKAGE", f"component_count={components}"))
        has_cash = (
            _int(offer.get("offer_cash")) > 0 or _int(offer.get("request_cash")) > 0
        )
        has_assets = bool(
            _list(offer.get("offer_properties"))
            or _list(offer.get("request_properties"))
        )
        has_assets = has_assets or _int(offer.get("offer_jail_cards")) > 0
        has_assets = has_assets or _int(offer.get("request_jail_cards")) > 0
        if has_cash and has_assets:
            detected.append(("CASH_SWEETENER", "cash_and_non_cash_assets"))
        _add_concession_tactic(offer, detected)
        _add_language_tactics(str(offer.get("public_message") or ""), detected)
        rows.extend(_tactic_rows(offer, detected))
    return rows


def _component_count(offer: dict[str, Any]) -> int:
    return sum(
        (
            int(_int(offer.get("offer_cash")) > 0),
            int(bool(_list(offer.get("offer_properties")))),
            int(_int(offer.get("offer_jail_cards")) > 0),
            int(_int(offer.get("request_cash")) > 0),
            int(bool(_list(offer.get("request_properties")))),
            int(_int(offer.get("request_jail_cards")) > 0),
        )
    )


def _add_concession_tactic(
    offer: dict[str, Any], detected: list[tuple[str, str]]
) -> None:
    concession = offer.get("concession_face_value")
    if not isinstance(concession, (int, float)):
        return
    if concession > 0:
        detected.append(("CONCESSION", f"face_value_change={concession:g}"))
    elif concession < 0:
        detected.append(("HARDENING", f"face_value_change={concession:g}"))
    else:
        detected.append(("REPEATED_POSITION", "face_value_change=0"))


def _add_language_tactics(message: str, detected: list[tuple[str, str]]) -> None:
    for tactic_id, patterns in LANGUAGE_PATTERNS.items():
        for pattern in patterns:
            match = pattern.search(message)
            if match is not None:
                detected.append((tactic_id, match.group(0)))
                break


def _tactic_rows(
    offer: dict[str, Any], detected: list[tuple[str, str]]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for tactic_id, evidence in detected:
        definition = TACTIC_CODEBOOK[tactic_id]
        rows.append(
            {
                "schema_version": "v1",
                "run_id": offer.get("run_id"),
                "episode_id": offer.get("episode_id"),
                "offer_id": offer.get("offer_id"),
                "offer_index": offer.get("offer_index"),
                "decision_id": offer.get("decision_id"),
                "offerer_player_id": offer.get("offerer_player_id"),
                "model_id": offer.get("model_id"),
                "model_display_name": offer.get("model_display_name"),
                "tactic_id": tactic_id,
                "tactic_family": definition["family"],
                "detection_method": definition["method"],
                "confidence": definition["confidence"],
                "requires_manual_review": definition["requires_manual_review"],
                "evidence": evidence,
            }
        )
    return rows


def _group_key(row: dict[str, Any], include_run: bool) -> tuple[str, ...]:
    model_id = str(row.get("model_id") or row.get("offerer_player_id") or "unknown")
    display = str(row.get("model_display_name") or model_id)
    return (
        (str(row.get("run_id") or "unknown"), model_id, display)
        if include_run
        else (model_id, display)
    )


def tactic_frequency_rows(
    offers: list[dict[str, Any]],
    tactics: list[dict[str, Any]],
    *,
    include_run: bool,
) -> list[dict[str, Any]]:
    offer_ids: dict[tuple[str, ...], set[str]] = defaultdict(set)
    episode_ids: dict[tuple[str, ...], set[str]] = defaultdict(set)
    counts: Counter[tuple[str, ...]] = Counter()
    totals: Counter[tuple[str, ...]] = Counter()
    for offer in offers:
        key = _group_key(offer, include_run)
        offer_ids[key].add(str(offer.get("offer_id")))
        episode_ids[key].add(str(offer.get("episode_id")))
    for tactic in tactics:
        key = _group_key(tactic, include_run)
        counts[(*key, str(tactic.get("tactic_id")))] += 1
        totals[key] += 1
    return [
        _frequency_row(key, count, offer_ids, episode_ids, totals, include_run)
        for key, count in sorted(counts.items())
    ]


def _frequency_row(
    tactic_key: tuple[str, ...],
    count: int,
    offer_ids: dict[tuple[str, ...], set[str]],
    episode_ids: dict[tuple[str, ...], set[str]],
    totals: Counter[tuple[str, ...]],
    include_run: bool,
) -> dict[str, Any]:
    if include_run:
        run_id, model_id, display, tactic_id = tactic_key
        base = (run_id, model_id, display)
    else:
        model_id, display, tactic_id = tactic_key
        base = (model_id, display)
        run_id = None
    offer_count = len(offer_ids[base])
    episode_count = len(episode_ids[base])
    row = {
        "schema_version": "v1",
        "model_id": model_id,
        "model_display_name": display,
        "tactic_id": tactic_id,
        "tactic_family": TACTIC_CODEBOOK[tactic_id]["family"],
        "tactic_use_count": count,
        "offer_count": offer_count,
        "episode_count": episode_count,
        "frequency_per_offer": count / offer_count if offer_count else None,
        "frequency_per_episode": count / episode_count if episode_count else None,
        "share_of_tactic_uses": count / totals[base] if totals[base] else None,
    }
    if include_run:
        row["run_id"] = run_id
    return row


def shannon_entropy(counts: Iterable[int]) -> float | None:
    values = [count for count in counts if count > 0]
    total = sum(values)
    if not total:
        return None
    return -sum((count / total) * math.log2(count / total) for count in values)


def model_summary_rows(
    offers: list[dict[str, Any]], tactics: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for model_id, display in sorted({_group_key(row, False) for row in offers}):
        model_offers = [
            row for row in offers if _group_key(row, False) == (model_id, display)
        ]
        model_tactics = [
            row for row in tactics if _group_key(row, False) == (model_id, display)
        ]
        language = Counter(
            str(row.get("tactic_id"))
            for row in model_tactics
            if row.get("tactic_family") == "language"
        )
        all_counts = Counter(str(row.get("tactic_id")) for row in model_tactics)
        dominant = language.most_common(1)[0] if language else (None, 0)
        rows.append(
            _model_summary_row(
                model_id, display, model_offers, language, all_counts, dominant
            )
        )
    return rows


def _model_summary_row(
    model_id: str,
    display: str,
    offers: list[dict[str, Any]],
    language: Counter[str],
    all_counts: Counter[str],
    dominant: tuple[str | None, int],
) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "model_id": model_id,
        "model_display_name": display,
        "run_count": len({str(row.get("run_id")) for row in offers}),
        "episode_count": len({str(row.get("episode_id")) for row in offers}),
        "offer_count": len(offers),
        "initial_offer_count": sum(bool(row.get("is_initial_offer")) for row in offers),
        "counteroffer_count": sum(
            row.get("event_type") == "TRADE_COUNTERED" for row in offers
        ),
        "accepted_offer_count": sum(
            bool(row.get("is_accepted_offer")) for row in offers
        ),
        "all_tactic_use_count": sum(all_counts.values()),
        "language_tactic_use_count": sum(language.values()),
        "unique_language_tactic_count": len(language),
        "all_tactic_entropy_bits": shannon_entropy(all_counts.values()),
        "language_tactic_entropy_bits": shannon_entropy(language.values()),
        "dominant_language_tactic": dominant[0],
        "dominant_language_tactic_share": dominant[1] / sum(language.values())
        if language
        else None,
    }


def analyze_sources(
    sources: list[str | Path],
    output_dir: Path,
    *,
    board_path: Path = DEFAULT_BOARD_PATH,
    jail_card_value: int = 50,
) -> dict[str, Any]:
    property_values = load_property_values(board_path)
    all_offers: list[dict[str, Any]] = []
    all_episodes: list[dict[str, Any]] = []
    all_warnings: list[str] = []
    source_rows: list[dict[str, Any]] = []
    for source in sources:
        saved_dir, run_dir = resolve_source(source)
        offers, raw_episodes, warnings = extract_episodes(
            run_dir, property_values, jail_card_value
        )
        all_offers.extend(offers)
        all_episodes.extend(finalize_episodes(raw_episodes))
        all_warnings.extend(f"{run_dir.name}: {warning}" for warning in warnings)
        source_rows.append(_source_row(source, saved_dir, run_dir))
    tactics = classify_tactics(all_offers)
    return _write_outputs(
        output_dir,
        all_offers,
        all_episodes,
        tactics,
        source_rows,
        all_warnings,
        board_path,
        jail_card_value,
    )


def _source_row(
    source: str | Path, saved_dir: Path | None, run_dir: Path
) -> dict[str, Any]:
    return {
        "source": str(source),
        "saved_game_dir": str(saved_dir) if saved_dir else None,
        "run_dir": str(run_dir),
        "events_sha256": sha256_file(run_dir / "events.jsonl"),
        "decisions_sha256": sha256_file(run_dir / "decisions.jsonl"),
    }


def _write_outputs(
    output_dir: Path,
    offers: list[dict[str, Any]],
    episodes: list[dict[str, Any]],
    tactics: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    warnings: list[str],
    board_path: Path,
    jail_card_value: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "negotiation_offers.csv", offers)
    write_csv(output_dir / "negotiation_tactics.csv", tactics)
    write_csv(output_dir / "negotiation_episodes.csv", episodes)
    write_csv(
        output_dir / "model_tactic_frequency.csv",
        tactic_frequency_rows(offers, tactics, include_run=False),
    )
    write_csv(
        output_dir / "model_run_tactic_frequency.csv",
        tactic_frequency_rows(offers, tactics, include_run=True),
    )
    write_csv(
        output_dir / "model_negotiation_summary.csv",
        model_summary_rows(offers, tactics),
    )
    write_json(
        output_dir / "negotiation_tactic_codebook.json",
        {
            "schema_version": "v1",
            "analyzer_version": ANALYZER_VERSION,
            "tactics": TACTIC_CODEBOOK,
        },
    )
    manifest = _manifest(
        sources, warnings, board_path, jail_card_value, episodes, offers, tactics
    )
    write_json(output_dir / "manifest.json", manifest)
    return manifest


def _manifest(
    sources: list[dict[str, Any]],
    warnings: list[str],
    board_path: Path,
    jail_card_value: int,
    episodes: list[dict[str, Any]],
    offers: list[dict[str, Any]],
    tactics: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "analyzer_version": ANALYZER_VERSION,
        "sources": sources,
        "board_path": str(board_path.resolve()),
        "board_sha256": sha256_file(board_path),
        "valuation_proxy": {
            "property_value": "board deed price",
            "cash_value": "face value",
            "get_out_of_jail_card_value": jail_card_value,
            "warning": "Concessions are accounting proxies, not continuation-value estimates.",
        },
        "classification_policy": {
            "multi_label": True,
            "public_message_only": True,
            "language_labels_are_review_candidates": True,
            "deception_or_collusion_adjudication": False,
        },
        "counts": {
            "runs": len(sources),
            "episodes": len(episodes),
            "offers": len(offers),
            "tactic_uses": len(tactics),
        },
        "warnings": warnings,
    }


def default_output_dir(sources: list[str]) -> Path:
    if len(sources) != 1:
        raise ValueError("--output-dir is required when analyzing multiple sources")
    saved_dir, run_dir = resolve_source(sources[0])
    if saved_dir is not None:
        return saved_dir / "analysis" / "negotiation"
    return run_dir.parent / f"{run_dir.name}-negotiation-analysis"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract negotiation offers, tactic candidates, frequencies, and episode summaries."
    )
    parser.add_argument(
        "sources",
        nargs="+",
        help="Saved-game names, saved-game directories, or raw run directories.",
    )
    parser.add_argument(
        "--output-dir", type=Path, help="Required when analyzing multiple sources."
    )
    parser.add_argument("--board", type=Path, default=DEFAULT_BOARD_PATH)
    parser.add_argument("--jail-card-value", type=int, default=50)
    args = parser.parse_args()
    output_dir = args.output_dir or default_output_dir(args.sources)
    manifest = analyze_sources(
        args.sources,
        output_dir.resolve(),
        board_path=args.board.resolve(),
        jail_card_value=args.jail_card_value,
    )
    print(
        json.dumps(
            {"output_dir": str(output_dir.resolve()), **manifest["counts"]}, indent=2
        )
    )


if __name__ == "__main__":
    main()
