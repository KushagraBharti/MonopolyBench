import type { ReplayStep } from '@/net/contracts';

/** Existing saved runs may wrap the original event instead of flattening it. */
export type SavedReplayStep = Partial<ReplayStep> & {
  step_index: number;
  seq?: number;
  type?: string;
  decision_id?: string | null;
  event?: {
    type?: string;
    seq?: number;
    event_id?: string;
    turn_index?: number;
    actor?: ReplayStep['actor'];
    payload?: Record<string, unknown>;
  };
};

/** A UI projection only: leave canonical replay files and protocol objects untouched. */
export function replayPresentation(step: SavedReplayStep): ReplayStep {
  const event = step.event;
  return {
    step_index: step.step_index,
    event_type: step.event_type ?? event?.type ?? step.type ?? 'UNKNOWN_EVENT',
    event_seq: step.event_seq ?? event?.seq ?? step.seq ?? null,
    event_id: step.event_id ?? event?.event_id ?? null,
    turn_index: step.turn_index ?? event?.turn_index ?? null,
    actor: step.actor ?? event?.actor ?? null,
    payload: { ...(step.decision_id ? { decision_id: step.decision_id } : {}), ...(step.payload ?? event?.payload ?? {}) },
  };
}
