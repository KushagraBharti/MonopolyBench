import { useCallback, useEffect, useRef, useState } from 'react'
import { CLOUD_API, cloudRequest, type CampaignCell, type CloudCampaign, type CloudExport, type CloudJob } from '@/net/jobs'
import type { ResumeAllResult } from '@contracts/cloud'

/** Bulk recovery never overrides manual holds; retain the server's reasons in the UI. */
export async function retryEligibleGames(): Promise<string> {
  const result = await cloudRequest<ResumeAllResult>('/resume-all', {})
  const skipped = result.skipped ?? []
  const waiting = result.waiting_for_worker ?? []
  return [
    skipped.length ? `${skipped.length} games stayed paused. ${[...new Set(skipped.flatMap(job => job.reasons))].join(' ')}` : '',
    waiting.length ? `${waiting.length} games are finishing an in-flight request. Retry after their workers stop.` : '',
  ].filter(Boolean).join(' ')
}

/** Polls a cloud endpoint. `replace` accepts a mutation response and discards older in-flight polls. */
export function usePoll<T>(path: string) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState('')
  const [nonce, setNonce] = useState(0)
  const generation = useRef(0)
  useEffect(() => {
    let active = true
    let timer: ReturnType<typeof setTimeout>
    const load = async () => {
      const gen = generation.current
      try {
        const value = await cloudRequest<T>(path)
        if (active && gen === generation.current) { setData(value); setError('') }
      } catch (e) {
        if (active && gen === generation.current) setError(errorText(e))
      } finally {
        if (active) timer = setTimeout(load, 5000)
      }
    }
    void load()
    return () => { active = false; clearTimeout(timer) }
  }, [path, nonce])
  const refresh = useCallback(() => { generation.current += 1; setNonce(n => n + 1) }, [])
  const replace = useCallback((value: T) => { generation.current += 1; setData(value); setError('') }, [])
  return { data, error, refresh, replace }
}

export function errorText(e: unknown) {
  return e instanceof Error ? e.message : String(e)
}

/** Server messages that mean the model connection check (preflight) is missing, stale or failed. */
export function needsConnectionCheck(text: string) {
  return /preflight|connection check|model connection/i.test(text)
}

export interface ModelInfo { name: string; lab: string; mark: string; color: string; ink: string }
export const MODEL_INFO: Record<string, ModelInfo> = {
  'anthropic/claude-opus-5.5': { name: 'Claude Opus 5.5', lab: 'Anthropic', mark: 'A', color: '#ff6b1a', ink: '#0a0a0a' },
  'openai/gpt-6.1-sol': { name: 'GPT-6.1 Sol', lab: 'OpenAI', mark: 'O', color: '#00e639', ink: '#0a0a0a' },
  'google/gemini-4-argon': { name: 'Gemini 4 Argon', lab: 'Google', mark: 'G', color: '#3a0fff', ink: '#ffffff' },
  'x-ai/grok-4.7': { name: 'Grok 4.7', lab: 'xAI', mark: 'X', color: '#f5007a', ink: '#ffffff' },
}
export const ROSTER = Object.keys(MODEL_INFO)

export function modelInfo(id: string): ModelInfo {
  return MODEL_INFO[id] ?? { name: id.split('/').pop() ?? id, lab: id.split('/')[0] ?? '', mark: (id.split('/').pop() ?? '?')[0].toUpperCase(), color: '#e8e7e4', ink: '#0a0a0a' }
}

export type Tone = 'idle' | 'live' | 'done' | 'warn' | 'bad'
const JOB_STATUS: Record<string, [string, Tone]> = {
  queued: ['Waiting for a slot', 'idle'],
  running: ['Playing', 'live'],
  paused: ['Paused', 'warn'],
  recovering: ['Recovering', 'warn'],
  finalizing: ['Wrapping up', 'live'],
  completed: ['Finished', 'done'],
  failed: ['Failed', 'bad'],
  cancelled: ['Cancelled', 'bad'],
}
export function jobStatus(status: string | null | undefined): [string, Tone] {
  if (!status) return ['Not started', 'idle']
  return JOB_STATUS[status] ?? [capitalize(status), 'idle']
}

/** A cell's game status. The embedded game is the freshest source when the server sends it. */
export function cellJobStatus(cell: CampaignCell) {
  return cell.game?.status ?? (cell.job_id ? cell.job_status : cell.status === 'cancelled' ? 'cancelled' : null)
}
export function cellJobId(cell: CampaignCell) {
  return cell.game?.job_id ?? cell.job_id
}

/** Placeholder text for a game with no saved board yet. */
export function waitingText(status: string | null | undefined) {
  if (status === 'queued') return 'Waiting for a slot. Board appears after the first saved move.'
  if (status === 'cancelled' || status === 'failed') return 'Stopped before the first saved move.'
  return 'Board appears after the first saved move.'
}

export function cellStatus(cell: CampaignCell): [string, Tone] {
  if (!cellJobId(cell) && cell.not_started_reason === 'code_identity_mismatch') return ['Blocked: code changed', 'bad']
  return jobStatus(cellJobStatus(cell))
}

export function campaignStatus(campaign: CloudCampaign): [string, Tone] {
  const counts = cellCounts(campaign.cells)
  if (campaign.status === 'draft') return ['Draft file', 'idle']
  if (campaign.status === 'done') return counts.stopped ? ['Done, some stopped', 'warn'] : ['Finished', 'done']
  if (campaign.status === 'cancelled') return ['Cancelled', 'bad']
  if (campaign.status === 'running') return ['Running', 'live']
  if (campaign.status === 'paused') return ['Paused', 'warn']
  if (campaign.status === 'frozen') return campaign.readiness?.can_start ? ['Ready to start', 'done'] : ['Saved, not ready', 'warn']
  return [capitalize(campaign.status), 'idle']
}

/** Finished means completed. Stopped means failed or cancelled. Waiting means a game exists but hasn't got a slot yet. */
export function cellCounts(cells: CampaignCell[]) {
  const counts = { total: cells.length, finished: 0, playing: 0, paused: 0, waiting: 0, notStarted: 0, stopped: 0, active: 0, done: false }
  for (const cell of cells) {
    const status = cellJobStatus(cell)
    if (status === 'completed') counts.finished += 1
    else if (!status) counts.notStarted += 1
    else if (status === 'queued') counts.waiting += 1
    else if (status === 'failed' || status === 'cancelled') counts.stopped += 1
    else if (status === 'paused') counts.paused += 1
    else counts.playing += 1
  }
  counts.active = counts.waiting + counts.playing + counts.paused
  counts.done = counts.total > 0 && counts.finished + counts.stopped === counts.total
  return counts
}

export function campaignName(campaign: Pick<CloudCampaign, 'campaign_id' | 'display_name' | 'config'>) {
  return campaign.display_name || (typeof campaign.config?.study_label === 'string' ? campaign.config.study_label : '') || campaign.campaign_id
}

/** Model id per player_id, from the run configuration. Never inferred from seat or color. */
export function playerModels(config: { players: { player_id: string; openrouter_model_id: string }[] }): Record<string, string> {
  return Object.fromEntries(config.players.map(p => [p.player_id, p.openrouter_model_id]))
}

export function jobTitle(job: CloudJob) {
  if (job.kind === 'smoke') return 'Model test'
  if (job.kind === 'single') return 'Single game'
  return typeof job.cell_index === 'number' ? `Campaign game ${job.cell_index + 1}` : 'Campaign game'
}

/** Board number for each seed, in the order seeds were drawn. */
export function boardNumbers(cells: { seed: number; cell_index: number }[]) {
  const order = new Map<number, number>()
  for (const cell of [...cells].sort((a, b) => a.cell_index - b.cell_index)) {
    if (!order.has(cell.seed)) order.set(cell.seed, order.size + 1)
  }
  return order
}

export function duration(seconds: number) {
  if (seconds < 60) return `${Math.floor(seconds)}s`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes} min`
  return `${Math.floor(minutes / 60)} h ${minutes % 60} min`
}

export function capitalize(text: string) {
  return text ? text[0].toUpperCase() + text.slice(1).replace(/_/g, ' ') : text
}

export const ACTION_LABELS: Record<string, string> = { start: 'Start game', pause: 'Pause', resume: 'Resume', cancel: 'Cancel game', archive: 'Archive' }

export const EFFORTS = ['low', 'medium', 'high'] as const
export type Effort = typeof EFFORTS[number]

export function money(value: number) {
  return `$${value.toFixed(2)}`
}

/** Parses the optional spend-pause field. Empty means no threshold. */
export function parseBudget(text: string): { value: number | null; problem: string } {
  const trimmed = text.trim().replace(/^\$/, '')
  if (!trimmed) return { value: null, problem: '' }
  const value = Number(trimmed)
  if (!Number.isFinite(value) || value <= 0) return { value: null, problem: 'Enter an amount above $0, or leave it empty for no pause.' }
  return { value, problem: '' }
}

/** One-line summary of a game's settings: effort, turn limit and spend pause. */
export function settingsLine(config: { players: { reasoning: { effort: string } }[]; max_turns: number | null; cost_budget?: number | null }) {
  const efforts = [...new Set(config.players.map(p => p.reasoning.effort))]
  return [
    `${capitalize(efforts.join('/'))} effort`,
    config.max_turns == null ? 'Full game, no turn limit' : `${config.max_turns} turn limit`,
    config.cost_budget == null ? 'No spend pause' : `Pauses at ${money(config.cost_budget)} recorded spend`,
  ].join(' · ')
}


/** Where a job belongs in the workspace: model tests, standalone games, or a campaign. */
export function jobHome(job: Pick<CloudJob, 'kind' | 'campaign_id'>): { href: string; label: string } {
  if (job.kind === 'smoke') return { href: '/tests', label: 'Tests' }
  if (job.kind === 'campaign' && job.campaign_id) return { href: `/campaigns/${encodeURIComponent(job.campaign_id)}`, label: 'Back to campaign' }
  if (job.kind === 'campaign') return { href: '/campaigns', label: 'Campaigns' }
  return { href: '/games', label: 'Games' }
}

/** Server times are Unix seconds. */
export function when(seconds: number | null | undefined) {
  if (seconds == null) return '—'
  return new Date(seconds * 1000).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
}

export function fileSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`
  if (bytes < 1024 ** 3) return `${(bytes / 1024 ** 2).toFixed(1)} MB`
  return `${(bytes / 1024 ** 3).toFixed(2)} GB`
}

export type ExportGroup = 'single' | 'smoke' | 'campaign'
/** Campaign snapshots and campaign games both group under campaigns. */
export function exportGroup(item: CloudExport): ExportGroup | null {
  if (item.scope === 'campaign') return 'campaign'
  const kind = item.run_kind ?? item.job_kind
  return kind === 'single' || kind === 'smoke' || kind === 'campaign' ? kind : null
}

export function exportKindLabel(item: CloudExport) {
  if (item.scope === 'campaign') return 'Campaign snapshot'
  return item.kind === 'diagnostic' ? 'Diagnostic package (game stopped early)' : 'Finished game package'
}

export function exportName(item: CloudExport) {
  if (item.display_name) return item.display_name
  if (item.scope === 'campaign') return `Campaign snapshot ${item.revision}`
  const group = exportGroup(item)
  if (group === 'smoke') return `Model test ${item.run_id ?? item.scope_id}`
  if (group === 'campaign') return typeof item.cell_index === 'number' ? `Campaign game ${item.cell_index + 1}` : 'Campaign game'
  return `Game ${item.run_id ?? item.scope_id}`
}

/** Authenticated download through the session cookie; no token needed. */
export function exportDownload(item: Pick<CloudExport, 'export_id'>) {
  return `${CLOUD_API}/exports/${encodeURIComponent(item.export_id)}/download`
}

export function exportSource(item: CloudExport): { href: string; label: string } | null {
  if (item.source_url?.startsWith('/')) return { href: item.source_url, label: item.scope === 'campaign' ? 'Open campaign' : 'Open game' }
  if (item.scope === 'campaign') return { href: `/campaigns/${encodeURIComponent(item.scope_id)}`, label: 'Open campaign' }
  return { href: `/games/${encodeURIComponent(item.scope_id)}`, label: 'Open game' }
}

export function newestFirst<T extends { created_at?: number }>(items: T[]) {
  return [...items].sort((a, b) => (b.created_at ?? 0) - (a.created_at ?? 0))
}

const TERMINAL = new Set(['completed', 'failed', 'cancelled'])
/** Why a game's download isn't offered yet. Null when it is ready. */
/** True when the server reports the export bundle could not be built. */
export function exportFailed(job: Pick<CloudJob, 'export_status'>) {
  return job.export_status === 'failed' || job.export_status === 'error'
}

export function downloadWait(job: Pick<CloudJob, 'status' | 'export_status'>) {
  if (job.export_status === 'ready') return null
  if (exportFailed(job)) return 'Download failed to build. Individual files are still available under Details and research, Artifacts; ask the operator to rebuild the export.'
  return TERMINAL.has(job.status) || job.status === 'finalizing' ? 'Download is being prepared.' : 'Download available after the game finishes.'
}
