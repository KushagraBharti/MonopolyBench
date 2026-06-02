import type { StateSnapshot } from "./state";

export type ArtifactKind = "json" | "jsonl";

export interface ArtifactIndexEntry {
  name: string;
  path: string;
  exists: boolean;
  kind: ArtifactKind;
}

export interface ArtifactIndex {
  run_id: string;
  artifacts: ArtifactIndexEntry[];
}

export interface JsonArtifact<T = unknown> {
  kind: "json";
  content: T;
}

export interface JsonlArtifact<T = unknown> {
  kind: "jsonl";
  rows: T[];
}

export type RunArtifact<T = unknown> = (JsonArtifact<T> | JsonlArtifact<T>) & {
  run_id: string;
  artifact: string;
};

export type BatchArtifact<T = unknown> = (JsonArtifact<T> | JsonlArtifact<T>) & {
  batch_id: string;
  artifact: string;
};

export interface SnapshotIndexEntry {
  name: string;
  path: string;
}

export interface SnapshotIndex {
  run_id: string;
  snapshots: SnapshotIndexEntry[];
}

export interface ArtifactManifestEntry {
  label: string;
  path: string;
  relative_path: string;
  exists: boolean;
  bytes?: number;
  sha256?: string;
}

export interface ArtifactManifest {
  schema_version: "v1";
  manifest_version: "artifact_manifest_v1" | "batch_artifact_manifest_v1";
  run_id?: string;
  batch_dir?: string;
  run_dir?: string;
  created_at?: string;
  artifacts: ArtifactManifestEntry[];
}

export interface ReplayReport {
  schema_version: "v1";
  replay_report_version: string;
  run_id?: string;
  status: string;
  original_event_count?: number;
  replayed_event_count?: number;
  original_event_hash?: string | null;
  replayed_event_hash?: string | null;
  [key: string]: unknown;
}

export interface ReplayStep {
  schema_version?: "v1";
  replay_step_version?: "replay_step_v1";
  step_index: number;
  event_seq?: number | null;
  event_id?: string | null;
  turn_index?: number | null;
  event_type: string;
  actor?: { kind?: string; player_id?: string | null } | null;
  payload?: Record<string, unknown>;
}

export interface ReplayFlag {
  schema_version?: "v1";
  replay_flag_version?: "replay_flag_v1";
  flag_id?: string;
  step_index?: number;
  event_seq?: number | null;
  turn_index?: number | null;
  event_type?: string;
  flag_type?: string;
  label?: string;
  severity?: string;
  decision_id?: string | null;
}

export interface TraceFinding {
  schema_version?: "v1";
  finding_id?: string;
  finding_type?: string;
  kind?: string;
  severity?: string;
  status?: string;
  run_id?: string;
  decision_id?: string | null;
  event_id?: string | null;
  event_seq?: number | null;
  event_seq_start?: number | null;
  event_seq_end?: number | null;
  turn_index?: number | null;
  player_id?: string | null;
  model_id?: string | null;
  human_review_required?: boolean;
  human_review_status?: string;
  evidence?: unknown;
  summary?: string | null;
}

export interface ReviewQueueItem {
  queue_item_id: string;
  run_id?: string;
  batch_id?: string | null;
  decision_id?: string | null;
  turn_index?: number | null;
  player_id?: string | null;
  model_id?: string | null;
  finding_ids?: string[];
  failure_ids?: string[];
  severity?: string;
  reason_for_review?: string;
  suggested_labels?: string[];
  artifact_paths?: Record<string, string>;
  status?: string;
}

export interface ReviewLabel {
  schema_version?: "v1";
  label_version?: "review_label_v1";
  label_id: string;
  run_id: string;
  queue_item_id?: string | null;
  reviewer_id: string;
  reviewed_at: string;
  selected_labels: string[];
  confidence?: number | null;
  notes?: string;
  adjudication_status?: string;
  gold_label?: boolean;
  evidence_references?: unknown[];
}

export interface ReviewSummary {
  schema_version?: "v1";
  review_summary_version: "review_summary_v1";
  run_id: string;
  label_count: number;
  gold_label_count?: number;
  by_label: Record<string, number>;
  by_reviewer: Record<string, number>;
}

export interface ScorecardArtifact {
  schema_version: "v1";
  scorecard_version: string;
  run: Record<string, unknown>;
  players: Record<string, unknown>[];
  [key: string]: unknown;
}

export interface UsageReport {
  schema_version: "v1";
  usage_accounting_version: string;
  source: string;
  local_tokenizer_estimates_used: false;
  totals?: Record<string, unknown>;
  by_model?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface BatchListItem {
  batch_id: string;
  batch_dir: string;
  run_count?: number | null;
  manifest_exists: boolean;
}

export interface BatchList {
  batches: BatchListItem[];
}

export interface BatchDetail {
  batch_id: string;
  batch_dir: string;
  manifest: Record<string, unknown>;
  config: Record<string, unknown>;
  leaderboard: Record<string, unknown>;
}

export interface BatchArtifactIndex {
  batch_id: string;
  artifacts: ArtifactIndexEntry[];
  model_cards: {
    card_id: string;
    json_path: string;
    markdown_path: string;
  }[];
}

export interface BatchModelCard {
  batch_id: string;
  card_id: string;
  json: Record<string, unknown>;
  markdown: string | null;
}

export interface RunListItem {
  run_id: string;
  run_dir: string;
  mode?: string | null;
  seed?: number | null;
  winner_player_id?: string | null;
  turn_count?: number | null;
  reason?: string | null;
  summary_exists?: boolean;
  scorecard_exists?: boolean;
  replay_report_exists?: boolean;
}

export interface RunList {
  runs: RunListItem[];
}

export interface RunDetail {
  run_id: string;
  run_dir: string;
  summary: Record<string, unknown>;
  run_config: Record<string, unknown>;
  players: Record<string, unknown>;
  seat_assignment: Record<string, unknown>;
  scorecard: Record<string, unknown>;
  usage: Record<string, unknown>;
  replay_report: Record<string, unknown>;
  trace_summary: Record<string, unknown>;
  failure_summary: Record<string, unknown>;
}

export interface ModelDetail {
  model_id: string;
  game_count: number;
  win_count: number;
  win_rate?: number | null;
  average_final_net_worth?: number | null;
  total_cost: number;
  total_tokens: number;
  runs: Record<string, unknown>[];
}

export type SnapshotContent = StateSnapshot;
