from __future__ import annotations

import asyncio
import os
import sys
from dataclasses import dataclass, field
from typing import Any, cast

from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

from .catalog import get_suite, list_scenario_summaries, list_scenarios, load_scenario
from .runner import MicroRunConfig, build_leaderboard, run_batch_with_progress, run_scenario


CATEGORIES = [
    "ALL",
    "BUY_OR_AUCTION",
    "AUCTION",
    "TRADE_PROPOSE",
    "TRADE_RESPONSE",
    "BUILD_OR_MORTGAGE",
    "LIQUIDATION",
    "JAIL",
    "POST_TURN_STRATEGY",
]
PROMPT_CONDITION = "live_game"
DEFAULT_MODEL_ID = "openai/gpt-oss-120b"
FOCUS_AREAS = ["catalog", "actions"]
ACTION_BUTTONS = [
    ("Run selected", "run_selected", "r"),
    ("Run filtered", "run_filtered", "c"),
    ("Run suite", "run_suite", "a"),
    ("Detail", "detail", "d"),
    ("Leaderboard", "leaderboard", "l"),
    ("Latest", "latest", "h"),
    ("Model ID", "edit_model", "m"),
    ("Display name", "edit_name", "n"),
    ("Reasoning", "cycle_reasoning", "g"),
    ("Search", "edit_search", "/"),
    ("Category", "cycle_category", "f"),
    ("Quit", "quit", "q"),
]
REASONING_OPTIONS = ["low", "medium", "high"]


@dataclass(frozen=True)
class KeyPress:
    name: str
    char: str = ""
    x: int | None = None
    y: int | None = None


@dataclass
class MicroTuiState:
    suite_id: str = "micro-v1"
    category: str = "ALL"
    search: str = ""
    selected_index: int = 0
    model_id: str = DEFAULT_MODEL_ID
    focus: str = "catalog"
    action_index: int = 0
    input_mode: str | None = None
    input_buffer: str = ""
    display_name: str = "Micro Agent"
    reasoning_effort: str = "medium"
    latest_result: dict[str, Any] | None = None
    latest_batch: dict[str, Any] | None = None
    latest_failures: list[dict[str, Any]] = field(default_factory=list)
    latest_scope: str = "none"
    last_error: str | None = None
    status_message: str | None = None
    terminal_width: int = 100
    terminal_height: int = 30
    summaries: list[dict[str, Any]] = field(default_factory=list)
    scenarios_by_id: dict[str, dict[str, Any]] = field(default_factory=dict)
    suite_scenario_ids: list[str] = field(default_factory=list)
    test_mode: bool = False


def main() -> None:
    console = Console()
    state = MicroTuiState()
    state.test_mode = os.getenv("MONOPOLY_MICRO_TUI_TEST_MODE", "").strip().lower() in {"1", "true", "yes"}
    _load_catalog_state(state)
    _clamp_selection(state)
    mouse_mode = _enable_mouse(console)
    try:
        with Live(_render_dashboard(state), console=console, screen=True, refresh_per_second=12) as live:
            while True:
                _sync_terminal_size(console, state)
                live.update(_render_dashboard(state))
                action = _apply_dashboard_key(state, _read_key())
                if action == "quit":
                    return
                if action is not None:
                    live.stop()
                    try:
                        _execute_action(console, state, action)
                    finally:
                        live.start(refresh=True)
                _clamp_selection(state)
    finally:
        _disable_mouse(console, mouse_mode)


def _execute_action(console: Console, state: MicroTuiState, action: str) -> None:
    if action == "detail":
        scenario = _selected_scenario(state)
        if scenario is None:
            _wait_for_key(console, "No selected scenario.")
            return
        _show_detail(console, scenario["scenario_id"])
        return
    if action == "run_selected":
        scenario = _selected_scenario(state)
        if scenario is None:
            _wait_for_key(console, "No selected scenario.")
            return
        _run_single(console, state, scenario["scenario_id"])
        return
    if action == "run_filtered":
        scenario_ids = [item["scenario_id"] for item in _filtered_scenarios(state)]
        _run_batch_scope(console, state, scenario_ids, scope=f"category/search ({len(scenario_ids)})")
        return
    if action == "run_suite":
        scenario_ids = list(state.suite_scenario_ids)
        _run_batch_scope(console, state, scenario_ids, scope=f"full suite ({len(scenario_ids)})")
        return
    if action == "leaderboard":
        _show_leaderboard(console, state)
        return
    if action == "latest":
        _show_latest(console, state)


def _apply_dashboard_key(state: MicroTuiState, key: KeyPress) -> str | None:
    state.last_error = None
    if state.input_mode is not None:
        return _apply_input_key(state, key)

    if key.name == "mouse" and key.x is not None and key.y is not None:
        return _apply_mouse_click(state, key.x, key.y)
    if key.name == "char":
        return _apply_shortcut_key(state, key.char.lower())
    if key.name == "tab":
        _cycle_focus(state, 1)
        return None
    if key.name == "shift_tab":
        _cycle_focus(state, -1)
        return None
    if key.name == "escape":
        state.search = ""
        state.selected_index = 0
        state.status_message = "Search cleared."
        return None
    if key.name in {"up", "down", "page_up", "page_down", "home", "end"}:
        _move_current_focus(state, key.name)
        return None
    if key.name in {"left", "right"}:
        if state.focus == "catalog":
            _cycle_category(state, -1 if key.name == "left" else 1)
        else:
            _move_action(state, -1 if key.name == "left" else 1)
        return None
    if key.name == "enter":
        if state.focus == "catalog":
            return "detail"
        label, action, _shortcut = ACTION_BUTTONS[state.action_index]
        if action == "edit_model":
            _begin_input(state, "model")
            return None
        if action == "edit_name":
            _begin_input(state, "name")
            return None
        if action == "edit_search":
            _begin_input(state, "search")
            return None
        if action == "cycle_reasoning":
            _cycle_reasoning(state, 1)
            return None
        if action == "cycle_category":
            _cycle_category(state, 1)
            state.status_message = f"Category set to {state.category}."
            return None
        state.status_message = f"{label} selected."
        return action
    return None


def _apply_mouse_click(state: MicroTuiState, x: int, y: int) -> str | None:
    regions = _layout_regions(state)
    if _point_inside(x, y, regions["catalog"]):
        state.focus = "catalog"
        row = y - regions["catalog"][1] - 4
        items = _filtered_scenarios(state)
        start = _visible_catalog_start(state, len(items))
        if 0 <= row < min(18, len(items) - start):
            state.selected_index = start + row
            state.status_message = "Scenario selected. Press Enter or click Detail/Run."
        return None

    if _point_inside(x, y, regions["actions"]):
        state.focus = "actions"
        row = y - regions["actions"][1] - 2
        if row < 0:
            return None
        row = min(row, len(ACTION_BUTTONS) - 1)
        state.action_index = row
        label, action, _shortcut = ACTION_BUTTONS[row]
        if action == "edit_model":
            _begin_input(state, "model")
            return None
        if action == "edit_name":
            _begin_input(state, "name")
            return None
        if action == "edit_search":
            _begin_input(state, "search")
            return None
        if action == "cycle_reasoning":
            _cycle_reasoning(state, 1)
            return None
        if action == "cycle_category":
            _cycle_category(state, 1)
            state.status_message = f"Category set to {state.category}."
            return None
        state.status_message = f"{label} clicked."
        return action
    return None


def _apply_input_key(state: MicroTuiState, key: KeyPress) -> str | None:
    if key.name == "enter":
        if state.input_mode == "model":
            state.model_id = state.input_buffer.strip() or state.model_id
            state.status_message = f"Model set to {state.model_id}."
        elif state.input_mode == "name":
            state.display_name = state.input_buffer.strip() or state.display_name
            state.status_message = f"Display name set to {state.display_name}."
        elif state.input_mode == "search":
            state.search = state.input_buffer.strip()
            state.selected_index = 0
            state.status_message = f"Search set to {state.search or '-'}."
        state.input_mode = None
        state.input_buffer = ""
        return None
    if key.name == "escape":
        state.input_mode = None
        state.input_buffer = ""
        state.status_message = "Edit cancelled."
        return None
    if key.name == "backspace":
        state.input_buffer = state.input_buffer[:-1]
        return None
    if key.name == "char":
        state.input_buffer += key.char
        return None
    return None


def _apply_shortcut_key(state: MicroTuiState, char: str) -> str | None:
    shortcuts = {shortcut: action for _label, action, shortcut in ACTION_BUTTONS}
    action = shortcuts.get(char)
    if action is None:
        return None
    if action == "edit_model":
        _begin_input(state, "model")
        return None
    if action == "edit_name":
        _begin_input(state, "name")
        return None
    if action == "edit_search":
        _begin_input(state, "search")
        return None
    if action == "cycle_reasoning":
        _cycle_reasoning(state, 1)
        return None
    if action == "cycle_category":
        _cycle_category(state, 1)
        state.status_message = f"Category set to {state.category}."
        return None
    return action


def _begin_input(state: MicroTuiState, mode: str) -> None:
    state.input_mode = mode
    if mode == "model":
        state.input_buffer = state.model_id
    elif mode == "name":
        state.input_buffer = state.display_name
    else:
        state.input_buffer = state.search
    state.status_message = f"Editing {mode}. Enter saves, Esc cancels."


def _cycle_focus(state: MicroTuiState, delta: int) -> None:
    current = FOCUS_AREAS.index(state.focus)
    state.focus = FOCUS_AREAS[(current + delta) % len(FOCUS_AREAS)]
    state.status_message = f"Focus: {state.focus}."


def _move_current_focus(state: MicroTuiState, key_name: str) -> None:
    if state.focus == "actions":
        step_by_key = {"up": -1, "down": 1, "page_up": -3, "page_down": 3}
        if key_name == "home":
            state.action_index = 0
        elif key_name == "end":
            state.action_index = len(ACTION_BUTTONS) - 1
        else:
            _move_action(state, step_by_key[key_name])
        return

    step_by_key = {"up": -1, "down": 1, "page_up": -10, "page_down": 10}
    if key_name == "home":
        state.selected_index = 0
    elif key_name == "end":
        state.selected_index = max(0, len(_filtered_scenarios(state)) - 1)
    else:
        state.selected_index += step_by_key[key_name]
    _clamp_selection(state)


def _move_action(state: MicroTuiState, delta: int) -> None:
    state.action_index = (state.action_index + delta) % len(ACTION_BUTTONS)


def _cycle_category(state: MicroTuiState, delta: int) -> None:
    current = CATEGORIES.index(state.category)
    state.category = CATEGORIES[(current + delta) % len(CATEGORIES)]
    state.selected_index = 0


def _cycle_reasoning(state: MicroTuiState, delta: int) -> None:
    current = REASONING_OPTIONS.index(state.reasoning_effort)
    state.reasoning_effort = REASONING_OPTIONS[(current + delta) % len(REASONING_OPTIONS)]
    state.status_message = f"Reasoning set to {state.reasoning_effort}."


def _sync_terminal_size(console: Console, state: MicroTuiState) -> None:
    state.terminal_width = max(40, console.size.width)
    state.terminal_height = max(20, console.size.height)


def _load_catalog_state(state: MicroTuiState) -> None:
    suite = get_suite(state.suite_id)
    suite_ids = set(suite["scenario_ids"])
    state.suite_scenario_ids = list(suite["scenario_ids"])
    state.summaries = list_scenario_summaries(suite_id=state.suite_id)
    state.scenarios_by_id = {
        scenario["scenario_id"]: scenario
        for scenario in list_scenarios()
        if scenario["scenario_id"] in suite_ids
    }


def _ensure_catalog_state(state: MicroTuiState) -> None:
    if not state.summaries or not state.scenarios_by_id or not state.suite_scenario_ids:
        _load_catalog_state(state)


def _layout_regions(state: MicroTuiState) -> dict[str, tuple[int, int, int, int]]:
    width = state.terminal_width
    height = state.terminal_height
    body_top = 7
    body_bottom = max(body_top, height - 5)
    body_height = body_bottom - body_top + 1
    catalog_right = max(20, (width * 3) // 5)
    scenario_bottom = body_top + max(1, (body_height * 3) // 5) - 1
    actions_right = catalog_right + max(1, (width - catalog_right) // 2)
    return {
        "catalog": (1, body_top, catalog_right, body_bottom),
        "scenario": (catalog_right + 1, body_top, width, scenario_bottom),
        "actions": (catalog_right + 1, scenario_bottom + 1, actions_right, body_bottom),
        "status": (actions_right + 1, scenario_bottom + 1, width, body_bottom),
    }


def _point_inside(x: int, y: int, region: tuple[int, int, int, int]) -> bool:
    left, top, right, bottom = region
    return left <= x <= right and top <= y <= bottom


def _visible_catalog_start(state: MicroTuiState, item_count: int) -> int:
    return max(0, min(state.selected_index - 8, max(0, item_count - 18)))


def _read_key() -> KeyPress:
    if sys.platform == "win32":
        return _read_windows_key()
    return _read_posix_key()


def _read_windows_key() -> KeyPress:
    import msvcrt

    char = msvcrt.getwch()
    if char == "\x1b":
        return _read_windows_escape_sequence(msvcrt) or KeyPress("escape")
    if char in {"\x00", "\xe0"}:
        code = msvcrt.getwch()
        return {
            "H": KeyPress("up"),
            "P": KeyPress("down"),
            "K": KeyPress("left"),
            "M": KeyPress("right"),
            "I": KeyPress("page_up"),
            "Q": KeyPress("page_down"),
            "G": KeyPress("home"),
            "O": KeyPress("end"),
            "\x0f": KeyPress("shift_tab"),
        }.get(code, KeyPress("unknown"))
    if char == "\r":
        return KeyPress("enter")
    if char == "\t":
        return KeyPress("tab")
    if char == "\b":
        return KeyPress("backspace")
    if char.isprintable():
        return KeyPress("char", char)
    return KeyPress("unknown")


def _read_windows_escape_sequence(msvcrt: Any) -> KeyPress | None:
    import time

    time.sleep(0.01)
    if not msvcrt.kbhit():
        return None
    second = msvcrt.getwch()
    if second != "[":
        return None
    if not msvcrt.kbhit():
        return None
    third = msvcrt.getwch()
    if third == "<":
        payload = ""
        while True:
            char = msvcrt.getwch()
            payload += char
            if char in {"M", "m"}:
                return _parse_sgr_mouse(payload)
        return None
    if third == "Z":
        return KeyPress("shift_tab")
    return {
        "A": KeyPress("up"),
        "B": KeyPress("down"),
        "C": KeyPress("right"),
        "D": KeyPress("left"),
        "H": KeyPress("home"),
        "F": KeyPress("end"),
    }.get(third)


def _read_posix_key() -> KeyPress:
    select = cast(Any, __import__("select"))
    termios = cast(Any, __import__("termios"))
    tty = cast(Any, __import__("tty"))

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        char = sys.stdin.read(1)
        if char == "\x1b":
            if not select.select([sys.stdin], [], [], 0.03)[0]:
                return KeyPress("escape")
            second = sys.stdin.read(1)
            if second != "[":
                return KeyPress("escape")
            if not select.select([sys.stdin], [], [], 0.03)[0]:
                return KeyPress("escape")
            third = sys.stdin.read(1)
            if third == "<":
                payload = ""
                while select.select([sys.stdin], [], [], 0.03)[0]:
                    next_char = sys.stdin.read(1)
                    payload += next_char
                    if next_char in {"M", "m"}:
                        return _parse_sgr_mouse(payload) or KeyPress("unknown")
                return KeyPress("unknown")
            if third == "Z":
                return KeyPress("shift_tab")
            if third in {"1", "4", "5", "6"}:
                _tilde = sys.stdin.read(1)
                return {"1": KeyPress("home"), "4": KeyPress("end"), "5": KeyPress("page_up"), "6": KeyPress("page_down")}[third]
            return {
                "A": KeyPress("up"),
                "B": KeyPress("down"),
                "C": KeyPress("right"),
                "D": KeyPress("left"),
                "H": KeyPress("home"),
                "F": KeyPress("end"),
            }.get(third, KeyPress("unknown"))
        if char in {"\r", "\n"}:
            return KeyPress("enter")
        if char == "\t":
            return KeyPress("tab")
        if char in {"\x7f", "\b"}:
            return KeyPress("backspace")
        if char.isprintable():
            return KeyPress("char", char)
        return KeyPress("unknown")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def _parse_sgr_mouse(payload: str) -> KeyPress | None:
    if not payload or payload[-1] != "M":
        return None
    parts = payload[:-1].split(";")
    if len(parts) != 3:
        return None
    try:
        button = int(parts[0])
        x = int(parts[1])
        y = int(parts[2])
    except ValueError:
        return None
    if button != 0:
        return None
    return KeyPress("mouse", x=x, y=y)


def _enable_mouse(console: Console) -> int | None:
    previous_mode = _enable_windows_virtual_terminal_input()
    _write_terminal_sequence(console, "\x1b[?1000h\x1b[?1006h")
    return previous_mode


def _disable_mouse(console: Console, previous_mode: int | None) -> None:
    _write_terminal_sequence(console, "\x1b[?1000l\x1b[?1006l")
    _restore_windows_console_mode(previous_mode)


def _write_terminal_sequence(console: Console, sequence: str) -> None:
    file = console.file
    file.write(sequence)
    file.flush()


def _enable_windows_virtual_terminal_input() -> int | None:
    if sys.platform != "win32":
        return None
    try:
        import ctypes
    except ImportError:
        return None
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-10)
    mode = ctypes.c_uint32()
    if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        return None
    previous = int(mode.value)
    enable_virtual_terminal_input = 0x0200
    enable_extended_flags = 0x0080
    enable_mouse_input = 0x0010
    enable_quick_edit_mode = 0x0040
    new_mode = (previous | enable_virtual_terminal_input | enable_extended_flags | enable_mouse_input) & ~enable_quick_edit_mode
    if not kernel32.SetConsoleMode(handle, new_mode):
        return None
    return previous


def _restore_windows_console_mode(previous_mode: int | None) -> None:
    if previous_mode is None or sys.platform != "win32":
        return
    try:
        import ctypes
    except ImportError:
        return
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-10)
    kernel32.SetConsoleMode(handle, previous_mode)


def _render_dashboard(state: MicroTuiState) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(_header_panel(state), name="header", size=7),
        Layout(name="body"),
        Layout(_controls_panel(state), name="controls", size=5),
    )
    layout["body"].split_row(
        Layout(_catalog_panel(state), name="catalog", ratio=3),
        Layout(name="right", ratio=2),
    )
    layout["right"].split_column(
        Layout(_scenario_panel(state), name="scenario", ratio=3),
        Layout(name="run_controls", ratio=2),
    )
    layout["run_controls"].split_row(
        Layout(_actions_panel(state), name="actions", ratio=1),
        Layout(_run_status_panel(state), name="status", ratio=1),
    )
    return layout


def _header_panel(state: MicroTuiState) -> Panel:
    _ensure_catalog_state(state)
    counts = _category_counts(state.summaries)
    filtered_count = len(_filtered_scenarios(state))
    target_count = filtered_count if state.category != "ALL" or state.search else len(state.suite_scenario_ids)
    mode = f"editing {state.input_mode}: {state.input_buffer}" if state.input_mode else f"focus={state.focus}"
    summary = (
        f"[bold]MonopolyBench[/bold] [magenta]Micro Dashboard TUI[/magenta]   "
        f"[bold]Suite[/bold] {state.suite_id}   [bold]Prompt[/bold] {PROMPT_CONDITION}"
        f"{'   [yellow]TEST MODE[/yellow]' if state.test_mode else ''}\n"
        f"[bold]Target[/bold] {target_count}/{len(state.suite_scenario_ids)}   "
        f"[bold]Filter[/bold] {state.category} / {state.search or '-'}   [bold]Mode[/bold] {mode}\n"
        f"[bold]Model[/bold] {state.model_id}   [bold]Name[/bold] {state.display_name}   "
        f"[bold]Reasoning[/bold] {state.reasoning_effort}\n"
        f"[bold]Counts[/bold] " + " ".join(f"{key}:{value}" for key, value in counts.items())
    )
    if state.last_error:
        summary += f"\n[red]{state.last_error}[/red]"
    elif state.status_message:
        summary += f"\n[dim]{state.status_message}[/dim]"
    return Panel(summary, title="MonopolyBench Micro Decision Suite", border_style="cyan")


def _controls_panel(state: MicroTuiState) -> Panel:
    if state.input_mode is not None:
        text = "Type to edit. Enter saves. Esc cancels. Backspace deletes."
    else:
        text = (
            "Click actions/scenarios or use keys. Arrows move/select. Left/right cycles categories in catalog. "
            "Tab/Shift+Tab changes focus. Enter opens/activates. r run selected, c run filtered, a run suite, d detail, "
            "l leaderboard, h latest, m model, / search, f category, q quit."
        )
    return Panel(text, title="Keyboard", border_style="dim")


def _catalog_panel(state: MicroTuiState) -> Panel:
    items = _filtered_scenarios(state)
    table = Table(expand=True, show_lines=False)
    table.add_column("#", justify="right", width=4)
    table.add_column("Category", width=19)
    table.add_column("Diff", width=6)
    table.add_column("Title")
    table.add_column("Ref", width=20)
    start = _visible_catalog_start(state, len(items))
    visible = items[start : start + 18]
    for absolute_index, item in enumerate(visible, start=start):
        selected = absolute_index == state.selected_index
        style = "black on cyan" if selected else ""
        ref = str(item.get("reference_action", ""))
        table.add_row(
            str(absolute_index + 1),
            item["category"],
            item["difficulty"],
            item["title"],
            ref,
            style=style,
        )
    if not visible:
        table.add_row("-", "-", "-", "No scenarios match the current filters.", "-")
    title = f"Catalog ({len(items)} shown by filter)"
    border = "bright_green" if state.focus == "catalog" and state.input_mode is None else "green"
    return Panel(table, title=title, border_style=border)


def _scenario_panel(state: MicroTuiState) -> Panel:
    _ensure_catalog_state(state)
    item = _selected_scenario(state)
    if item is None:
        return Panel("No scenario selected.", title="Scenario", border_style="yellow")
    scenario = state.scenarios_by_id.get(item["scenario_id"]) or load_scenario(item["scenario_id"])
    legal_actions = ", ".join(action["action"] for action in scenario["decision_point"]["legal_actions"])
    rubric_points = sum(float(entry["max_points"]) for entry in scenario["evaluation"]["rubric"])
    text = Text()
    text.append(f"{scenario['title']}\n", style="bold")
    text.append(f"{scenario['description']}\n\n")
    text.append(f"ID: {scenario['scenario_id']}\n", style="dim")
    text.append(f"Category: {scenario['category']}   Difficulty: {scenario['difficulty']}\n")
    text.append(f"Decision: {scenario['decision_point']['decision_type']}\n")
    text.append(f"Focal player: {scenario['focal_player_id']}\n")
    text.append(f"Reference: {scenario['reference_policy']['action']['action']}\n")
    text.append(f"Rubric: {len(scenario['evaluation']['rubric'])} criteria / {rubric_points:g} points\n")
    text.append(f"Legal actions: {legal_actions}\n\n")
    text.append("Strategic tension:\n", style="bold")
    text.append(str(scenario["notes"].get("strategic_theme", "-")))
    return Panel(text, title="Selected Scenario", border_style="yellow")


def _actions_panel(state: MicroTuiState) -> Panel:
    table = Table(expand=True, show_header=False, box=None)
    table.add_column("Key", width=5)
    table.add_column("Action")
    for index, (label, _action, shortcut) in enumerate(ACTION_BUTTONS):
        selected = state.focus == "actions" and state.input_mode is None and index == state.action_index
        style = "black on magenta" if selected else ""
        table.add_row(shortcut, label, style=style)
    border = "bright_magenta" if state.focus == "actions" and state.input_mode is None else "magenta"
    return Panel(table, title="Controls", border_style=border)


def _run_status_panel(state: MicroTuiState) -> Panel:
    selected = _selected_scenario(state)
    latest_kind = "None"
    latest_score = "-"
    latest_action = "-"
    latest_failures = "-"
    if state.latest_result is not None:
        latest_kind = "Single"
        latest_score = f"{state.latest_result['score']['total']} {state.latest_result['score']['label']}"
        latest_action = state.latest_result["outcome"]["action"]["action"]
        latest_failures = "0"
    elif state.latest_batch is not None:
        latest_kind = "Batch"
        rows = state.latest_batch.get("leaderboard", {}).get("rows", [])
        latest_score = str(rows[0]["average_score"]) if rows else "0"
        latest_action = state.latest_batch.get("batch_id", "-")
        latest_failures = str(len(state.latest_failures))

    table = Table(expand=True, show_header=False, box=None)
    table.add_column("Key", width=12)
    table.add_column("Value")
    table.add_row("Selected", selected["title"] if selected else "-")
    table.add_row("Category", state.category)
    table.add_row("Filtered", str(len(_filtered_scenarios(state))))
    table.add_row("Latest", latest_kind)
    table.add_row("Score", latest_score)
    table.add_row("Action/Batch", latest_action)
    table.add_row("Failures", latest_failures)
    table.add_row("Scope", state.latest_scope)
    return Panel(table, title="Run Status", border_style="blue")


def _filtered_scenarios(state: MicroTuiState) -> list[dict[str, Any]]:
    _ensure_catalog_state(state)
    query = state.search.strip().lower()
    filtered: list[dict[str, Any]] = []
    for item in state.summaries:
        if state.category != "ALL" and item["category"] != state.category:
            continue
        haystack = " ".join([item["title"], item["description"], " ".join(item["tags"])]).lower()
        if query and query not in haystack:
            continue
        filtered.append(item)
    return filtered


def _selected_scenario(state: MicroTuiState) -> dict[str, Any] | None:
    items = _filtered_scenarios(state)
    if not items:
        return None
    _clamp_selection(state)
    return items[state.selected_index]


def _clamp_selection(state: MicroTuiState) -> None:
    count = len(_filtered_scenarios(state))
    if count <= 0:
        state.selected_index = 0
        return
    state.selected_index = max(0, min(state.selected_index, count - 1))


def _category_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts = {category: 0 for category in CATEGORIES if category != "ALL"}
    for item in items:
        counts[item["category"]] += 1
    return counts


def _show_detail(console: Console, scenario_id: str) -> None:
    scenario = load_scenario(scenario_id)
    console.clear()
    console.rule(f"[bold]{scenario['title']}[/bold]")
    console.print(scenario["description"])
    console.print(f"[bold]Category[/bold] {scenario['category']}   [bold]Difficulty[/bold] {scenario['difficulty']}")
    console.print(f"[bold]Focal player[/bold] {scenario['focal_player_id']}   [bold]Decision[/bold] {scenario['decision_point']['decision_type']}")
    console.print(f"[bold]Strategic tension[/bold] {scenario['notes']['strategic_theme']}")
    console.print(f"[bold]Trap action[/bold] {scenario['notes'].get('trap_action', '-')}")
    console.print(f"[bold]Reference[/bold] {scenario['reference_policy']['action']['action']} - {scenario['reference_policy']['rationale']}")
    _print_board_summary(console, scenario)
    _print_legal_actions(console, scenario)
    _print_rubric(console, scenario)
    _print_research_sources(console, scenario)
    _wait_for_key(console)


def _print_board_summary(console: Console, scenario: dict[str, Any]) -> None:
    table = Table(title="Board Summary", expand=True)
    table.add_column("Player")
    table.add_column("Cash", justify="right")
    table.add_column("Position")
    table.add_column("Jail")
    table.add_column("Owned")
    state = scenario["decision_point"]["state"]
    for player in state["players"]:
        owned = [space["name"] for space in state["board"] if space.get("owner_id") == player["player_id"]]
        table.add_row(
            player["name"],
            str(player["cash"]),
            str(player["position"]),
            "yes" if player["in_jail"] else "no",
            ", ".join(owned[:8]) + ("..." if len(owned) > 8 else ""),
        )
    console.print(table)


def _print_legal_actions(console: Console, scenario: dict[str, Any]) -> None:
    table = Table(title="Legal Actions", expand=True)
    table.add_column("Action")
    table.add_column("Args")
    table.add_column("Highlights")
    for action in scenario["decision_point"]["legal_actions"]:
        schema = action.get("args_schema", {})
        args = ", ".join((schema.get("properties") or {}).keys()) or "none"
        hints = action.get("ui_hints", {}).get("highlight_space_indices", [])
        table.add_row(action["action"], args, ", ".join(str(item) for item in hints) or "-")
    console.print(table)


def _print_rubric(console: Console, scenario: dict[str, Any]) -> None:
    table = Table(title="Rubric", expand=True)
    table.add_column("Criterion")
    table.add_column("Type")
    table.add_column("Points", justify="right")
    table.add_column("Description")
    for item in scenario["evaluation"]["rubric"]:
        table.add_row(item["criterion_id"], item["type"], str(item["max_points"]), item["description"])
    console.print(table)


def _print_research_sources(console: Console, scenario: dict[str, Any]) -> None:
    sources = scenario.get("research_sources") or []
    if not sources:
        return
    table = Table(title="Research Sources", expand=True)
    table.add_column("Title")
    table.add_column("Claim")
    for source in sources[:5]:
        table.add_row(str(source.get("title", "-")), str(source.get("claim", "-")))
    console.print(table)


def _run_single(console: Console, state: MicroTuiState, scenario_id: str) -> None:
    state.last_error = None
    if state.test_mode:
        result = _fake_result(state, scenario_id)
        state.latest_result = result
        state.latest_batch = None
        state.latest_failures = []
        state.latest_scope = f"single: {scenario_id}"
        _show_result(console, result)
        return
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            progress.add_task(f"Running {scenario_id}", total=None)
            result = asyncio.run(
                run_scenario(
                    MicroRunConfig(
                        scenario_id=scenario_id,
                        openrouter_model_id=state.model_id,
                        name=state.display_name,
                        reasoning={"effort": state.reasoning_effort},
                        prompt_condition=PROMPT_CONDITION,
                    )
                )
            )
    except Exception as exc:
        state.last_error = str(exc)
        _wait_for_key(console, f"Run failed: {exc}")
        return
    state.latest_result = result
    state.latest_batch = None
    state.latest_failures = []
    state.latest_scope = f"single: {scenario_id}"
    _show_result(console, result)


def _run_batch_scope(console: Console, state: MicroTuiState, scenario_ids: list[str], *, scope: str) -> None:
    if not scenario_ids:
        _wait_for_key(console, "No scenarios match the current scope.")
        return
    state.last_error = None
    if state.test_mode:
        results = [_fake_result(state, scenario_id) for scenario_id in scenario_ids]
        batch = {
            "batch_id": f"micro-tui-test-{len(results)}",
            "leaderboard": build_leaderboard(results),
            "results": results,
            "failures": [],
        }
        state.latest_batch = batch
        state.latest_result = None
        state.latest_failures = []
        state.latest_scope = scope
        _show_leaderboard(console, state)
        return
    events: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    async def on_progress(event: dict[str, Any]) -> None:
        events.append(event)

    async def execute() -> dict[str, Any]:
        return await run_batch_with_progress(
            suite_id=state.suite_id,
            model_id=state.model_id,
            prompt_condition=PROMPT_CONDITION,
            reasoning={"effort": state.reasoning_effort},
            scenario_ids=scenario_ids,
            progress_callback=on_progress,
        )

    async def run_with_progress() -> dict[str, Any]:
        task = asyncio.create_task(execute())
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            progress_task = progress.add_task(f"Running {scope}", total=len(scenario_ids))
            processed = 0
            while not task.done():
                while processed < len(events):
                    event = events[processed]
                    processed += 1
                    if event["event"] == "scenario_started":
                        progress.update(progress_task, description=f"Running {event['scenario_id']}")
                    elif event["event"] == "scenario_completed":
                        progress.advance(progress_task)
                    elif event["event"] == "scenario_failed":
                        failures.append(event["failure"])
                        progress.advance(progress_task)
                await asyncio.sleep(0.1)
            result = await task
            while processed < len(events):
                event = events[processed]
                processed += 1
                if event["event"] == "scenario_failed":
                    failures.append(event["failure"])
                if event["event"] in {"scenario_completed", "scenario_failed"}:
                    progress.advance(progress_task)
            return result

    try:
        batch = asyncio.run(run_with_progress())
    except Exception as exc:
        state.last_error = str(exc)
        _wait_for_key(console, f"Batch failed: {exc}")
        return
    state.latest_batch = batch
    state.latest_result = None
    batch_failures = batch.get("failures", [])
    state.latest_failures = failures or [dict(item) for item in batch_failures if isinstance(item, dict)]
    state.latest_scope = scope
    _show_leaderboard(console, state)


def _fake_result(state: MicroTuiState, scenario_id: str) -> dict[str, Any]:
    scenario = state.scenarios_by_id.get(scenario_id) or load_scenario(scenario_id)
    action = scenario["reference_policy"]["action"]
    return {
        "schema_version": "v1",
        "run_id": f"micro-tui-test-{scenario_id}",
        "suite_id": scenario["suite_id"],
        "scenario_id": scenario["scenario_id"],
        "category": scenario["category"],
        "model": {
            "openrouter_model_id": state.model_id,
            "model_display_name": state.display_name,
            "reasoning": {"effort": state.reasoning_effort},
        },
        "prompt_condition": PROMPT_CONDITION,
        "outcome": {
            "action": {
                **action,
                "public_message": action.get("public_message", "TUI test mode selected the reference action."),
                "private_thought": action.get("private_thought", "TUI test mode exercised the run flow without OpenRouter."),
            },
            "retry_used": False,
            "fallback_used": False,
            "fallback_reason": None,
            "latency_ms": 0,
        },
        "score": {
            "total": 1.0,
            "label": "preferred",
            "breakdown": [
                {
                    "criterion_id": "tui_test",
                    "points": 1.0,
                    "max_points": 1.0,
                    "passed": True,
                    "message": "Synthetic TUI test result.",
                }
            ],
        },
    }


def _show_result(console: Console, result: dict[str, Any]) -> None:
    console.clear()
    console.print(Panel(f"Run: {result['run_id']}", title="Result Inspector", border_style="cyan"))
    action = result["outcome"]["action"]
    console.print(f"[bold]Scenario[/bold] {result['scenario_id']}")
    console.print(f"[bold]Category[/bold] {result['category']}   [bold]Model[/bold] {result['model']['openrouter_model_id']}")
    console.print(f"[bold]Action[/bold] {action['action']} {action.get('args', {})}")
    console.print(f"[bold]Score[/bold] {result['score']['total']} {result['score']['label']}")
    console.print(f"[bold]Retry[/bold] {result['outcome']['retry_used']}   [bold]Latency[/bold] {result['outcome']['latency_ms']} ms")
    console.print(f"[bold]Public[/bold] {action.get('public_message', '') or '-'}")
    console.print(f"[bold]Private[/bold] {action.get('private_thought', '') or '-'}")
    _print_score(console, result["score"])
    _wait_for_key(console)


def _print_score(console: Console, score: dict[str, Any]) -> None:
    table = Table(title=f"Score Breakdown: {score['total']} {score['label']}", expand=True)
    table.add_column("Criterion")
    table.add_column("Points")
    table.add_column("Passed")
    table.add_column("Message")
    for item in score["breakdown"]:
        table.add_row(
            item["criterion_id"],
            f"{item['points']}/{item['max_points']}",
            "yes" if item["passed"] else "no",
            item["message"],
        )
    console.print(table)


def _show_leaderboard(console: Console, state: MicroTuiState) -> None:
    console.clear()
    if state.latest_batch is not None:
        leaderboard = state.latest_batch["leaderboard"]
        failures = state.latest_failures
        title = f"Leaderboard: {state.latest_scope}"
    elif state.latest_result is not None:
        leaderboard = build_leaderboard([state.latest_result])
        failures = []
        title = f"Leaderboard: {state.latest_scope}"
    else:
        leaderboard = build_leaderboard([])
        failures = []
        title = "Leaderboard"
    table = Table(title=title, expand=True)
    for column in ("Model", "Scenarios", "Avg", "Retry", "Invalid", "Latency"):
        table.add_column(column)
    for row in leaderboard.get("rows", []):
        table.add_row(
            row["model"],
            str(row["scenario_count"]),
            str(row["average_score"]),
            str(row["retry_rate"]),
            str(row["invalid_rate"]),
            str(row["average_latency_ms"]),
        )
    if not leaderboard.get("rows"):
        table.add_row("-", "0", "0", "0", "0", "0")
    console.print(table)
    _print_category_scores(console, leaderboard)
    _print_failures(console, failures)
    _wait_for_key(console)


def _print_category_scores(console: Console, leaderboard: dict[str, Any]) -> None:
    breakdown = leaderboard.get("category_breakdown", {})
    if not breakdown:
        return
    table = Table(title="Category Scores", expand=True)
    table.add_column("Model")
    for category in CATEGORIES:
        if category != "ALL":
            table.add_column(category)
    for model, scores in breakdown.items():
        table.add_row(model, *[str(scores.get(category, "-")) for category in CATEGORIES if category != "ALL"])
    console.print(table)


def _print_failures(console: Console, failures: list[dict[str, Any]]) -> None:
    if not failures:
        console.print(Panel("No failed scenarios.", title="Failures", border_style="green"))
        return
    table = Table(title=f"Failures ({len(failures)})", expand=True)
    table.add_column("Scenario")
    table.add_column("Model")
    table.add_column("Error")
    for failure in failures[:20]:
        table.add_row(str(failure.get("scenario_id")), str(failure.get("model")), str(failure.get("error")))
    console.print(table)


def _show_latest(console: Console, state: MicroTuiState) -> None:
    if state.latest_result is not None:
        _show_result(console, state.latest_result)
        return
    if state.latest_batch is not None:
        _show_leaderboard(console, state)
        return
    _wait_for_key(console, "No run has completed in this TUI session yet.")


def _wait_for_key(console: Console, message: str | None = None) -> None:
    if message:
        renderable: Any = Group(Text(message), Text("Press any key to continue.", style="dim"))
    else:
        renderable = Text("Press any key to continue.", style="dim")
    console.print(Panel(renderable, border_style="dim"))
    _read_key()
