from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BOARD_SPEC_PATH = ROOT / "contracts" / "data" / "board.json"
MICRO_DIR = ROOT / "contracts" / "micro"
SCENARIOS_DIR = MICRO_DIR / "scenarios"
SUITES_DIR = MICRO_DIR / "suites"
RESEARCH_DIR = MICRO_DIR / "research"
SUITE_ID = "micro-v1"

CATEGORY_COUNTS = OrderedDict(
    [
        ("BUY_OR_AUCTION", 20),
        ("AUCTION", 20),
        ("TRADE_PROPOSE", 20),
        ("TRADE_RESPONSE", 10),
        ("BUILD_OR_MORTGAGE", 20),
        ("LIQUIDATION", 10),
        ("JAIL", 15),
        ("POST_TURN_STRATEGY", 15),
    ]
)

PLAYER_NAMES = {"p1": "Alpha", "p2": "Beta", "p3": "Gamma", "p4": "Delta"}
RESEARCH_SOURCES: dict[str, dict[str, str]] = {
    "haliem": {
        "title": "Decision Making in Monopoly using a Hybrid Deep Reinforcement Learning Approach",
        "url": "https://arxiv.org/abs/2103.00683",
        "claim": "Hybrid Monopoly agents combine learned decisions with fixed policies for less frequent buy/trade decisions.",
        "used_for": "Reference-policy and Haliem-style baseline approximations.",
    },
    "wikibooks_strategy": {
        "title": "Monopoly/Strategy - Wikibooks",
        "url": "https://en.wikibooks.org/wiki/Monopoly/Strategy",
        "claim": "Jail traffic raises orange value; railroads are frequent enough to matter; house shortages and hotel conversion affect development strategy.",
        "used_for": "Orange/red traffic, railroad context, house-shortage, and hotel-trap scenarios.",
    },
    "wargamer": {
        "title": "Monopoly rules and how to win - Wargamer",
        "url": "https://www.wargamer.com/monopoly/how-to-win-monopoly",
        "claim": "Early jail slows acquisition; late-game jail can be protective; utilities are often weak.",
        "used_for": "Jail, utility trap, and cash-discipline scenarios.",
    },
    "ultraboardgames": {
        "title": "Winning Monopoly Strategies - UltraBoardGames",
        "url": "https://ultraboardgames.com/monopoly/strategy.php",
        "claim": "Cash reserves should be preserved when developed opponent monopolies exist.",
        "used_for": "Build, mortgage, auction, and liquidation cash thresholds.",
    },
    "sanghyun_markov": {
        "title": "Monopoly Analysis - SangHyun Kim",
        "url": "https://sanghyun-kim.com/monopoly-analysis",
        "claim": "Markov-chain analysis highlights orange traffic and Illinois Avenue as high-probability property decisions.",
        "used_for": "Red/orange and Illinois auction variants.",
    },
    "hasbro_rules": {
        "title": "Monopoly Standard Game Instructions - Hasbro",
        "url": "https://instructions.hasbro.com/en-hk/instruction/monopoly-standard-monopoly",
        "claim": "Official component limits include 32 houses and 12 hotels; auctions, trading, houses, hotels, mortgages, and jail are rule-governed.",
        "used_for": "Legal edge cases, supply limits, and artifact-level rules fidelity.",
    },
    "hasbro_pdf": {
        "title": "MONOPOLY Parker Brothers Real Estate Trading Game Rules",
        "url": "https://www.hasbro.com/common/instruct/Monopoly.pdf",
        "claim": "Jail can result from cards, Go To Jail, or three doubles; the Bank holds deeds, houses, and hotels before purchase.",
        "used_for": "Jail third-turn/card scenarios and official-rule constraints.",
    },
    "monopolyland_rules": {
        "title": "Monopoly Rules: How to Play Monopoly",
        "url": "https://www.monopolyland.com/monopoly-rules/",
        "claim": "Declined property goes to auction; jail options are pay, card, or roll; scarce houses/hotels are auctioned.",
        "used_for": "Buy-or-auction, jail, and house-shortage scenario design.",
    },
    "monopolyland_auction": {
        "title": "Monopoly Auction Rules Explained",
        "url": "https://www.monopolyland.com/monopoly-auction-rules/",
        "claim": "Auction bids can start at any amount, but cash limits and opponent needs should shape bidding strategy.",
        "used_for": "Auction bid sizing, defensive bidding, and overbid traps.",
    },
    "monopolyland_stats": {
        "title": "Monopoly Statistics That Will Help You Win",
        "url": "https://www.monopolyland.com/monopoly-statistics-that-will-help-you-win/",
        "claim": "Jail is the most landed space; Illinois Avenue and New York Avenue are high-probability properties.",
        "used_for": "New York and Illinois acquisition/trade/auction scenarios.",
    },
    "soa_markov": {
        "title": "Actuarial Monopoly - Society of Actuaries",
        "url": "https://www.soa.org/news-and-publications/newsletters/compact/2012/april/actuarial-monopoly.aspx",
        "claim": "Probability modeling explains why orange and red squares receive elevated traffic from Jail.",
        "used_for": "Traffic-based property and jail timing scenarios.",
    },
    "mas275": {
        "title": "MAS275 Probability Modelling Example",
        "url": "https://www.normalesup.org/~stephens/MAS275/monopoly.pdf",
        "claim": "Jail is highly probable and Illinois Avenue is a high-probability property; orange/red groups are relatively high traffic.",
        "used_for": "Illinois, orange/red, and late-game movement-risk scenarios.",
    },
    "quatizer_strategy": {
        "title": "Monopoly Strategy - Quatizer",
        "url": "https://quatizer.com/strateg.html",
        "claim": "Strategic play prioritizes efficient monopolies, development timing, and avoiding cash starvation.",
        "used_for": "Cash discipline, development sequencing, and trade pricing.",
    },
    "house_shortage": {
        "title": "When To Build Houses vs Hotels In Monopoly",
        "url": "https://www.playiro.com/articles/when-to-build-houses-vs-hotels-in-monopoly-the-ultimate-strategy-guide",
        "claim": "Hotels can be a trap when holding houses constrains opponent development.",
        "used_for": "House-shortage and avoid-hotel scenarios.",
    },
    "reddit_house_shortage": {
        "title": "Monopoly house shortage strategy discussion",
        "url": "https://www.reddit.com/r/monopoly/comments/m41qj2",
        "claim": "Experienced players discuss using scarce houses and avoiding hotel conversion to limit opponents.",
        "used_for": "LLM failure traps around hotel upgrades and house supply.",
    },
}


def load_board() -> list[dict[str, Any]]:
    data = json.loads(BOARD_SPEC_PATH.read_text(encoding="utf-8"))
    return [
        {
            "index": space["index"],
            "kind": space["kind"],
            "name": space["name"],
            "group": space["group"],
            "price": space["price"],
            "owner_id": None,
            "mortgaged": False,
            "houses": 0,
            "hotel": False,
        }
        for space in data["spaces"]
    ]


def key(board: list[dict[str, Any]], index: int) -> str:
    return str(board[index]["name"]).replace(" ", "_").replace(".", "").upper()


def set_owned(board: list[dict[str, Any]], owner_id: str, *indices: int, mortgaged: bool = False) -> None:
    for index in indices:
        board[index]["owner_id"] = owner_id
        board[index]["mortgaged"] = mortgaged


def set_houses(board: list[dict[str, Any]], *indices: int, houses: int) -> None:
    for index in indices:
        board[index]["houses"] = houses


def players(cash: dict[str, int], position: dict[str, int], *, in_jail: set[str] | None = None,
            jail_turns: dict[str, int] | None = None, jail_cards: dict[str, int] | None = None) -> list[dict[str, Any]]:
    in_jail = in_jail or set()
    jail_turns = jail_turns or {}
    jail_cards = jail_cards or {}
    return [
        {
            "player_id": player_id,
            "name": PLAYER_NAMES[player_id],
            "cash": cash[player_id],
            "position": position[player_id],
            "in_jail": player_id in in_jail,
            "jail_turns": jail_turns.get(player_id, 0),
            "doubles_count": 0,
            "bankrupt": False,
            "bankrupt_to": None,
            "get_out_of_jail_cards": jail_cards.get(player_id, 0),
        }
        for player_id in ("p1", "p2", "p3", "p4")
    ]


def derived(state: dict[str, Any]) -> dict[str, Any]:
    net: dict[str, int] = {player["player_id"]: int(player["cash"]) for player in state["players"]}
    monopolies: dict[str, list[str]] = {player["player_id"]: [] for player in state["players"]}
    groups: dict[str, list[dict[str, Any]]] = {}
    for space in state["board"]:
        group = space.get("group")
        if group and group not in {"RAILROAD", "UTILITY"}:
            groups.setdefault(group, []).append(space)
        if space.get("owner_id"):
            net[space["owner_id"]] += int(space.get("price") or 0) + int(space.get("houses") or 0) * 50
    for group, spaces in groups.items():
        owners = {space.get("owner_id") for space in spaces}
        if len(owners) == 1 and next(iter(owners)) is not None:
            monopolies[next(iter(owners))].append(group)
    return {"net_worth_estimate_by_player": net, "monopolies_by_player": monopolies}


def state(active: str, turn: int, board: list[dict[str, Any]], ps: list[dict[str, Any]], **extra: Any) -> dict[str, Any]:
    payload = {
        "schema_version": "v1",
        "run_id": "micro-fixture",
        "turn_index": turn,
        "phase": "AWAITING_DECISION",
        "active_player_id": active,
        "players": ps,
        "bank": {"houses_remaining": extra.pop("houses_remaining", 32), "hotels_remaining": extra.pop("hotels_remaining", 12)},
        "board": board,
        "auction": extra.pop("auction", None),
        "trade": extra.pop("trade", None),
    }
    payload["derived"] = derived(payload)
    return payload


def empty_schema() -> dict[str, Any]:
    return {"type": "object", "additionalProperties": False}


def bid_schema() -> dict[str, Any]:
    return {"type": "object", "additionalProperties": False, "required": ["bid_amount"], "properties": {"bid_amount": {"type": "integer", "minimum": 0}}}


def space_schema() -> dict[str, Any]:
    return {"type": "object", "additionalProperties": False, "required": ["space_key"], "properties": {"space_key": {"type": "string"}}}


def bundle_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["cash", "properties", "get_out_of_jail_cards"],
        "properties": {
            "cash": {"type": "integer", "minimum": 0},
            "properties": {"type": "array", "items": {"type": "string"}},
            "get_out_of_jail_cards": {"type": "integer", "minimum": 0},
        },
    }


def trade_schema(include_target: bool) -> dict[str, Any]:
    props = {"offer": bundle_schema(), "request": bundle_schema()}
    req = ["offer", "request"]
    if include_target:
        props["to_player_id"] = {"type": "string"}
        req = ["to_player_id", "offer", "request"]
    return {"type": "object", "additionalProperties": False, "required": req, "properties": props}


def plan_schema(key_name: str) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [key_name],
        "properties": {
            key_name: {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["space_key", "kind", "count"],
                    "properties": {
                        "space_key": {"type": "string"},
                        "kind": {"type": "string", "enum": ["HOUSE", "HOTEL"]},
                        "count": {"type": "integer", "minimum": 1},
                    },
                },
            }
        },
    }


def legal(action: str, schema: dict[str, Any], highlights: list[int] | None = None) -> dict[str, Any]:
    item = {"action": action, "args_schema": schema}
    if highlights:
        item["ui_hints"] = {"highlight_space_indices": highlights}
    return item


def action(
    decision_id: str,
    action_name: str,
    args: dict[str, Any],
    *,
    public: str = "",
    thought: str = "Reference policy follows the scenario rubric.",
) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "decision_id": decision_id,
        "action": action_name,
        "args": args,
        "public_message": public,
        "private_thought": thought,
    }


def decision(decision_id: str, turn: int, decision_type: str, st: dict[str, Any], legal_actions: list[dict[str, Any]], **extra: Any) -> dict[str, Any]:
    payload = {
        "schema_version": "v1",
        "run_id": "micro-fixture",
        "decision_id": decision_id,
        "turn_index": turn,
        "player_id": "p1",
        "decision_type": decision_type,
        "state": st,
        "legal_actions": legal_actions,
    }
    payload.update(extra)
    return payload


def rubric(*items: tuple[str, str, float, dict[str, Any]]) -> dict[str, Any]:
    return {"schema_version": "v1", "scoring_mode": "rubric_v1", "rubric": [
        {"criterion_id": cid, "description": desc, "type": typ, "max_points": pts, "params": params}
        for cid, typ, pts, params, desc in items
    ]}


def scenario_payload(sid: str, category: str, index: int, title: str, description: str, tags: list[str],
                     diff: str, dec: dict[str, Any], evaln: dict[str, Any], ref: dict[str, Any],
                     rationale: str, tension: str, source_keys: list[str], trap: str = "") -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "scenario_id": sid,
        "suite_id": SUITE_ID,
        "category": category,
        "difficulty": diff,
        "title": title,
        "description": description,
        "tags": tags,
        "focal_player_id": "p1",
        "decision_point": dec,
        "evaluation": evaln,
        "reference_policy": {"name": "pro-heuristic-v1", "action": ref, "rationale": rationale},
        "research_sources": [RESEARCH_SOURCES[source_key] for source_key in source_keys],
        "notes": {"strategic_theme": tension, "expected_tension": description, "trap_action": trap},
    }


BUY_CASES = [
    ("buy-or-auction-vermont-light-blue-tempo-01", "Vermont completes light blue while Beta has auction cash", 8, (6, 9), (21, 23), 420, 980, "buy_property", 180, "Buying Vermont completes a cheap high-tempo set; auctioning lets cash-rich Beta steal it.", "start_auction", ["wikibooks_strategy", "soa_markov"], "easy"),
    ("buy-or-auction-connecticut-light-blue-low-buffer-02", "Connecticut completion with only one rent cushion", 9, (6, 8), (14, 15), 310, 760, "buy_property", 120, "Connecticut completes the set and leaves enough cash for ordinary taxes, so the auction risk dominates.", "start_auction", ["quatizer_strategy", "ultraboardgames"], "medium"),
    ("buy-or-auction-new-york-orange-high-traffic-03", "New York closes orange before Gamma exits Jail", 19, (16, 18), (21, 23), 520, 690, "buy_property", 250, "New York is a source-backed high-traffic orange; buying denies an auction to two liquid opponents.", "start_auction", ["monopolyland_stats", "soa_markov"], "medium"),
    ("buy-or-auction-illinois-red-completion-04", "Illinois closes red but Boardwalk is owned by leader", 24, (21, 23), (39,), 610, 830, "buy_property", 350, "Illinois is high probability and completes red; Alpha still keeps a reserve against the leader's dark blue.", "start_auction", ["sanghyun_markov", "mas275"], "medium"),
    ("buy-or-auction-electric-company-cash-danger-05", "Electric Company is tempting but cash is needed for red rent", 12, (5, 15), (21, 23, 24), 145, 740, "start_auction", 140, "Auctioning the utility preserves cash because Beta's red houses make the next lap dangerous.", "buy_property", ["wargamer", "ultraboardgames"], "hard"),
    ("buy-or-auction-water-works-no-utility-synergy-06", "Water Works without Electric Company under cash pressure", 28, (11, 13), (16, 18, 19), 175, 640, "start_auction", 160, "Water Works alone is a low-priority utility and Alpha needs liquidity near orange.", "buy_property", ["wargamer", "quatizer_strategy"], "medium"),
    ("buy-or-auction-reading-first-railroad-07", "Reading Railroad as early bargaining leverage", 5, (6,), (12, 28), 730, 650, "buy_property", 500, "Reading is affordable and railroads are frequent enough to become trade leverage before monopolies form.", "start_auction", ["wikibooks_strategy", "monopolyland_rules"], "easy"),
    ("buy-or-auction-pennsylvania-second-railroad-08", "Second railroad with safe post-buy cash", 15, (5,), (21, 23), 690, 860, "buy_property", 420, "A second railroad doubles railroad rent and keeps a safe cash cushion.", "start_auction", ["wikibooks_strategy", "quatizer_strategy"], "easy"),
    ("buy-or-auction-bo-railroad-cash-rich-opponent-09", "B&O Railroad cannot be auctioned to Delta cheaply", 25, (5, 15), (16, 18), 580, 1220, "buy_property", 340, "Buying prevents the cash leader from assembling three railroads through an auction discount.", "start_auction", ["wikibooks_strategy", "monopolyland_auction"], "medium"),
    ("buy-or-auction-short-line-third-railroad-low-cash-10", "Short Line is a third railroad but Alpha is rent-exposed", 35, (5, 15), (21, 23, 24), 245, 780, "start_auction", 220, "The third railroad is useful, but buying leaves Alpha unable to survive developed red.", "buy_property", ["ultraboardgames", "wikibooks_strategy"], "hard"),
    ("buy-or-auction-kentucky-blocks-beta-red-11", "Kentucky blocks Beta from red monopoly", 21, (16, 18), (23, 24), 460, 980, "buy_property", 220, "Buying Kentucky blocks Beta's red monopoly and preserves enough cash to keep trading.", "start_auction", ["sanghyun_markov", "monopolyland_stats"], "medium"),
    ("buy-or-auction-tennessee-blocks-orange-12", "Tennessee blocks Gamma's orange completion", 18, (21, 23), (16, 19), 390, 880, "buy_property", 200, "Tennessee is a defensive buy: auctioning gives Gamma the strongest traffic set.", "start_auction", ["soa_markov", "wikibooks_strategy"], "medium"),
    ("buy-or-auction-st-charles-low-cost-open-13", "St. Charles early acquisition before trades emerge", 11, (1, 3), (5,), 980, 920, "buy_property", 800, "Early cheap acquisition increases trade optionality and does not threaten liquidity.", "start_auction", ["haliem", "quatizer_strategy"], "easy"),
    ("buy-or-auction-oriental-cheap-builder-14", "Oriental is cheap enough despite no immediate set", 6, (8,), (37, 39), 840, 700, "buy_property", 730, "The low price creates useful trade inventory without delaying later development.", "start_auction", ["haliem", "wargamer"], "easy"),
    ("buy-or-auction-boardwalk-fame-bias-low-cash-15", "Boardwalk fame trap with only $260", 39, (6, 8, 9), (16, 18, 19), 260, 1020, "start_auction", 240, "Boardwalk is famous, but buying it here sacrifices survival against developed orange.", "buy_property", ["wargamer", "ultraboardgames"], "hard"),
    ("buy-or-auction-park-place-no-boardwalk-16", "Park Place without Boardwalk and green rents ahead", 37, (21, 23), (31, 32, 34), 365, 810, "start_auction", 300, "Park Place is speculative without Boardwalk and leaves Alpha short against green.", "buy_property", ["ultraboardgames", "quatizer_strategy"], "hard"),
    ("buy-or-auction-st-james-orange-deny-leader-17", "St. James deny-buy against cash leader", 16, (18,), (19, 24), 450, 1180, "buy_property", 260, "Buying St. James prevents the leader from buying orange cheaply in auction.", "start_auction", ["soa_markov", "monopolyland_auction"], "medium"),
    ("buy-or-auction-virginia-pink-with-trade-path-18", "Virginia creates a pink trade path but not at all costs", 14, (11, 13), (16, 18, 19), 500, 560, "buy_property", 340, "Virginia completes a moderate-cost set while retaining enough cash for orange danger.", "start_auction", ["quatizer_strategy", "ultraboardgames"], "medium"),
    ("buy-or-auction-mediterranean-cheap-but-blocking-19", "Mediterranean blocks Brown completion cheaply", 1, (3,), (6, 8), 620, 820, "buy_property", 560, "The low price and blocking value outweigh the weak rent profile.", "start_auction", ["haliem", "quatizer_strategy"], "easy"),
    ("buy-or-auction-north-carolina-green-caution-20", "North Carolina is expensive with no build cash", 32, (31,), (16, 18, 19), 335, 780, "start_auction", 320, "Green is expensive to develop; auctioning preserves liquidity near built orange.", "buy_property", ["ultraboardgames", "wargamer"], "hard"),
]


def build_buy(i: int) -> dict[str, Any]:
    sid, title, target, alpha_owned, beta_owned, cash, beta_cash, ref_name, min_cash, rationale, trap, sources, diff = BUY_CASES[i - 1]
    board = load_board()
    set_owned(board, "p1", *alpha_owned)
    set_owned(board, "p2", *beta_owned)
    set_owned(board, "p3", 5, 12)
    ps = players({"p1": cash, "p2": beta_cash, "p3": 660, "p4": 720}, {"p1": target, "p2": 21, "p3": 12, "p4": 35})
    st = state("p1", 10 + i, board, ps)
    did = f"{sid}-d1"
    dec = decision(did, 10 + i, "BUY_OR_AUCTION_DECISION", st, [legal("buy_property", empty_schema(), [target]), legal("start_auction", empty_schema(), [target])])
    ref = action(did, ref_name, {}, public="I need to manage the auction risk here.", thought=f"{rationale} Trap action: {trap}. cash monopoly auction opponent")
    rubrics = [("branch", "action_name_is", 0.50, {"action": ref_name}, f"Chooses {ref_name} for this exact purchase/auction context.")]
    if i % 4 == 0:
        rubrics.extend([
            ("cash", "keeps_cash_above", 0.20, {"min_cash": min_cash}, f"Leaves at least ${min_cash} after the action."),
            ("public", "public_message_nonempty", 0.10, {}, "Explains the buy/auction posture publicly without leaking too much."),
            ("thought", "private_thought_mentions", 0.20, {"terms": ["cash", "monopoly", "auction", "opponent", "block"]}, "Private thought names the live strategic pressure."),
        ])
    elif ref_name == "buy_property":
        rubrics.extend([
            ("acceptable_branch", "action_name_in", 0.10, {"actions": ["buy_property"]}, "Stays on the purchase branch when the price is strategically justified."),
            ("cash", "keeps_cash_above", 0.20, {"min_cash": min_cash}, f"Leaves at least ${min_cash} after the action."),
            ("thought", "private_thought_mentions", 0.20, {"terms": ["cash", "monopoly", "auction", "opponent", "block"]}, "Private thought names the live strategic pressure."),
        ])
    else:
        rubrics.extend([
            ("cash", "keeps_cash_above", 0.30, {"min_cash": min_cash}, f"Preserves at least ${min_cash} instead of buying into rent danger."),
            ("thought", "private_thought_mentions", 0.20, {"terms": ["cash", "monopoly", "auction", "opponent", "block"]}, "Private thought names why passing to auction is better here."),
        ])
    return scenario_payload(
        sid, "BUY_OR_AUCTION", i, title,
        f"{title}. {rationale} A shallow policy would choose {trap}; the decisive detail is the current mix of liquidity, opponent cash, and set leverage.",
        ["buy-vs-auction", "cash-discipline", "monopoly-awareness", key(board, target).lower()], diff,
        dec,
        rubric(*rubrics),
        ref, rationale, "Purchase timing, monopoly/blocking value, and liquidity.", sources, trap,
    )


AUCTION_CASES = [
    ("auction-illinois-min-raise-red-completion-01", "Illinois minimum raise for red completion", 24, (21, 23), (16, 18), 430, 221, "bid_auction", 222, 252, "A one-dollar raise contests a high-probability red without burning the reserve.", "overbid_auction", ["sanghyun_markov", "mas275"], "medium"),
    ("auction-new-york-orange-completion-02", "New York bid for orange completion under moderate pressure", 19, (16, 18), (21, 23), 520, 188, "bid_auction", 189, 235, "New York completes the traffic-heavy orange group, but the right bid is controlled.", "drop_out", ["monopolyland_stats", "soa_markov"], "medium"),
    ("auction-tennessee-cheap-steal-03", "Tennessee below face-value steal", 18, (16,), (19, 24), 610, 120, "bid_auction", 121, 170, "The current bid is below face value and supports an orange trade path.", "drop_out", ["soa_markov", "monopolyland_auction"], "easy"),
    ("auction-st-james-defensive-block-04", "St. James defensive block against leader", 16, (21, 23), (18, 19), 470, 165, "bid_auction", 166, 215, "Blocking the leader's orange monopoly is worth a limited defensive bid.", "drop_out", ["wikibooks_strategy", "monopolyland_auction"], "hard"),
    ("auction-boardwalk-overbid-drop-05", "Boardwalk overbid trap while orange is developed", 39, (6, 8, 9), (16, 18, 19), 340, 395, "drop_out", 396, 395, "Boardwalk is famous, but bidding would leave Alpha unable to survive orange rents.", "bid_auction", ["wargamer", "ultraboardgames"], "hard"),
    ("auction-park-place-no-pair-drop-06", "Park Place no-pair overbid", 37, (11, 13, 14), (31, 32), 410, 300, "drop_out", 301, 300, "Park Place without Boardwalk is not worth exhausting cash against green pressure.", "bid_auction", ["ultraboardgames", "quatizer_strategy"], "hard"),
    ("auction-electric-company-utility-overpay-07", "Electric Company utility overpay", 12, (5, 15), (28,), 260, 146, "drop_out", 147, 146, "A utility above face value is a poor use of scarce cash.", "bid_auction", ["wargamer", "monopolyland_auction"], "medium"),
    ("auction-water-works-second-utility-cap-08", "Water Works second utility but cap is reached", 28, (12,), (21, 23, 24), 300, 175, "drop_out", 176, 175, "Owning both utilities helps only modestly and Alpha needs cash against red.", "bid_auction", ["wargamer", "ultraboardgames"], "medium"),
    ("auction-reading-railroad-low-price-09", "Reading Railroad low-price first railroad", 5, (), (16, 18), 760, 82, "bid_auction", 83, 130, "A cheap first railroad is useful income and trade inventory.", "drop_out", ["wikibooks_strategy", "monopolyland_auction"], "easy"),
    ("auction-bo-railroad-third-railroad-10", "B&O as third railroad with safe cash", 25, (5, 15), (21, 23), 620, 230, "bid_auction", 231, 285, "A third railroad is valuable if the bid stays near the current price.", "drop_out", ["wikibooks_strategy", "quatizer_strategy"], "medium"),
    ("auction-kentucky-block-red-11", "Kentucky defensive bid blocks Beta red", 21, (16, 18), (23, 24), 500, 205, "bid_auction", 206, 250, "A bounded bid prevents Beta from completing red cheaply.", "drop_out", ["sanghyun_markov", "monopolyland_stats"], "medium"),
    ("auction-indiana-leader-threat-12", "Indiana leader-threat overbid discipline", 23, (21,), (24,), 295, 268, "drop_out", 269, 268, "The leader wants red, but Alpha cannot afford to bluff beyond survival cash.", "bid_auction", ["monopolyland_auction", "ultraboardgames"], "hard"),
    ("auction-virginia-pink-midgame-13", "Virginia midgame value bid", 14, (11, 13), (16, 18, 19), 570, 160, "bid_auction", 161, 205, "Completing pink is less glamorous but affordable and developable.", "drop_out", ["quatizer_strategy", "haliem"], "medium"),
    ("auction-pacific-green-too-expensive-14", "Pacific expensive green caution", 31, (32,), (16, 18, 19), 360, 240, "drop_out", 241, 240, "Green development costs are too high when orange danger is immediate.", "bid_auction", ["ultraboardgames", "wargamer"], "hard"),
    ("auction-oriental-light-blue-cheap-block-15", "Oriental cheap block and trade inventory", 6, (8,), (9,), 690, 74, "bid_auction", 75, 125, "The bid is cheap enough to block light-blue completion and create trade value.", "drop_out", ["haliem", "quatizer_strategy"], "easy"),
    ("auction-mediterranean-brown-ignore-war-16", "Mediterranean auction war is not worth it", 1, (3,), (6, 8, 9), 235, 118, "drop_out", 119, 118, "Brown completion is cheap, but not worth a war while Alpha faces built light blue.", "bid_auction", ["ultraboardgames", "quatizer_strategy"], "medium"),
    ("auction-pennsylvania-railroad-force-price-17", "Pennsylvania Railroad force-price bluff", 15, (5,), (25, 35), 680, 198, "bid_auction", 199, 240, "A controlled bid makes Delta pay for railroad consolidation if Alpha loses.", "drop_out", ["monopolyland_auction", "wikibooks_strategy"], "medium"),
    ("auction-short-line-cash-leader-trap-18", "Short Line cash leader can call the bluff", 35, (5, 15), (25,), 275, 260, "drop_out", 261, 260, "The cash leader can call any bluff and Alpha's reserve is too thin.", "bid_auction", ["monopolyland_auction", "ultraboardgames"], "hard"),
    ("auction-states-avenue-positive-but-not-critical-19", "States Avenue positive but noncritical bid", 13, (11,), (31, 32), 640, 112, "bid_auction", 113, 160, "A modest bid improves pink leverage without compromising cash.", "drop_out", ["haliem", "quatizer_strategy"], "easy"),
    ("auction-marvin-gardens-yellow-overstretch-20", "Marvin Gardens completes yellow but no build cash", 29, (26, 27), (16, 18, 19), 315, 282, "drop_out", 283, 282, "Completing yellow is not enough if the winning bid leaves no development or rent defense cash.", "bid_auction", ["ultraboardgames", "wargamer"], "hard"),
]


def build_auction(i: int) -> dict[str, Any]:
    sid, title, target, alpha_owned, beta_owned, cash, current_bid, ref_name, min_bid, max_bid, rationale, trap, sources, diff = AUCTION_CASES[i - 1]
    board = load_board()
    set_owned(board, "p1", *alpha_owned)
    set_owned(board, "p2", *beta_owned)
    set_owned(board, "p3", 12, 28)
    ps = players({"p1": cash, "p2": 720, "p3": 850, "p4": 540}, {"p1": target, "p2": 24, "p3": 12, "p4": 35})
    auc = {"property_space_key": key(board, target), "current_high_bid": current_bid, "current_leader_player_id": "p2", "active_bidders_player_ids": ["p1", "p2", "p4"], "current_bidder_player_id": "p1", "initiator_player_id": "p3", "action_count": 3 + i, "history": [{"index": 1, "action": "BID", "player_id": "p2", "bid_amount": current_bid}]}
    st = state("p1", 40 + i, board, ps, auction=auc)
    did = f"{sid}-d1"
    dec = decision(did, 40 + i, "AUCTION_BID_DECISION", st, [legal("bid_auction", bid_schema(), [target]), legal("drop_out", empty_schema(), [target])])
    args = {"bid_amount": min_bid} if ref_name == "bid_auction" else {}
    ref = action(did, ref_name, args, public="I will keep this auction disciplined.", thought=f"{rationale} Trap action: {trap}. bid cash block overbid")
    rubric_items = [("branch", "action_name_is", 0.50, {"action": ref_name}, f"Chooses {ref_name} for this auction state.")]
    if ref_name == "bid_auction":
        rubric_items.extend([("minimum", "bid_at_least", 0.20, {"min": min_bid}, "Bid clears the current leader."), ("cap", "bid_at_most", 0.20, {"max": max_bid}, "Bid stays below the scenario cap.")])
        if i % 5 == 0:
            rubric_items.append(("public", "public_message_nonempty", 0.05, {}, "Signals auction discipline without revealing the exact cap."))
    else:
        rubric_items.append(("cash", "keeps_cash_above", 0.30, {"min_cash": cash - current_bid}, "Dropping preserves the unsafe post-bid cash reserve."))
        if i % 4 == 0:
            rubric_items.append(("discipline", "action_name_in", 0.05, {"actions": ["drop_out"]}, "Declines the bluff when the cash leader can punish it."))
    rubric_items.append(("thought", "private_thought_mentions", 0.10 if len(rubric_items) < 4 else 0.05, {"terms": ["bid", "cash", "block", "overbid", "leader"]}, "Private thought mentions the auction pressure."))
    return scenario_payload(
        sid, "AUCTION", i, title,
        f"{title}. {rationale} The hard part is resisting {trap} when monopoly potential and cash survival point in opposite directions.",
        ["auction", "bid-discipline", key(board, target).lower()], diff, dec, rubric(*rubric_items), ref,
        rationale, "Auction value, blocking pressure, and bid discipline.", sources, trap,
    )


TRADE_PROPOSE_CASES = [
    ("trade-propose-water-works-for-new-york-01", "Offer Water Works and cash for New York", (16, 18, 28), (19, 12), "p2", 28, 19, 140, "Orange completion is worth a surplus utility and moderate cash.", ["monopolyland_stats", "soa_markov"], "medium"),
    ("trade-propose-reading-for-tennessee-02", "Use Reading Railroad to unlock orange", (16, 19, 5), (18, 15), "p2", 5, 18, 90, "Railroad income is useful but orange completion is stronger.", ["wikibooks_strategy", "soa_markov"], "medium"),
    ("trade-propose-jail-card-for-st-james-03", "Spend jail card as orange sweetener", (18, 19), (16,), "p2", None, 16, 120, "A jail card plus cash can make the orange-completion offer plausible.", ["wargamer", "monopolyland_rules"], "hard"),
    ("trade-propose-red-indiana-for-kentucky-04", "Request Kentucky without giving Beta orange", (23, 24, 12), (21, 16), "p2", 12, 21, 110, "Red completion is strong, but the offer avoids giving orange completion back.", ["sanghyun_markov", "ultraboardgames"], "medium"),
    ("trade-propose-red-block-with-railroad-05", "Offer B&O for Indiana to block red split", (21, 24, 25), (23, 35), "p2", 25, 23, 60, "The railroad sweetener is acceptable because Indiana completes red.", ["wikibooks_strategy", "mas275"], "medium"),
    ("trade-propose-mutual-orange-vs-yellow-06", "Mutual monopoly trade where Alpha can build first", (16, 18, 26), (19, 27, 29), "p2", 26, 19, 0, "Alpha can build orange immediately while Beta's yellow build cash is weak.", ["soa_markov", "ultraboardgames"], "hard"),
    ("trade-propose-mutual-red-vs-green-07", "Mutual trade only with cash compensation", (21, 23, 31), (24, 32, 34), "p2", 31, 24, 260, "Green is expensive; Alpha should demand cash while completing red.", ["ultraboardgames", "sanghyun_markov"], "hard"),
    ("trade-propose-no-good-trade-boardwalk-08", "Greedy Boardwalk ask should be softened", (37, 12), (39, 16, 18), "p2", 12, 39, 300, "A raw utility-for-Boardwalk ask is unrealistic; cash must be meaningful.", ["wargamer", "quatizer_strategy"], "hard"),
    ("trade-propose-cash-poor-beta-orange-09", "Cash-poor Beta needs liquidity for New York", (16, 18, 5), (19,), "p2", 5, 19, 220, "Beta is cash-poor, so the cash sweetener matters more than face value.", ["ultraboardgames", "monopolyland_stats"], "medium"),
    ("trade-propose-cash-poor-gamma-red-10", "Cash-poor Gamma sells Illinois only for liquidity", (21, 23, 28), (24,), "p3", 28, 24, 240, "The cash-poor counterparty makes a utility-plus-cash structure plausible.", ["sanghyun_markov", "ultraboardgames"], "medium"),
    ("trade-propose-railroad-swap-for-light-blue-11", "Railroad swap to complete light blue", (6, 9, 15), (8, 25), "p2", 15, 8, 30, "A railroad swap plus small cash completes a cheap set without creating opponent monopoly.", ["wikibooks_strategy", "haliem"], "easy"),
    ("trade-propose-jail-card-late-safety-for-red-12", "Late jail card sweetener for red", (21, 23), (24,), "p2", None, 24, 160, "A jail card has late-game value and can close the red deal.", ["wargamer", "hasbro_pdf"], "hard"),
    ("trade-propose-defensive-deny-green-13", "Do not give green completion for weak pink gain", (11, 13, 31), (14, 32, 34), "p2", 31, 14, 40, "Alpha can ask for Virginia, but giving Pacific would hand Beta a stronger green monopoly.", ["ultraboardgames", "quatizer_strategy"], "hard"),
    ("trade-propose-utility-package-for-railroad-14", "Package both utilities for Pennsylvania Railroad", (12, 28), (15,), "p2", 12, 15, 35, "Both utilities can be surplus before monopolies form; railroad rent is steadier.", ["wargamer", "wikibooks_strategy"], "medium"),
    ("trade-propose-politically-risky-leader-message-15", "Political offer to slow the leader", (16, 18, 5), (19,), "p4", 5, 19, 180, "A public anti-leader frame helps make the orange-completion trade plausible.", ["monopolyland_auction", "soa_markov"], "hard"),
    ("trade-propose-dark-blue-fame-trap-16", "Boardwalk ask must not overpay with orange", (16, 18, 19), (39,), "p2", 16, 39, 0, "Trading away orange for Boardwalk is a fame-bias trap unless compensation is huge.", ["wargamer", "ultraboardgames"], "hard"),
    ("trade-propose-yellow-build-race-17", "Complete yellow only with retained build cash", (26, 27, 12), (29,), "p2", 12, 29, 80, "Yellow can work if Alpha keeps enough cash to build afterward.", ["ultraboardgames", "quatizer_strategy"], "medium"),
    ("trade-propose-pink-cheap-development-18", "Complete pink using small railroad sweetener", (11, 13, 5), (14,), "p3", 5, 14, 50, "Pink is developable and the offer is small enough not to overpay.", ["haliem", "quatizer_strategy"], "easy"),
    ("trade-propose-brown-fast-build-19", "Complete brown only as cheap side plan", (1, 5), (3,), "p2", 5, 3, 20, "Brown is weak but cheap; the offer must remain tiny.", ["quatizer_strategy", "haliem"], "easy"),
    ("trade-propose-orange-no-reveal-public-20", "Orange completion with non-revealing public message", (16, 18, 28), (19,), "p2", 28, 19, 170, "The model should privately identify orange value without publicly revealing desperation.", ["soa_markov", "wargamer"], "hard"),
]


def build_trade_propose(i: int) -> dict[str, Any]:
    sid, title, alpha_owned, target_owned, to_player, offer_index, request_index, cash_offer, rationale, sources, diff = TRADE_PROPOSE_CASES[i - 1]
    board = load_board()
    set_owned(board, "p1", *alpha_owned)
    set_owned(board, to_player, *target_owned)
    set_owned(board, "p3", 6, 8, 9)
    ps = players({"p1": 560, "p2": 260 if "cash-poor" in sid else 720, "p3": 480, "p4": 980}, {"p1": 20, "p2": 19, "p3": 9, "p4": 39}, jail_cards={"p1": 1 if offer_index is None else 0})
    st = state("p1", 70 + i, board, ps)
    did = f"{sid}-d1"
    dec = decision(did, 70 + i, "TRADE_PROPOSE_DECISION", st, [legal("propose_trade", trade_schema(True))], post_turn={"options": {"can_trade_with": ["p2", "p3", "p4"], "max_trade_exchanges": 4, "mortgageable_space_indices": [idx for idx in alpha_owned if idx in {5, 12, 15, 25, 28, 35}], "unmortgageable_space_indices": [], "buildable_space_indices": [], "sellable_building_space_indices": []}})
    offer_props = [] if offer_index is None else [key(board, offer_index)]
    args = {"to_player_id": to_player, "offer": {"cash": cash_offer, "properties": offer_props, "get_out_of_jail_cards": 1 if offer_index is None else 0}, "request": {"cash": 0, "properties": [key(board, request_index)], "get_out_of_jail_cards": 0}}
    ref = action(did, "propose_trade", args, public="This gives both of us a useful path without overcommitting.", thought=f"{rationale} trade monopoly cash opponent public")
    rubrics = [
        ("target", "trade_target_is", 0.18, {"player_id": to_player}, "Targets the player who owns the requested asset."),
        ("request", "trade_request_contains_property", 0.24, {"space_key": key(board, request_index)}, "Requests the strategically relevant property."),
    ]
    if offer_props:
        rubrics.append(("offer_asset", "trade_offer_contains_property", 0.16, {"space_key": offer_props[0]}, "Includes the intended bargaining chip instead of a random asset."))
        rubrics.append(("cash", "trade_offer_cash_between", 0.17, {"min": max(0, cash_offer - 60), "max": cash_offer + 80}, "Uses a plausible cash range."))
    elif "jail" in sid:
        rubrics.append(("card", "arg_equals", 0.16, {"key": "offer", "value": args["offer"]}, "Packages the jail card exactly as the late/tempo sweetener."))
        rubrics.append(("cash", "trade_offer_cash_between", 0.17, {"min": max(0, cash_offer - 60), "max": cash_offer + 80}, "Adds enough cash to make the card offer plausible."))
    else:
        rubrics.append(("cash", "trade_offer_cash_between", 0.24, {"min": max(0, cash_offer - 60), "max": cash_offer + 80}, "Uses cash discipline instead of overpaying with a core property."))
    if "no-reveal" in sid or "politically" in sid:
        rubrics.append(("public", "public_message_nonempty", 0.16, {}, "Uses a deliberate public message for negotiation framing."))
    else:
        rubrics.append(("thought", "private_thought_mentions", 0.16, {"terms": ["trade", "monopoly", "cash", "opponent", "orange", "red"]}, "Private thought names the real strategic goal."))
    rubrics.append(("discipline", "private_thought_mentions", 0.10, {"terms": ["trade", "cash", "public", "opponent"]}, "Private thought shows price/message discipline."))
    return scenario_payload(
        sid, "TRADE_PROPOSE", i, title,
        f"{title}. {rationale} The offer has to be credible to the counterparty while preserving Alpha's actual strategic edge.",
        ["trade", "negotiation", "monopoly-awareness"], diff, dec,
        rubric(*rubrics),
        ref, rationale, "Trade structure, plausibility, and private/public message discipline.", sources, "greedy_unacceptable_trade",
    )


TRADE_RESPONSE_CASES = [
    ("trade-response-accept-orange-for-utility-01", "Accept New York for utility and cash", 19, "accept_trade", {}, "Accept because Alpha completes orange and only gives surplus utility value.", ["monopolyland_stats", "wargamer"], "easy"),
    ("trade-response-accept-red-with-cash-02", "Accept Illinois with enough cash paid out", 24, "accept_trade", {}, "Accept because red completion outweighs the moderate cash concession.", ["sanghyun_markov", "mas275"], "medium"),
    ("trade-response-accept-liquidity-saving-03", "Accept liquidity-saving railroad sale", 15, "accept_trade", {}, "Accept because cash prevents liquidation without creating an opponent monopoly.", ["ultraboardgames", "wikibooks_strategy"], "medium"),
    ("trade-response-reject-beta-orange-04", "Reject offer handing Beta orange", 16, "reject_trade", {}, "Reject because the face-value gain gives Beta the stronger orange monopoly.", ["soa_markov", "ultraboardgames"], "hard"),
    ("trade-response-reject-leader-red-05", "Reject leader's red-completion offer", 21, "reject_trade", {}, "Reject because the current leader gets red for too little cash.", ["sanghyun_markov", "monopolyland_stats"], "hard"),
    ("trade-response-reject-boardwalk-bait-06", "Reject Boardwalk bait for orange", 39, "reject_trade", {}, "Reject because Boardwalk fame does not justify surrendering orange.", ["wargamer", "ultraboardgames"], "hard"),
    ("trade-response-counter-mutual-monopoly-cash-07", "Counter mutual monopoly with higher cash", 24, "counter_trade", {"offer": {"cash": 0, "properties": ["KENTUCKY_AVENUE"], "get_out_of_jail_cards": 0}, "request": {"cash": 250, "properties": ["ILLINOIS_AVENUE"], "get_out_of_jail_cards": 0}}, "Counter because mutual monopolies require cash compensation for Alpha's faster build path.", ["ultraboardgames", "haliem"], "hard"),
    ("trade-response-counter-jail-card-value-08", "Counter for jail card value late", 19, "counter_trade", {"offer": {"cash": 40, "properties": [], "get_out_of_jail_cards": 0}, "request": {"cash": 0, "properties": ["NEW_YORK_AVENUE"], "get_out_of_jail_cards": 1}}, "Counter because the jail card has late-game safety value in addition to New York.", ["wargamer", "hasbro_pdf"], "hard"),
    ("trade-response-reject-face-value-positive-09", "Reject face-value-positive green trap", 31, "reject_trade", {}, "Reject because the apparent property-value gain gives Beta an immediately buildable green monopoly.", ["ultraboardgames", "quatizer_strategy"], "hard"),
    ("trade-response-accept-pink-build-window-10", "Accept pink completion with build window", 14, "accept_trade", {}, "Accept because pink can be built cheaply while opponents lack complete sets.", ["haliem", "quatizer_strategy"], "medium"),
]


def build_trade_response(i: int) -> dict[str, Any]:
    sid, title, focal_prop, ref_name, ref_args, rationale, sources, diff = TRADE_RESPONSE_CASES[i - 1]
    board = load_board()
    set_owned(board, "p1", 16, 18, 21, 23, 11, 13)
    set_owned(board, "p2", 19, 24, 31, 32, 39)
    offered = {"cash": 120, "properties": [key(board, focal_prop)], "get_out_of_jail_cards": 1 if "jail" in sid else 0}
    requested = {"cash": 0, "properties": [key(board, 16)] if ref_name.startswith("reject") else [key(board, 12)], "get_out_of_jail_cards": 0}
    ps = players({"p1": 430, "p2": 760, "p3": 400, "p4": 900}, {"p1": 20, "p2": focal_prop, "p3": 9, "p4": 39}, jail_cards={"p2": 1 if "jail" in sid else 0})
    tr = {"initiator_player_id": "p2", "counterparty_player_id": "p1", "max_exchanges": 4, "exchange_index": min(i, 3), "history_last_2": [], "history": [], "current_offer": {"offer": offered, "request": requested}}
    st = state("p1", 80 + i, board, ps, trade=tr)
    did = f"{sid}-d1"
    dec = decision(did, 80 + i, "TRADE_RESPONSE_DECISION", st, [legal("accept_trade", empty_schema()), legal("reject_trade", empty_schema()), legal("counter_trade", trade_schema(False))])
    ref = action(did, ref_name, ref_args, public="I need better balance on this deal." if ref_name == "counter_trade" else "", thought=f"{rationale} trade opponent monopoly cash")
    rubrics = [("branch", "action_name_is", 0.55, {"action": ref_name}, f"Chooses {ref_name} for this offer.")]
    if ref_name == "counter_trade":
        rubrics.extend([
            ("counter_request", "trade_request_contains_property", 0.18, {"space_key": ref_args["request"]["properties"][0]}, "Counteroffer requests the missing strategic asset."),
            ("counter_cash", "trade_request_cash_between", 0.12, {"min": 0, "max": max(300, int(ref_args["request"].get("cash", 0)) + 80)}, "Counter cash/request shape stays within a plausible range."),
            ("public", "public_message_nonempty", 0.15, {}, "Uses public message when negotiating/countering."),
        ])
    elif ref_name == "accept_trade":
        rubrics.extend([
            ("safe_branch", "action_name_in", 0.15, {"actions": ["accept_trade"]}, "Accepts because this specific offer improves Alpha's development/liquidity window."),
            ("thought", "private_thought_mentions", 0.20, {"terms": ["trade", "monopoly", "cash", "liquidity", "build"]}, "Private thought identifies why accepting is not just face-value chasing."),
            ("message_ok", "action_name_is", 0.10, {"action": "accept_trade"}, "No counter-message is required for a clean accept."),
        ])
    else:
        rubrics.extend([
            ("reject_branch", "action_name_in", 0.15, {"actions": ["reject_trade"]}, "Rejects the opponent-favoring monopoly or fame-bait offer."),
            ("thought", "private_thought_mentions", 0.20, {"terms": ["trade", "opponent", "monopoly", "cash", "leader"]}, "Private thought identifies trade risk."),
            ("no_public_needed", "action_name_is", 0.10, {"action": "reject_trade"}, "Rejecting directly is better than negotiating a bad frame."),
        ])
    return scenario_payload(
        sid, "TRADE_RESPONSE", i, title,
        f"{title}. {rationale} The decision turns on monopoly timing and opponent threat, not printed property price.",
        ["trade-response", "opponent-risk", "monopoly-awareness"], diff,
        dec,
        rubric(*rubrics),
        ref, rationale, "Trade response under asymmetric monopoly value.", sources, "face_value_only_trade_eval",
    )


BUILD_CASES = [
    ("build-orange-third-house-st-james-01", "Build St. James to the three-house breakpoint", (16, 18, 19), 2, 310, "build_houses_or_hotel", 16, "Orange at three houses is the core pressure point and Alpha can still keep rent cash.", ["soa_markov", "ultraboardgames"], "medium"),
    ("build-orange-third-house-tennessee-02", "Build Tennessee before Beta passes Jail", (16, 18, 19), 2, 280, "build_houses_or_hotel", 18, "Opponent position makes an immediate orange build stronger than waiting.", ["monopolyland_stats", "soa_markov"], "medium"),
    ("build-orange-third-house-new-york-03", "Build New York while houses remain", (16, 18, 19), 2, 350, "build_houses_or_hotel", 19, "New York's traffic justifies the third house while supply is available.", ["monopolyland_stats", "wikibooks_strategy"], "easy"),
    ("build-orange-mortgage-utility-to-build-04", "Mortgage utility to fund orange build", (16, 18, 19), 2, 70, "mortgage_property", 12, "Mortgaging Electric Company preserves the orange build plan better than ending flat-footed.", ["wargamer", "ultraboardgames"], "hard"),
    ("build-red-third-house-kentucky-05", "Build Kentucky to red three-house breakpoint", (21, 23, 24), 2, 390, "build_houses_or_hotel", 21, "Red is high traffic enough to justify immediate development.", ["sanghyun_markov", "mas275"], "medium"),
    ("build-red-third-house-illinois-06", "Build Illinois before Gamma reaches red", (21, 23, 24), 2, 360, "build_houses_or_hotel", 24, "Illinois has strong landing probability and Gamma is approaching.", ["sanghyun_markov", "monopolyland_stats"], "medium"),
    ("build-red-cash-caution-end-07", "Do not build red with $95 reserve", (21, 23, 24), 1, 95, "end_turn", None, "A red house is tempting, but cash reserve is too low against built orange.", ["ultraboardgames", "wargamer"], "hard"),
    ("build-light-blue-cheap-tempo-08", "Cheap light-blue build with safe reserve", (6, 8, 9), 1, 420, "build_houses_or_hotel", 8, "Light-blue houses are cheap and Alpha can build without cash danger.", ["haliem", "quatizer_strategy"], "easy"),
    ("build-light-blue-last-cheap-house-09", "Take the cheap light-blue house before shortage", (6, 8, 9), 2, 290, "build_houses_or_hotel", 9, "A cheap house also tightens the remaining house supply.", ["hasbro_rules", "wikibooks_strategy"], "medium"),
    ("build-yellow-expensive-caution-10", "End turn instead of overbuilding yellow", (26, 27, 29), 1, 180, "end_turn", None, "Yellow houses are expensive and the reserve would be unsafe.", ["ultraboardgames", "quatizer_strategy"], "hard"),
    ("build-green-expensive-caution-11", "Do not build green while cash-poor", (31, 32, 34), 1, 210, "end_turn", None, "Green requires too much capital when opponents have orange threats.", ["ultraboardgames", "wargamer"], "hard"),
    ("build-house-shortage-hold-four-12", "Hold four houses instead of hotel", (16, 18, 19), 4, 520, "end_turn", None, "Upgrading to hotel releases houses and weakens Alpha's house-shortage leverage.", ["house_shortage", "reddit_house_shortage"], "hard"),
    ("build-house-shortage-avoid-hotel-red-13", "Avoid red hotel during shortage", (21, 23, 24), 4, 610, "end_turn", None, "Four-house red constrains opponents; hotel conversion is the trap.", ["hasbro_rules", "wikibooks_strategy"], "hard"),
    ("build-last-houses-orange-14", "Buy scarce orange houses before opponent can build", (16, 18, 19), 2, 460, "build_houses_or_hotel", 16, "Taking scarce houses now limits the opponent's yellow development.", ["hasbro_rules", "house_shortage"], "hard"),
    ("build-mortgage-railroad-for-red-15", "Mortgage railroad to reach red build cash", (21, 23, 24), 2, 115, "mortgage_property", 5, "A non-core railroad mortgage is worth a red house breakpoint.", ["wikibooks_strategy", "ultraboardgames"], "medium"),
    ("build-mortgage-utility-for-light-blue-16", "Mortgage utility for light-blue pressure", (6, 8, 9), 2, 65, "mortgage_property", 12, "Utility mortgage funds cheap houses without breaking the set.", ["wargamer", "quatizer_strategy"], "medium"),
    ("build-preserve-cash-vs-boardwalk-17", "End turn to preserve Boardwalk survival cash", (16, 18, 19), 2, 155, "end_turn", None, "Alpha is near dark blue and should not spend the rent cushion.", ["ultraboardgames", "wargamer"], "hard"),
    ("build-opponent-position-orange-now-18", "Build orange before Delta is seven away", (16, 18, 19), 1, 450, "build_houses_or_hotel", 19, "Opponent position creates immediate rent opportunity.", ["soa_markov", "monopolyland_stats"], "medium"),
    ("build-pink-cheap-two-houses-19", "Build pink modestly with safe cash", (11, 13, 14), 1, 370, "build_houses_or_hotel", 14, "Pink is not top tier, but cheap development is efficient here.", ["haliem", "quatizer_strategy"], "easy"),
    ("build-dark-blue-hotel-fame-trap-20", "Avoid dark-blue hotel while houses scarce", (37, 39), 4, 700, "end_turn", None, "Hotel fame is less valuable than holding houses and cash in this state.", ["house_shortage", "wargamer"], "hard"),
]


def build_build(i: int) -> dict[str, Any]:
    sid, title, group_indices, house_count, cash, ref_name, target_index, rationale, sources, diff = BUILD_CASES[i - 1]
    board = load_board()
    set_owned(board, "p1", *group_indices, 12, 5)
    set_owned(board, "p2", 21, 23, 24 if group_indices != (21, 23, 24) else 16)
    set_houses(board, *group_indices, houses=house_count)
    ps = players({"p1": cash, "p2": 640, "p3": 350, "p4": 1020}, {"p1": 20, "p2": 24, "p3": 39, "p4": 25})
    st = state("p1", 100 + i, board, ps, houses_remaining=4 if "shortage" in sid or "last-houses" in sid else 18)
    did = f"{sid}-d1"
    mortgageable = [12, 5]
    dec = decision(did, 100 + i, "POST_TURN_ACTION_DECISION", st, [legal("build_houses_or_hotel", plan_schema("build_plan"), list(group_indices)), legal("mortgage_property", space_schema(), mortgageable), legal("end_turn", empty_schema())], post_turn={"options": {"can_trade_with": ["p2", "p3", "p4"], "max_trade_exchanges": 4, "mortgageable_space_indices": mortgageable, "unmortgageable_space_indices": [], "buildable_space_indices": list(group_indices), "sellable_building_space_indices": list(group_indices)}})
    args = {}
    if ref_name == "build_houses_or_hotel":
        args = {"build_plan": [{"space_key": key(board, target_index), "kind": "HOUSE", "count": 1}]}
    elif ref_name == "mortgage_property":
        args = {"space_key": key(board, target_index)}
    ref = action(did, ref_name, args, thought=f"{rationale} build cash houses hotel mortgage")
    rubrics = [("branch", "action_name_is", 0.55, {"action": ref_name}, f"Chooses {ref_name} for this build/mortgage decision.")]
    if ref_name == "build_houses_or_hotel":
        rubrics.extend([("group", "builds_on_group", 0.25, {"space_keys": [key(board, idx) for idx in group_indices]}, "Builds on the intended color group."), ("count", "build_count_between", 0.10, {"min": 1, "max": 2}, "Builds incrementally.")])
    elif ref_name == "mortgage_property":
        rubrics.append(("mortgage", "mortgages_space", 0.30, {"space_key": key(board, target_index)}, "Mortgages the intended non-core asset."))
    else:
        rubrics.append(("cash", "keeps_cash_above", 0.30, {"min_cash": 150}, "Preserves cash instead of overdeveloping."))
    rubrics.append(("thought", "private_thought_mentions", 0.10, {"terms": ["build", "cash", "houses", "hotel", "mortgage"]}, "Private thought names the build constraint."))
    return scenario_payload(
        sid, "BUILD_OR_MORTGAGE", i, title,
        f"{title}. {rationale} The decision depends on house supply, immediate rent threat, and whether the reserve survives the build.",
        ["build", "mortgage", "three-house", "house-shortage"], diff, dec, rubric(*rubrics), ref,
        rationale, "Development timing, cash reserve, and house-supply constraints.", sources, "generic_build_heuristic",
    )


LIQUIDATION_CASES = [
    ("liquidation-mortgage-electric-before-orange-01", "Mortgage Electric before selling orange houses", "mortgage_property", 12, 95, "p2", "Small shortfall can be covered by utility mortgage while preserving orange.", ["wargamer", "ultraboardgames"], "medium"),
    ("liquidation-mortgage-reading-before-red-02", "Mortgage Reading before tearing down red", "mortgage_property", 5, 130, "p2", "Railroad mortgage preserves three-house red pressure.", ["wikibooks_strategy", "ultraboardgames"], "medium"),
    ("liquidation-mortgage-water-works-bank-debt-03", "Mortgage Water Works for bank debt", "mortgage_property", 28, 80, None, "Owed to bank is less dangerous than transferring assets to a player, so preserve houses.", ["hasbro_rules", "ultraboardgames"], "easy"),
    ("liquidation-sell-one-orange-evenly-04", "Sell one orange house when mortgages are insufficient", "sell_houses_or_hotel", 16, 260, "p2", "Mortgage value is insufficient; sell evenly and keep the monopoly alive.", ["hasbro_rules", "monopolyland_rules"], "hard"),
    ("liquidation-sell-red-house-not-core-railroad-05", "Sell red house after non-core mortgages exhausted", "sell_houses_or_hotel", 21, 290, "p3", "The legal sale is painful but better than bankruptcy to Gamma.", ["hasbro_pdf", "ultraboardgames"], "hard"),
    ("liquidation-bankruptcy-unavoidable-bank-06", "Bankruptcy unavoidable to bank", "declare_bankruptcy", None, 1400, None, "No legal liquidation can cover the bank debt.", ["hasbro_rules", "monopolyland_rules"], "hard"),
    ("liquidation-bankruptcy-unavoidable-player-07", "Bankruptcy unavoidable to player", "declare_bankruptcy", None, 1650, "p2", "Even selling buildings cannot cover rent owed to Beta.", ["hasbro_pdf", "monopolyland_rules"], "hard"),
    ("liquidation-mortgaged-interest-edge-08", "Mortgage unmortgaged railroad instead of already mortgaged utility", "mortgage_property", 15, 110, "p2", "The utility is already mortgaged, so the railroad is the clean legal source.", ["hasbro_rules", "wikibooks_strategy"], "medium"),
    ("liquidation-preserve-monopoly-survival-09", "Break a weak asset before monopoly houses", "mortgage_property", 25, 180, "p4", "Preserve the developed monopoly even though mortgaging railroad income hurts.", ["ultraboardgames", "quatizer_strategy"], "medium"),
    ("liquidation-sell-hotel-house-shortage-10", "Sell hotel only when no mortgage path covers debt", "sell_houses_or_hotel", 39, 500, "p2", "Debt is large enough that hotel sale is necessary despite releasing house supply.", ["hasbro_rules", "house_shortage"], "hard"),
]


def build_liquidation(i: int) -> dict[str, Any]:
    sid, title, ref_name, target_index, shortfall, owed_to, rationale, sources, diff = LIQUIDATION_CASES[i - 1]
    board = load_board()
    base_assets = [16, 18, 19, 21, 23, 24, 12, 28, 5, 15, 25, 37, 39]
    variant_assets = {
        1: [16, 18, 19, 12, 5],
        2: [21, 23, 24, 5, 15],
        3: [16, 18, 19, 28, 25],
        4: [16, 18, 19, 12, 28, 5],
        5: [21, 23, 24, 15, 25],
        6: [37, 39, 12, 28],
        7: [16, 18, 19, 21, 23, 24, 5],
        8: [12, 15, 25, 28, 16, 18, 19],
        9: [16, 18, 19, 25, 37],
        10: [37, 39, 5, 15, 25],
    }
    owned_assets = variant_assets.get(i, base_assets)
    set_owned(board, "p1", *owned_assets)
    set_owned(board, "p2", 6, 8, 9)
    set_owned(board, "p3", 26, 27, 29)
    if all(idx in owned_assets for idx in (16, 18, 19)):
        set_houses(board, 16, 18, 19, houses=3 if i not in {4, 9} else 2)
    if all(idx in owned_assets for idx in (21, 23, 24)):
        set_houses(board, 21, 23, 24, houses=2 if i not in {2, 5, 7} else 3)
    if all(idx in owned_assets for idx in (37, 39)):
        set_houses(board, 37, 39, houses=4 if i in {6, 10} else 2)
        if i == 10:
            board[39]["houses"] = 0
            board[39]["hotel"] = True
    if i in {2, 5}:
        board[12]["mortgaged"] = True
    if i in {8}:
        board[28]["mortgaged"] = True
    if i in {4, 7}:
        board[5]["mortgaged"] = True
    if sid.endswith("08"):
        board[28]["mortgaged"] = True
    ps = players(
        {"p1": 15 + (i * 7), "p2": 620 + (i * 20), "p3": 360 + (i * 15), "p4": 780 - (i * 8)},
        {"p1": [12, 24, 28, 16, 21, 37, 19, 15, 25, 39][i - 1], "p2": 24, "p3": 9, "p4": 39},
    )
    st = state("p1", 130 + i, board, ps, houses_remaining=max(0, 12 - i), hotels_remaining=12 if i < 10 else 10)
    did = f"{sid}-d1"
    mortgageable = [idx for idx in [12, 28, 5, 15, 25] if not board[idx]["mortgaged"]]
    sellable = [16, 18, 19, 21, 23, 24, 37, 39]
    dec = decision(did, 130 + i, "LIQUIDATION_DECISION", st, [legal("mortgage_property", space_schema(), mortgageable), legal("sell_houses_or_hotel", plan_schema("sell_plan"), sellable), legal("declare_bankruptcy", empty_schema())], liquidation={"owed_amount": 20 + shortfall, "owed_to_player_id": owed_to, "reason": "rent" if owed_to else "bank fee", "shortfall": shortfall, "options": {"mortgageable_space_indices": mortgageable, "sellable_building_space_indices": sellable}})
    args: dict[str, Any] = {}
    if ref_name == "mortgage_property":
        args = {"space_key": key(board, target_index)}
    elif ref_name == "sell_houses_or_hotel":
        args = {"sell_plan": [{"space_key": key(board, target_index), "kind": "HOTEL" if board[target_index].get("hotel") else "HOUSE", "count": 1}]}
    ref = action(did, ref_name, args, thought=f"{rationale} liquidation mortgage sell bankruptcy preserve")
    rubrics = [("branch", "action_name_is", 0.55, {"action": ref_name}, f"Chooses {ref_name} for this liquidation state.")]
    if ref_name == "mortgage_property":
        rubrics.append(("asset", "mortgages_space", 0.25, {"space_key": key(board, target_index)}, "Mortgages the intended non-core asset."))
        if i % 2 == 0:
            rubrics.append(("safe_branch", "action_name_in", 0.05, {"actions": ["mortgage_property"]}, "Covers the shortfall without selling buildings."))
    elif ref_name == "sell_houses_or_hotel":
        rubrics.append(("sell_branch", "action_name_in", 0.20, {"actions": ["sell_houses_or_hotel"]}, "Sells buildings only after non-core mortgages cannot cover the debt."))
        rubrics.append(("not_bankrupt", "action_name_in", 0.05, {"actions": ["sell_houses_or_hotel", "mortgage_property"]}, "Avoids unnecessary bankruptcy."))
    else:
        rubrics.append(("bankruptcy", "action_name_in", 0.25, {"actions": ["declare_bankruptcy"]}, "Declares bankruptcy when legal liquidation cannot cover the debt."))
    rubrics.append(("thought", "private_thought_mentions", 0.15, {"terms": ["liquidation", "mortgage", "sell", "bankruptcy", "preserve"]}, "Private thought names the liquidation tradeoff."))
    return scenario_payload(
        sid, "LIQUIDATION", i, title,
        f"{title}. {rationale} The key distinction is whether a non-core mortgage, building sale, or bankruptcy is actually sufficient in this debt state.",
        ["liquidation", "asset-preservation", "debt"], diff, dec, rubric(*rubrics), ref,
        rationale, "Debt payment, legal liquidation order, and asset preservation.", sources, "tear_down_core_assets_first",
    )


JAIL_CASES = [
    ("jail-early-pay-undeveloped-board-01", "Pay early on undeveloped board", 0, 1280, 0, "pay_jail_fine", "Early acquisition tempo matters more than saving $50.", ["wargamer", "monopolyland_rules"], "easy"),
    ("jail-early-pay-many-unowned-02", "Pay early with many properties unowned", 0, 1420, 0, "pay_jail_fine", "Alpha should keep moving while acquisition is still open.", ["wargamer", "haliem"], "easy"),
    ("jail-early-use-card-tempo-03", "Use jail card early when cash is earmarked", 1, 520, 0, "use_get_out_of_jail_card", "The card preserves cash and keeps acquisition tempo.", ["hasbro_pdf", "wargamer"], "medium"),
    ("jail-early-pay-own-railroad-race-04", "Pay to keep railroad acquisition race alive", 0, 900, 0, "pay_jail_fine", "Railroad and cheap-property opportunities are still live.", ["wikibooks_strategy", "wargamer"], "medium"),
    ("jail-late-roll-orange-danger-05", "Roll late against developed orange", 0, 180, 1, "roll_for_doubles", "Late jail is protection from built orange with thin cash.", ["wargamer", "soa_markov"], "hard"),
    ("jail-late-roll-red-danger-06", "Roll late against developed red", 0, 230, 1, "roll_for_doubles", "Red danger makes staying in jail defensible.", ["sanghyun_markov", "mas275"], "hard"),
    ("jail-late-roll-house-shortage-07", "Roll while opponents control scarce houses", 0, 260, 2, "roll_for_doubles", "Leaving exposes Alpha to built monopolies during house shortage.", ["house_shortage", "wargamer"], "hard"),
    ("jail-late-roll-cash-poor-08", "Roll with cash-poor reserve", 0, 75, 1, "roll_for_doubles", "Paying consumes too much of the emergency reserve.", ["ultraboardgames", "wargamer"], "hard"),
    ("jail-card-third-turn-use-09", "Use card on third jail turn", 1, 360, 2, "use_get_out_of_jail_card", "Third-turn pressure makes card use better than cash fine.", ["hasbro_pdf", "monopolyland_rules"], "medium"),
    ("jail-card-late-own-orange-income-10", "Use card to collect with own orange built", 1, 420, 2, "use_get_out_of_jail_card", "Alpha owns built orange and can afford to re-enter circulation for rent collection.", ["wargamer", "soa_markov"], "medium"),
    ("jail-third-turn-no-card-pay-11", "Pay on third turn without card", 0, 510, 2, "pay_jail_fine", "Rules pressure makes exit unavoidable; paying avoids wasting the decision.", ["hasbro_pdf", "monopolyland_rules"], "medium"),
    ("jail-third-turn-low-cash-roll-12", "Roll third turn with low cash", 0, 95, 2, "roll_for_doubles", "Roll first because cash is scarce even though exit may be forced after failure.", ["monopolyland_rules", "ultraboardgames"], "hard"),
    ("jail-own-red-rent-collection-13", "Pay to leave and collect red rents", 0, 700, 1, "pay_jail_fine", "Alpha's developed red and safe cash make movement profitable.", ["sanghyun_markov", "wargamer"], "medium"),
    ("jail-own-orange-safe-board-pay-14", "Pay when own orange dominates and board is safe", 0, 650, 1, "pay_jail_fine", "Alpha wants circulation because opponents lack developed threats.", ["soa_markov", "wargamer"], "medium"),
    ("jail-cash-poor-danger-roll-15", "Roll with $62 and multiple hotel threats", 0, 62, 1, "roll_for_doubles", "Cash is too low to pay voluntarily into a dangerous board.", ["ultraboardgames", "wargamer"], "hard"),
]


def build_jail(i: int) -> dict[str, Any]:
    sid, title, cards, cash, turns, ref_name, rationale, sources, diff = JAIL_CASES[i - 1]
    board = load_board()
    set_owned(board, "p1", 16, 18, 19)
    set_owned(board, "p2", 21, 23, 24)
    if "late" in sid or "danger" in sid or "third" in sid:
        set_houses(board, 21, 23, 24, houses=3)
    if "own-red" in sid:
        set_houses(board, 21, 23, 24, houses=0)
        set_owned(board, "p1", 21, 23, 24)
        set_houses(board, 21, 23, 24, houses=3)
    ps = players({"p1": cash, "p2": 410, "p3": 300, "p4": 500}, {"p1": 10, "p2": 24, "p3": 34, "p4": 39}, in_jail={"p1"}, jail_turns={"p1": turns}, jail_cards={"p1": cards})
    st = state("p1", 150 + i, board, ps, houses_remaining=8 if "late" in sid or "danger" in sid else 32)
    did = f"{sid}-d1"
    actions = [legal("pay_jail_fine", empty_schema(), [10]), legal("roll_for_doubles", empty_schema(), [10])]
    if cards:
        actions.insert(1, legal("use_get_out_of_jail_card", empty_schema(), [10]))
    dec = decision(did, 150 + i, "JAIL_DECISION", st, actions)
    ref = action(did, ref_name, {}, thought=f"{rationale} jail danger tempo cash card")
    rubrics = [("branch", "action_name_is", 0.60, {"action": ref_name}, "Uses the phase-appropriate jail action.")]
    if ref_name == "use_get_out_of_jail_card":
        rubrics.extend([
            ("card", "uses_jail_card", 0.18, {}, "Uses the jail card when card value beats paying cash or waiting."),
            ("thought", "private_thought_mentions", 0.22, {"terms": ["jail", "card", "tempo", "cash"]}, "Private thought names card timing."),
        ])
    elif ref_name == "pay_jail_fine":
        rubrics.extend([
            ("cash", "keeps_cash_above", 0.15, {"min_cash": max(0, cash - 50)}, "Leaves a playable reserve after paying."),
            ("tempo", "action_name_in", 0.10, {"actions": ["pay_jail_fine"]}, "Chooses movement tempo over passive protection."),
            ("thought", "private_thought_mentions", 0.15, {"terms": ["jail", "tempo", "cash", "rent"]}, "Private thought names why exiting matters."),
        ])
    else:
        rubrics.extend([
            ("defense", "action_name_in", 0.15, {"actions": ["roll_for_doubles"]}, "Uses jail as defense rather than voluntarily spending cash."),
            ("cash", "keeps_cash_above", 0.10, {"min_cash": cash}, "Preserves the full cash reserve by rolling."),
            ("thought", "private_thought_mentions", 0.15, {"terms": ["jail", "danger", "cash", "orange", "red"]}, "Private thought names board danger."),
        ])
    return scenario_payload(
        sid, "JAIL", i, title,
        f"{title}. {rationale} This scenario separates early tempo, late defense, card timing, and forced-exit pressure.",
        ["jail", "phase", "board-danger"], diff,
        dec,
        rubric(*rubrics),
        ref, rationale, "Jail as tempo early, defense late, or card/third-turn management.", sources, "fixed_jail_policy",
    )


POST_CASES = [
    ("post-turn-end-no-good-mortgage-01", "End turn when only bad mortgage is available", "end_turn", None, "The legal mortgage weakens Alpha without funding a useful build.", ["ultraboardgames", "quatizer_strategy"], "medium"),
    ("post-turn-end-cash-danger-02", "End turn with cash danger despite build option", "end_turn", None, "The build is legal but leaves Alpha exposed to red rent.", ["ultraboardgames", "wargamer"], "hard"),
    ("post-turn-end-avoid-overaction-03", "End turn after useful actions are exhausted", "end_turn", None, "No optional action improves the position enough to justify churn.", ["haliem", "quatizer_strategy"], "easy"),
    ("post-turn-build-orange-before-beta-04", "Build orange before Beta approaches", "build_houses_or_hotel", 19, "Beta is seven spaces from New York, so building now has immediate upside.", ["soa_markov", "monopolyland_stats"], "medium"),
    ("post-turn-build-red-before-gamma-05", "Build red before Gamma passes Free Parking", "build_houses_or_hotel", 24, "Gamma's position creates a near-term red rent opportunity.", ["sanghyun_markov", "mas275"], "medium"),
    ("post-turn-build-light-blue-cheap-06", "Build cheap light-blue houses now", "build_houses_or_hotel", 8, "Cheap houses add pressure while keeping liquidity.", ["haliem", "quatizer_strategy"], "easy"),
    ("post-turn-unmortgage-reading-safe-07", "Unmortgage Reading with ample cash", "unmortgage_property", 5, "Reading rent and trade value justify unmortgaging with safe reserve.", ["wikibooks_strategy", "ultraboardgames"], "easy"),
    ("post-turn-unmortgage-illinois-before-traffic-08", "Unmortgage Illinois before traffic window", "unmortgage_property", 24, "Illinois is too high-traffic to leave inactive when Alpha has cash.", ["sanghyun_markov", "monopolyland_stats"], "medium"),
    ("post-turn-unmortgage-new-york-safe-09", "Unmortgage New York with orange complete", "unmortgage_property", 19, "New York's traffic makes unmortgaging worthwhile.", ["soa_markov", "monopolyland_stats"], "medium"),
    ("post-turn-propose-orange-before-ending-10", "Propose orange trade before ending", "propose_trade", 19, "A trade attempt is higher value than ending because it can complete orange.", ["soa_markov", "wargamer"], "medium"),
    ("post-turn-propose-red-before-build-11", "Propose red completion before building elsewhere", "propose_trade", 24, "Trade sequencing matters: complete red before spending cash on lesser builds.", ["sanghyun_markov", "haliem"], "hard"),
    ("post-turn-propose-railroad-swap-12", "Propose railroad swap before ending", "propose_trade", 15, "Railroad swap can improve income without rules inference by UI.", ["wikibooks_strategy", "haliem"], "medium"),
    ("post-turn-mortgage-utility-build-orange-13", "Mortgage utility to create orange build liquidity", "mortgage_property", 12, "Mortgage weak utility first so the next decision can build orange.", ["wargamer", "ultraboardgames"], "hard"),
    ("post-turn-mortgage-railroad-build-red-14", "Mortgage railroad to fund red", "mortgage_property", 5, "Railroad mortgage is justified because red development is stronger.", ["wikibooks_strategy", "sanghyun_markov"], "hard"),
    ("post-turn-avoid-unmortgage-cash-poor-15", "Avoid unmortgaging when cash-poor", "end_turn", None, "Unmortgaging is legal but wrong with only a thin rent cushion.", ["ultraboardgames", "wargamer"], "hard"),
]


def build_post(i: int) -> dict[str, Any]:
    sid, title, ref_name, target_index, rationale, sources, diff = POST_CASES[i - 1]
    board = load_board()
    p1_assets = {5, 12}
    p2_assets = {31, 32, 34}
    if "orange" in sid or "end-" in sid:
        p1_assets.update({16, 18, 19})
    if "red" in sid and ref_name != "propose_trade":
        p1_assets.update({21, 23, 24})
    if "light-blue" in sid:
        p1_assets.update({6, 8, 9})
    if "reading" in sid:
        p1_assets.add(5)
    if "illinois" in sid and ref_name == "unmortgage_property":
        p1_assets.update({21, 23, 24})
    if "new-york" in sid and ref_name == "unmortgage_property":
        p1_assets.update({16, 18, 19})
    if ref_name == "mortgage_property" and target_index is not None:
        p1_assets.add(target_index)
    if ref_name == "propose_trade" and target_index is not None:
        p2_assets.add(target_index)
        if "red" in sid:
            p1_assets.update({21, 23})
        if "orange" in sid:
            p1_assets.update({16, 18})
    set_owned(board, "p1", *sorted(p1_assets))
    set_owned(board, "p2", *sorted(p2_assets))
    if all(idx in p1_assets for idx in (16, 18, 19)):
        set_houses(board, 16, 18, 19, houses=2 if i not in {2, 15} else 1)
    if all(idx in p1_assets for idx in (21, 23, 24)):
        set_houses(board, 21, 23, 24, houses=1 if i not in {5, 14} else 2)
    if all(idx in p1_assets for idx in (6, 8, 9)):
        set_houses(board, 6, 8, 9, houses=1)
    for idx in [5, 19, 24]:
        board[idx]["mortgaged"] = ref_name == "unmortgage_property" and idx == target_index
    cash = 90 if "cash-poor" in sid or "cash-danger" in sid else 360 + i * 18
    positions = {
        "p1": [20, 30, 10, 18, 22, 7, 5, 24, 19, 18, 23, 15, 12, 5, 24][i - 1],
        "p2": 17 if "orange" in sid else 24,
        "p3": 22 if "red" in sid else 39,
        "p4": 25 if i % 2 else 37,
    }
    ps = players({"p1": cash, "p2": 640 + i * 5, "p3": 350 + i * 3, "p4": 1020 - i * 10}, positions)
    st = state("p1", 180 + i, board, ps, houses_remaining=6 if i in {4, 5, 6, 13, 14} else 18)
    did = f"{sid}-d1"
    buildable = [idx for idx in [16, 18, 19, 21, 23, 24, 6, 8, 9] if board[idx].get("owner_id") == "p1"]
    unmortgageable = [idx for idx in [5, 19, 24] if board[idx].get("owner_id") == "p1" and board[idx].get("mortgaged")]
    legal_actions = [legal("end_turn", empty_schema()), legal("build_houses_or_hotel", plan_schema("build_plan"), buildable or [16, 18, 19]), legal("propose_trade", trade_schema(True)), legal("unmortgage_property", space_schema(), unmortgageable or [5])]
    if ref_name == "mortgage_property":
        legal_actions.insert(1, legal("mortgage_property", space_schema(), [target_index]))
    dec = decision(did, 180 + i, "POST_TURN_ACTION_DECISION", st, legal_actions, post_turn={"options": {"can_trade_with": ["p2", "p3", "p4"], "max_trade_exchanges": 4, "mortgageable_space_indices": [idx for idx in [12, 5, target_index] if isinstance(idx, int) and board[idx].get("owner_id") == "p1" and not board[idx].get("mortgaged")], "unmortgageable_space_indices": unmortgageable, "buildable_space_indices": buildable, "sellable_building_space_indices": buildable}})
    ref_args: dict[str, Any] = {}
    if ref_name == "build_houses_or_hotel":
        ref_args = {"build_plan": [{"space_key": key(board, target_index), "kind": "HOUSE", "count": 1}]}
    elif ref_name == "unmortgage_property":
        ref_args = {"space_key": key(board, target_index)}
    elif ref_name == "propose_trade":
        ref_args = {"to_player_id": "p2", "offer": {"cash": 120, "properties": [], "get_out_of_jail_cards": 0}, "request": {"cash": 0, "properties": [key(board, target_index)], "get_out_of_jail_cards": 0}}
    elif ref_name == "mortgage_property":
        ref_args = {"space_key": key(board, target_index)}
    ref = action(did, ref_name, ref_args, public="Let's see if there is a deal before I pass." if ref_name == "propose_trade" else "", thought=f"{rationale} post-turn cash build trade unmortgage mortgage")
    rubrics = [("branch", "action_name_is", 0.55, {"action": ref_name}, f"Chooses {ref_name} instead of taking a generic optional action.")]
    if ref_name == "build_houses_or_hotel":
        rubrics.append(("build", "builds_on_group", 0.25, {"space_keys": [key(board, target_index)]}, "Builds on the intended property group."))
    elif ref_name in {"unmortgage_property", "mortgage_property"}:
        rubrics.append(("space", "arg_equals", 0.25, {"key": "space_key", "value": key(board, target_index)}, "Targets the intended property."))
    elif ref_name == "propose_trade":
        rubrics.append(("request", "trade_request_contains_property", 0.25, {"space_key": key(board, target_index)}, "Requests the relevant trade asset."))
    else:
        rubrics.append(("cash", "keeps_cash_above", 0.25, {"min_cash": 80}, "Does not spend cash on a low-value optional action."))
    rubrics.append(("thought", "private_thought_mentions", 0.20, {"terms": ["post-turn", "cash", "build", "trade", "unmortgage", "mortgage"]}, "Private thought identifies the optional-action reason."))
    return scenario_payload(
        sid, "POST_TURN_STRATEGY", i, title,
        f"{title}. {rationale} Optional-action restraint matters here because legal tools are not automatically useful tools.",
        ["post-turn", "optional-actions", "strategy"], diff, dec, rubric(*rubrics), ref,
        rationale, "Intentional optional-action sequencing after movement.", sources, "overacting_with_legal_tool",
    )


BUILDERS = {
    "BUY_OR_AUCTION": build_buy,
    "AUCTION": build_auction,
    "TRADE_PROPOSE": build_trade_propose,
    "TRADE_RESPONSE": build_trade_response,
    "BUILD_OR_MORTGAGE": build_build,
    "LIQUIDATION": build_liquidation,
    "JAIL": build_jail,
    "POST_TURN_STRATEGY": build_post,
}


def write_research_backlog(scenarios: list[dict[str, Any]]) -> None:
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
    lines = ["# Micro-v1 Research Backlog", ""]
    for source in RESEARCH_SOURCES.values():
        lines.extend([f"- source_url: {source['url']}", f"  source_type: strategy/research", f"  claim: {source['claim']}", ""])
    for scenario in scenarios:
        lines.extend(
            [
                f"## {scenario['scenario_id']}",
                f"category: {scenario['category']}",
                f"scenario_slug: {scenario['scenario_id']}",
                f"strategic_tension: {scenario['notes']['strategic_theme']}",
                f"source_claims: {', '.join(src['title'] for src in scenario['research_sources'])}",
                "board_state_requirements: frozen DecisionPoint fixture in contracts/micro/scenarios",
                f"legal_actions_required: {', '.join(action['action'] for action in scenario['decision_point']['legal_actions'])}",
                f"preferred_action: {scenario['reference_policy']['action']['action']}",
                "acceptable_actions: rubric-dependent partial credit",
                "bad_actions: actions missing the primary rubric branch",
                f"rubric_criteria: {', '.join(item['criterion_id'] for item in scenario['evaluation']['rubric'])}",
                f"difficulty: {scenario['difficulty']}",
                "",
            ]
        )
    (RESEARCH_DIR / "scenario_backlog.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    SCENARIOS_DIR.mkdir(parents=True, exist_ok=True)
    SUITES_DIR.mkdir(parents=True, exist_ok=True)
    for path in SCENARIOS_DIR.glob("*.json"):
        path.unlink()
    for path in MICRO_DIR.glob("*.json"):
        path.unlink()
    scenarios: list[dict[str, Any]] = []
    for category, count in CATEGORY_COUNTS.items():
        for index in range(1, count + 1):
            scenarios.append(BUILDERS[category](index))
    scenario_ids = [scenario["scenario_id"] for scenario in scenarios]
    for scenario in scenarios:
        (SCENARIOS_DIR / f"{scenario['scenario_id']}.json").write_text(json.dumps(scenario, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    suite = {
        "schema_version": "v1",
        "suite_id": SUITE_ID,
        "title": "MonopolyBench Micro Decision Suite v1",
        "description": "Research-backed frozen single-decision Monopoly scenarios for tactical, strategic, and negotiation evaluation.",
        "scenario_ids": scenario_ids,
        "categories": {category: {"target_count": count, "actual_count": count} for category, count in CATEGORY_COUNTS.items()},
        "scoring_version": "rubric-v1",
        "prompt_conditions": ["default", "minimal", "pro_strategy_cheatsheet", "no_private_thought", "full_state", "compact_state"],
    }
    (SUITES_DIR / f"{SUITE_ID}.json").write_text(json.dumps(suite, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    write_research_backlog(scenarios)
    print(f"Wrote {len(scenarios)} scenarios and suite {SUITE_ID}.")


if __name__ == "__main__":
    main()
