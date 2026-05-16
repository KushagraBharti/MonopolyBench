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
  prompt_conditions: string[];
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
  prompt_condition: string;
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
