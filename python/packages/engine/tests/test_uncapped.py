from monopoly_engine import Engine
from monopoly_engine.replay import replay_actions, canonical_event_lines


def test_uncapped_skips_turn_limit_and_ends_by_bankruptcy():
    players = [{"player_id": f"p{i}", "name": f"Player {i}"} for i in range(4)]
    engine = Engine(seed=7, players=players, run_id="uncapped", max_turns=None)
    engine.state.turn_index = 1_000_000
    assert not engine._should_end_game()
    for player in engine.state.players[1:]:
        player.bankrupt = True
    assert engine._should_end_game()
    assert engine._stop_reason == "BANKRUPTCY"


def test_uncapped_replay_reaches_same_initial_decision():
    players = [{"player_id": f"p{i}", "name": f"Player {i}"} for i in range(4)]
    engine = Engine(seed=7, players=players, run_id="uncapped", max_turns=None)
    _, events, decision, _ = engine.advance_until_decision(max_steps=10_000)
    assert decision
    replayed = replay_actions(seed=7, players=players, run_id="uncapped", actions=[], max_turns=None)
    assert canonical_event_lines(replayed) == canonical_event_lines(events)
