import type { Action } from "./actions";
import type { DecisionPoint } from "./decisions";

export type MicroScenarioCategory =
  | "BUY_OR_AUCTION"
  | "AUCTION"
  | "TRADE_PROPOSE"
  | "TRADE_RESPONSE"
  | "BUILD_OR_MORTGAGE"
  | "LIQUIDATION"
  | "JAIL"
  | "POST_TURN_STRATEGY";

export type MicroPromptCondition = "live_game";

export interface MicroScoreBreakdown {
  criterion_id: string;
  points: number;
  max_points: number;
  passed: boolean;
  message: string;
}

export interface MicroEvaluation {
  schema_version: "v1";
  scoring_mode: "rubric_v1";
  rubric: Array<{
    criterion_id: string;
    description: string;
    type: string;
    max_points: number;
    params: Record<string, unknown>;
  }>;
}

export interface MicroResearchMetadata {
  schema_version: "micro_research_metadata_v1";
  visibility: "research_only_never_prompt";
  review_status: "draft" | "reviewed_first_pass" | "reviewed_final";
  review_priority: "normal" | "medium" | "high";
  target_capability: string;
  target_behavior: string;
  strategic_tension: string;
  expected_failure_modes: string[];
  taxonomy_tags: string[];
  counterfactual_pair_id: string | null;
  counterfactual_role: "baseline" | "contrast" | null;
  paper_section: string;
  notes_for_researchers: string;
  source_claims: string[];
  source_urls: string[];
  created_by: string;
  last_reviewed_at: string;
  prompt_immutability_checked: true;
}

export interface MicroScenario {
  schema_version: "v1";
  scenario_id: string;
  suite_id: string;
  category: MicroScenarioCategory;
  difficulty: "easy" | "medium" | "hard";
  title: string;
  description: string;
  tags: string[];
  focal_player_id: string;
  decision_point: DecisionPoint;
  evaluation: MicroEvaluation;
  reference_policy: {
    name: string;
    action: Record<string, unknown>;
    rationale: string;
  };
  research_metadata?: MicroResearchMetadata;
  research_sources?: Array<{
    title: string;
    url: string;
    claim: string;
    used_for: string;
  }>;
  notes?: Record<string, unknown>;
}

export interface MicroSuite {
  schema_version: "v1";
  suite_id: string;
  title: string;
  description: string;
  scenario_ids: string[];
  categories: Record<MicroScenarioCategory, { target_count: number; actual_count?: number }>;
  scoring_version: string;
  prompt_conditions: MicroPromptCondition[];
}

export type MicroResearchSuiteFamily = "bias" | "safety" | "counterfactual" | "campaign";

export interface MicroResearchCategory {
  category_id: string;
  title: string;
  description: string;
  target_behavior: string;
  trap_behaviors: string[];
  preferred_behaviors: string[];
  scenario_ids: string[];
  counterfactual_pair_ids?: string[];
  human_review_required: boolean;
  scoring_notes: string;
  source_claims: string[];
  source_urls: string[];
}

export interface MicroResearchSuite {
  schema_version: "v1";
  suite_id: string;
  suite_family: MicroResearchSuiteFamily;
  benchmark_suite_version: string;
  title: string;
  description: string;
  source_suite_id: string;
  scenario_ids: string[];
  categories: MicroResearchCategory[];
  counterfactual_pair_ids?: string[];
  campaign_ids?: string[];
  human_review_required: boolean;
  report_dimensions: string[];
  prompt_pipeline: {
    status: "unchanged";
    note?: string;
  };
}

export interface MicroCounterfactualPair {
  pair_id: string;
  baseline_scenario_id: string;
  contrast_scenario_id: string;
  controlled_difference: string;
  invariant_claims: string[];
  expected_stability_metric: string;
  scoring_notes: string;
  human_review_required: boolean;
}

export interface MicroCounterfactualPairRegistry {
  schema_version: "v1";
  registry_version: "micro_counterfactual_pairs_v1";
  suite_id: string;
  pairs: MicroCounterfactualPair[];
  prompt_pipeline: {
    status: "unchanged";
    note?: string;
  };
}

export interface MicroCampaignDefinition {
  campaign_id: string;
  title: string;
  description: string;
  category: string;
  step_scenario_ids: string[];
  deterministic_opponent_policy: string;
  expected_strategic_path: string[];
  per_step_rubrics: string[];
  final_scoring_notes: string;
  replay_mode: "fixture_sequence" | "engine_replay_required";
  human_review_required: boolean;
}

export interface MicroCampaignRegistry {
  schema_version: "v1";
  registry_version: "micro_campaigns_v1";
  suite_id: string;
  campaigns: MicroCampaignDefinition[];
  prompt_pipeline: {
    status: "unchanged";
    note?: string;
  };
}

export interface MicroExpertLabelTask {
  schema_version: "v1";
  task_id: string;
  task_type: "scenario" | "counterfactual_pair" | "campaign" | "safety_label";
  suite_id: string;
  scenario_id?: string;
  counterfactual_pair_id?: string;
  campaign_id?: string;
  label_dimensions: string[];
  status: "queued" | "completed";
  human_review_only: true;
  prompt_pipeline: {
    status: "unchanged";
    note?: string;
  };
}

export interface MicroExpertLabel {
  schema_version: "v1";
  label_id: string;
  task_id: string;
  reviewer_id: string;
  expertise_level: string;
  label_source: string;
  timestamp: string;
  scenario_id?: string;
  counterfactual_pair_id?: string;
  campaign_id?: string;
  selected_action: Action | null;
  judgment: string;
  rationale: string;
  confidence: number;
  ambiguity_flag: boolean;
  adjudication_status: "single_label" | "pending_adjudication" | "adjudicated";
  inter_rater_group_id?: string | null;
  human_review_only: true;
}

export interface MicroResult {
  schema_version: "v1";
  run_id: string;
  suite_id: string;
  scenario_id: string;
  category: MicroScenarioCategory;
  model: {
    openrouter_model_id: string;
    model_display_name: string;
    reasoning?: Record<string, unknown> | null;
  };
  prompt_condition: MicroPromptCondition;
  outcome: {
    action: Action;
    retry_used: boolean;
    fallback_used: boolean;
    fallback_reason: string | null;
    latency_ms: number | null;
  };
  score: {
    total: number;
    label: "preferred" | "acceptable" | "bad" | "invalid";
    breakdown: MicroScoreBreakdown[];
  };
}
