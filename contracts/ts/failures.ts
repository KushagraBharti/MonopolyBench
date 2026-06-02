export type FindingSeverity = "low" | "medium" | "high";
export type FindingStatus = "deterministic" | "candidate";
export type FindingKind = "failure" | "trace";

export interface FailureFinding {
  schema_version: "v1";
  trace_analyzer_version?: string;
  failure_taxonomy_version: string;
  kind: FindingKind;
  run_id: string;
  finding_id: string;
  finding_type: string;
  severity: FindingSeverity;
  confidence: number;
  status: FindingStatus;
  turn_index?: number | null;
  decision_id?: string | null;
  player_id?: string | null;
  model_id?: string | null;
  event_seq_start?: number | null;
  event_seq_end?: number | null;
  supporting_event_ids?: (string | null)[];
  supporting_action_ids?: (string | null)[];
  supporting_decision_ids?: (string | null)[];
  summary: string;
  details?: Record<string, unknown>;
  derived_metrics?: Record<string, unknown>;
  snapshot_path?: string | null;
  human_review_required: boolean;
  human_review_status: string;
  tags?: string[];
}
