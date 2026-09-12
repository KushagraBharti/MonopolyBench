import { describe, expect, it } from 'vitest';
import type { Event, StateSnapshot } from '@/net/contracts';
import { blenderPosition, developmentVisible, PresentationCursor } from './presentation';

const snapshot = (run = 'one', turn = 1): StateSnapshot => ({ schema_version: 'v1', run_id: run, turn_index: turn, phase: 'START_TURN', active_player_id: 'p1', players: [], board: [], bank: { houses_remaining: 32, hotels_remaining: 12 } });
const dice = (seq: number, run = 'one'): Event => ({ schema_version: 'v1', run_id: run, seq, event_id: `${run}-${seq}`, turn_index: 1, ts_ms: 0, actor: { kind: 'ENGINE', player_id: null }, type: 'DICE_ROLLED', payload: { d1: 3, d2: 5, is_double: false } });
describe('render-only event delivery', () => {
  it('hydrates without playing historical effects', () => {
    const r = new PresentationCursor();
    expect(r.accept(snapshot(), [dice(2), dice(1)], 'live', true)).toMatchObject({ events: [], immediate: true, reset: true });
    expect(r.accept(snapshot(), [dice(3), dice(2)], 'live', true).events.map(e => e.seq)).toEqual([3]);
  });
  it('deduplicates a batch and subsequent redelivery', () => {
    const r = new PresentationCursor(); r.accept(snapshot(), [], 'live', true);
    expect(r.accept(snapshot(), [dice(2), dice(1), dice(2)], 'live', true).events.map(e => e.seq)).toEqual([1, 2]);
    expect(r.accept(snapshot(), [dice(1), dice(2)], 'live', true).events).toEqual([]);
  });
  it('still applies a newer snapshot when every event is a duplicate', () => {
    const r = new PresentationCursor(); r.accept(snapshot(), [], 'live', true);
    r.accept(snapshot(), [dice(1)], 'live', true);
    const next = snapshot('one', 2);
    expect(r.accept(next, [dice(1)], 'live', true)).toMatchObject({ snapshot: next, events: [], reset: false });
  });
  it('does not let a stale run poison the active cursor', () => {
    const r = new PresentationCursor(); r.accept(snapshot(), [], 'live', true);
    expect(r.accept(snapshot(), [dice(100, 'old'), dice(1)], 'live', true).events.map(e => e.seq)).toEqual([1]);
  });
  it('resets on a new run, backward seek, and explicit same-turn replay seek', () => {
    const r = new PresentationCursor(); r.accept(snapshot('one', 8), [dice(10)], 'live', true);
    expect(r.accept(snapshot('two', 8), [dice(1, 'two')], 'live', true).immediate).toBe(true);
    expect(r.accept(snapshot('two', 3), [dice(2, 'two')], 'live', true).immediate).toBe(true);
    expect(r.accept(snapshot('two', 3), [dice(3, 'two')], 'seek:42', true).immediate).toBe(true);
  });
  it('suppresses catch-up after reconnection and reduced-motion intervals', () => {
    const r = new PresentationCursor(); r.accept(snapshot(), [], 'connected:1', true);
    expect(r.accept(snapshot(), [dice(1)], 'connected:2', true).events).toEqual([]);
    expect(r.accept(snapshot(), [dice(2)], 'connected:2', false)).toMatchObject({ events: [], immediate: true });
    expect(r.accept(snapshot(), [dice(2), dice(3)], 'connected:2', true).events.map(e => e.seq)).toEqual([3]);
  });
  it('clears the prior run when stopped', () => {
    const r = new PresentationCursor(); r.accept(snapshot(), [dice(1)], 'live', true);
    expect(r.accept(null, [], 'live', true)).toMatchObject({ snapshot: null, immediate: true, events: [] });
  });
});
describe('snapshot appearance', () => {
  const property = { index: 6, kind: 'PROPERTY' as const, name: 'Oriental Avenue', group: 'LIGHT_BLUE', price: 100, owner_id: 'p1', mortgaged: false, houses: 4, hotel: false };
  it('shows four slots and lets a supplied hotel replace them', () => {
    expect([0, 1, 2, 3].map(i => developmentVisible(property, 'house', i))).toEqual([true, true, true, true]);
    expect(developmentVisible({ ...property, hotel: true }, 'house', 0)).toBe(false);
    expect(developmentVisible({ ...property, hotel: true }, 'hotel', 0)).toBe(true);
    expect(developmentVisible({ ...property, houses: 1 }, 'house', 1)).toBe(false);
    expect(developmentVisible(undefined, 'hotel', 0)).toBe(false);
  });
  it('maps authored coordinates without changing scale', () => {
    expect(blenderPosition([-5.19, -5.25, .405])).toEqual([-5.19, .405, 5.25]);
  });
});
