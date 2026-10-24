import { create } from 'zustand'
import type { CloudLive } from '@contracts/cloud'
import type { StateSnapshot, Event } from '@/net/contracts'

type View = { snapshot: StateSnapshot | null; events: Event[]; commit: number; generation: number }
type CloudState = { views: Record<string, View>; receive: (message: CloudLive) => void }
export const useCloudStore = create<CloudState>(set => ({
  views: {},
  receive: message => set(state => {
    const previous = state.views[message.job_id]
    if (previous && message.recovery_generation === previous.generation && message.commit_seq <= previous.commit) return state
    const reset = message.reset || !previous || message.recovery_generation !== previous.generation
    return { views: { ...state.views, [message.job_id]: {
      snapshot: message.snapshot,
      events: [...(reset ? [] : previous.events), ...message.events].slice(-500),
      commit: message.commit_seq,
      generation: message.recovery_generation,
    } } }
  }),
}))
