"""Interpret the author of current and legacy trade offers consistently."""
from typing import Any


def current_offer_author(trade: dict[str, Any]) -> str | None:
    author = trade.get("current_offer", {}).get("from_player_id")
    if isinstance(author, str):
        return author
    initiator, counterparty = trade.get("initiator_player_id"), trade.get("counterparty_player_id")
    history = trade.get("history") or trade.get("history_last_2") or []
    if isinstance(history, list):
        for entry in reversed(history):
            if not isinstance(entry, dict):
                continue
            # The engine moves the previous offer into history on each counter.
            previous_author = entry.get("from_player_id")
            if previous_author == initiator:
                return counterparty if isinstance(counterparty, str) else None
            if previous_author == counterparty:
                return initiator if isinstance(initiator, str) else None
    return initiator if isinstance(initiator, str) else None
