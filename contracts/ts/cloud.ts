import type { StateSnapshot } from './state'
import type { Event } from './events'

export type JobStatus = 'queued' | 'running' | 'paused' | 'recovering' | 'finalizing' | 'completed' | 'failed' | 'cancelled'
export interface ExecutionCost {
  known_total: number; openrouter_charge: number; provider_charge: number
  missing_calls: number; unknown_calls: number; calls: number
}
export interface CloudPlayer {
  player_id: string; name: string; openrouter_model_id: string
  reasoning: { effort: 'low' | 'medium' | 'high' }; provider: { only: string[] }
}
export interface CloudConfig {
  seed: number; run_id: string; players: CloudPlayer[]; max_turns: number | null; git_sha: string
}
export interface CloudJob {
  job_id: string; run_id: string; kind: 'smoke' | 'campaign'; status: JobStatus
  campaign_id: string | null; config: CloudConfig; snapshot: StateSnapshot | null
  commit_seq: number; created_at: number; started_at: number | null; last_progress_at: number | null
  pause_reason: string | null; replay_status: string | null; export_status: string | null
  recovered: boolean; repaired: boolean; allowed_actions: string[]; cost: ExecutionCost
  slow: boolean
}
export interface CloudLive {
  schema_version: 'v2'; type: 'HELLO' | 'SNAPSHOT' | 'EVENT'
  job_id: string; run_id: string; commit_seq: number; recovery_generation: number
  snapshot: StateSnapshot | null; events: Event[]; reset: boolean
}
export interface CloudCampaign {
  campaign_id: string; status: string; config?: Record<string, unknown>
  cells: { cell_index: number; seed: number; job_id: string | null; job_status: string | null; execution_rank: number; rerun_count: number }[]
}
