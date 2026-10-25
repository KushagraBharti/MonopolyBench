import type { Event, Player, Space, StateSnapshot } from '@/net/contracts'
import type { CloudJob } from '@/net/jobs'
import { getPlayerColor } from '@/domain/monopoly/colors'
import { capitalize, modelInfo } from '../cloudUi'

/** One seat as configured for the run, joined with that player's snapshot state. */
export type Seat = {
  playerId: string
  seat: number
  model: string
  modelName: string
  /** Model name, with the seat number when the same model sits in more than one seat. */
  label: string
  color: string
  player: Player | null
  holdings: Space[]
}

const OWNABLE = new Set<Space['kind']>(['PROPERTY', 'RAILROAD', 'UTILITY'])

/** Seats in configured order. Identity comes from config; cash, jail and ownership from the snapshot. */
export function buildSeats(job: CloudJob, snapshot: StateSnapshot | null): Seat[] {
  const counts = new Map<string, number>()
  for (const p of job.config.players) counts.set(p.openrouter_model_id, (counts.get(p.openrouter_model_id) ?? 0) + 1)
  const byId = new Map((snapshot?.players ?? []).map(p => [p.player_id, p]))
  return job.config.players.map((p, i) => {
    const modelName = modelInfo(p.openrouter_model_id).name
    return {
      playerId: p.player_id,
      seat: i + 1,
      model: p.openrouter_model_id,
      modelName,
      label: (counts.get(p.openrouter_model_id) ?? 0) > 1 ? `${modelName} (seat ${i + 1})` : modelName,
      color: getPlayerColor(p.player_id),
      player: byId.get(p.player_id) ?? null,
      holdings: (snapshot?.board ?? []).filter(s => s.owner_id === p.player_id && OWNABLE.has(s.kind)).sort((a, b) => a.index - b.index),
    }
  })
}

export const TERMINAL = new Set(['completed', 'failed', 'cancelled'])
/** True only while the game can still make moves. */
export function isActiveStatus(status: string | undefined) {
  return status === 'running' || status === 'paused' || status === 'recovering' || status === 'queued'
}

export type PendingDecision = { decisionId: string; playerId: string; type: string; turn: number }

/**
 * The newest decision the engine requested that has no response event yet.
 * Events are newest first. Only meaningful while the job is running.
 */
export function pendingDecision(events: Event[]): PendingDecision | null {
  const answered = new Set<string>()
  for (const event of events) {
    if (event.type === 'LLM_DECISION_RESPONSE') answered.add(event.payload.decision_id)
    if (event.type === 'LLM_DECISION_REQUESTED') {
      if (answered.has(event.payload.decision_id)) return null
      return { decisionId: event.payload.decision_id, playerId: event.payload.player_id, type: event.payload.decision_type, turn: event.turn_index }
    }
    if (event.type === 'GAME_ENDED') return null
  }
  return null
}

export function lastDice(events: Event[], turn: number | undefined) {
  for (const event of events) {
    if (event.turn_index !== turn) return null
    if (event.type === 'DICE_ROLLED') return event.payload
  }
  return null
}

export function decisionLabel(type: string) {
  return capitalize(type.toLowerCase())
}

export function reasonLabel(reason: string | null | undefined) {
  return reason ? reason.toLowerCase().replace(/_/g, ' ') : ''
}

export function money(value: number) {
  return `$${value.toLocaleString('en-US')}`
}
