import type { Event, StateSnapshot } from '@/net/contracts';

export type PresentationUpdate = { snapshot: StateSnapshot | null; events: Event[]; immediate: boolean; reset: boolean };

/** Tracks presentation delivery only. State and legality always come from the engine. */
export class PresentationCursor {
  private run: string | null = null;
  private turn = -1;
  private seq = -1;
  private resetKey: string | number | undefined;
  private initialized = false;
  private seen = new Set<string>();

  accept(snapshot: StateSnapshot | null, events: readonly Event[], resetKey: string | number, animate: boolean): PresentationUpdate {
    const reset = !this.initialized || this.run !== (snapshot?.run_id ?? null) ||
      this.resetKey !== resetKey || (snapshot !== null && snapshot.turn_index < this.turn);
    const relevant = events.filter(e => e.run_id === snapshot?.run_id).sort((a, b) => a.seq - b.seq);
    if (reset) {
      this.seen.clear();
      this.seq = -1;
    }
    const fresh: Event[] = [];
    for (const event of relevant) {
      if (event.seq <= this.seq || this.seen.has(event.event_id)) continue;
      this.seq = event.seq;
      this.seen.add(event.event_id);
      if (!reset && animate) fresh.push(event);
    }
    // The seq cursor also protects evicted IDs; bound memory during long research runs.
    if (this.seen.size > 1024) this.seen = new Set([...this.seen].slice(-512));
    this.initialized = true;
    this.run = snapshot?.run_id ?? null;
    this.turn = snapshot?.turn_index ?? -1;
    this.resetKey = resetKey;
    return { snapshot, events: fresh, immediate: reset || !animate, reset };
  }
}

export function developmentVisible(space: StateSnapshot['board'][number] | undefined, kind: 'house' | 'hotel', slot: number): boolean {
  return Boolean(space && (kind === 'hotel' ? space.hotel : !space.hotel && slot < space.houses));
}

export const blenderPosition = ([x, y, z]: readonly number[]): [number, number, number] => [x, z, -y];

// Values are orientations of the exported die's faces, never generated dice outcomes.
export const DIE_NORMALS: Record<number, [number, number, number]> = {
  1: [1, 0, 0], 2: [0, -1, 0], 3: [0, 0, -1],
  4: [0, 0, 1], 5: [0, 1, 0], 6: [-1, 0, 0],
};
