export type PromptPipelineMarker = {
  status: 'unchanged'
  note?: string
}

export type LongHorizonSeedEntry = {
  seed: number
  label: string
  rationale: string
}

export type LongHorizonSeedCohort = {
  cohort_id: string
  version: string
  description: string
  intended_use: string
  source_cohorts?: string[]
  seeds: LongHorizonSeedEntry[]
}

export type LongHorizonSeedRegistry = {
  schema_version: 'v1'
  registry_version: 'long_horizon_seed_registry_v1'
  benchmark_id: 'monopoly-long-v1'
  description: string
  cohorts: Record<string, LongHorizonSeedCohort>
  prompt_pipeline: PromptPipelineMarker
}

export type ResearchActorType = 'llm' | 'baseline'

export type ResearchActor = {
  actor_id: string
  actor_type: ResearchActorType
  baseline_id?: string
  display_name: string
  openrouter_model_id?: string
  reasoning?: { effort: 'low' | 'medium' | 'high' } | null
  top_p?: number | null
  enabled: boolean
  cost_budget_group: string
  notes: string
}

export type LongHorizonModelRoster = {
  roster_id: string
  version: string
  description: string
  actor_ids: string[]
}

export type LongHorizonModelRosterRegistry = {
  schema_version: 'v1'
  registry_version: 'long_horizon_model_roster_registry_v1'
  benchmark_id: 'monopoly-long-v1'
  description: string
  actors: Record<string, ResearchActor>
  rosters: Record<string, LongHorizonModelRoster>
  prompt_pipeline: PromptPipelineMarker
}

export type LongHorizonCampaignConfig = {
  schema_version: 'v1'
  campaign_config_version: 'long_horizon_campaign_config_v1'
  campaign_id: string
  benchmark_id: 'monopoly-long-v1'
  seed_cohort: string
  model_roster: string
  repetitions_per_seed: number
  seat_permutation: 'latin_square' | 'full' | 'seeded_random' | 'configured_order'
  max_turns: number
  max_trade_exchanges?: number
  max_auction_actions?: number
  cost_budget?: number
  concurrency?: number
  budget_policy?: string
  dry_run: boolean
  resume?: boolean
  continue_on_failure?: boolean
  replay_after_run?: boolean
  build_scorecard_after_run?: boolean
  build_trace_after_run?: boolean
  build_failure_taxonomy_after_run?: boolean
  prompt_pipeline: PromptPipelineMarker
}
