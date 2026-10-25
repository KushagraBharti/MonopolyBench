import { create } from 'zustand'
import type { CloudLive } from '@contracts/cloud'
import type { StateSnapshot, Event } from '@/net/contracts'

export type CloudView = { runId: string; snapshot: StateSnapshot | null; events: Event[]; commit: number; generation: number }
type CloudState = { views: Record<string, CloudView>; receive: (message: CloudLive) => boolean }

/** A rejected envelope must not update any other panel's presentation state. */
export function mergeCloudView(previous: CloudView | undefined, message: CloudLive): CloudView | undefined {
  if (message.snapshot && message.snapshot.run_id !== message.run_id) return previous
  if (message.events.some(event => event.run_id !== message.run_id)) return previous
  if (previous) {
    if (previous.runId !== message.run_id || message.recovery_generation < previous.generation) return previous
    if (message.commit_seq <= previous.commit) return previous
  }
  // The server's reset marks a transport generation boundary. Journal commits and
  // event sequences remain append-only across recovery, so keep the prior history.
  const events = new Map((previous?.events ?? []).map(event => [event.seq, event]))
  for (const event of message.events) events.set(event.seq, event)
  return {
    runId: message.run_id,
    snapshot: message.snapshot ?? previous?.snapshot ?? null,
    events: [...events.values()].sort((a, b) => a.seq - b.seq).slice(-500),
    commit: message.commit_seq,
    generation: message.recovery_generation,
  }
}

export const useCloudStore = create<CloudState>(set => ({
  views: {},
  receive: message => {
    let accepted = false
    set(state => {
      const previous = state.views[message.job_id]
      const view = mergeCloudView(previous, message)
      if (!view || view === previous) return state
      accepted = true
      return { views: { ...state.views, [message.job_id]: view } }
    })
    return accepted
  },
}))
