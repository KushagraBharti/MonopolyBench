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
  /** Pause threshold on recorded spend in USD. Not a hard cap: in-flight calls may overshoot. */
  cost_budget?: number | null
  response_policy?: { version: string; fallback_models: Record<string, string>; stages: string[]; trigger: string; max_resolver_calls: number }
}
export interface CloudJob {
  job_id: string; run_id: string; kind: 'single' | 'smoke' | 'campaign'; status: JobStatus
  campaign_id: string | null; cell_index?: number | null; config: CloudConfig; snapshot: StateSnapshot | null
  commit_seq: number; created_at: number; started_at: number | null; last_progress_at: number | null
  ended_at: number | null; outcome: { winner_player_id?: string; reason?: string } | null
  elapsed_seconds: number | null; progress_age_seconds: number | null
  rerun_of_job_id: string | null
  pause_reason: string | null; replay_status: string | null; export_status: string | null
  recovered: boolean; repaired: boolean; allowed_actions: string[]; cost: ExecutionCost
  slow: boolean
  snapshot_kind?: 'initial_preview' | 'committed'
}
export interface CloudLive {
  schema_version: 'v2'; type: 'HELLO' | 'SNAPSHOT' | 'EVENT'
  job_id: string; run_id: string; commit_seq: number; recovery_generation: number
  snapshot: StateSnapshot | null; events: Event[]; reset: boolean
}
export interface CampaignReadiness { can_start: boolean; reasons: string[] }
/** Planned game for one board seed and one cyclic seat rotation. */
export interface CampaignPlannedCell {
  cell_index: number; run_id: string; seed: number; execution_rank: number; models_by_seat: string[]
}
export interface CampaignCell extends Partial<CampaignPlannedCell> {
  cell_index: number; seed: number; execution_rank: number
  job_id: string | null; job_status: JobStatus | null; rerun_count: number
  status?: string; not_started_reason?: string | null
  /** The game for this cell once it has been started, else null. */
  game?: CloudJob | null
  /** Unstarted cells allow 'start'; started cells mirror their job's controls. */
  allowed_actions?: string[]
}
export interface CampaignConfig {
  campaign_id?: string; study_label?: string; seeds?: number[]; concurrency?: number
  model_roster?: string; seat_permutation?: string; max_turns?: number | null
  budget_policy?: string; billing?: Record<string, string>
  /** Optional per-game pause threshold on recorded spend in USD. */
  cost_budget?: number | null
  research_freeze?: Record<string, { path: string; sha256: string; content?: unknown }>
  [key: string]: unknown
}
export interface CloudCampaign {
  campaign_id: string; display_name?: string; status: string; config?: CampaignConfig
  config_sha256?: string; git_sha?: string; image_digest?: string; created_at?: number
  readiness?: CampaignReadiness
  cells: CampaignCell[]
}
/** POST /api/campaigns/prepare: persisted seed draw, no games or provider calls. */
export interface CampaignPrepareRequest { name: string; seed_blocks: number; concurrency: number; cost_budget?: number | null }
export interface CampaignPreparation {
  preparation_id: string; config: CampaignConfig; cells: CampaignPlannedCell[]
  readiness: CampaignReadiness; git_sha: string; image_digest: string
}
/** POST /api/campaigns/create: freezes a preparation; never starts games. */
export interface CampaignCreateRequest { preparation_id: string; idempotency_key: string }
/** POST /api/games/prepare (count 1) and /api/smoke/prepare (count 1..20, max_turns 5..10). No games start. */
export interface GamePrepareRequest {
  models: string[]; effort: 'low' | 'medium' | 'high'; max_turns: number | null; cost_budget: number | null; count?: number
}
export interface GamePreparation { preparation_id: string; configs: CloudConfig[]; created_at: number; [key: string]: unknown }
/** POST /api/games and /api/smoke: starts the prepared games. */
export interface GameStartRequest { preparation_id: string; idempotency_key: string }
