import { expect, it } from 'vitest';
import { replayPresentation } from './replayPresentation';

it('presents wrapped saved events with their original labels, payloads, actor and zero sequence', () => {
  const wrapped = { step_index: 0, seq: 0, turn_index: 0, type: 'PROPERTY_PURCHASED', event: { type: 'PROPERTY_PURCHASED', actor: { kind: 'PLAYER', player_id: 'p1' }, payload: { space_index: 6, price: 100 } } };
  const original = structuredClone(wrapped);
  expect(replayPresentation(wrapped)).toMatchObject({ event_type: 'PROPERTY_PURCHASED', event_seq: 0, turn_index: 0, actor: wrapped.event.actor, payload: wrapped.event.payload });
  expect(wrapped).toEqual(original);
});
it('preserves the documented flat replay presentation and decision reference', () => {
  expect(replayPresentation({ step_index: 5, event_type: 'LLM_DECISION_REQUESTED', event_seq: 12, decision_id: 'd1', payload: { player_id: 'p2' } })).toMatchObject({ event_type: 'LLM_DECISION_REQUESTED', event_seq: 12, payload: { player_id: 'p2', decision_id: 'd1' } });
});
