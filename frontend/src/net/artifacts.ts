import { getApiBaseUrl } from '@/net/ws';
import type {
  ArtifactIndex,
  BatchArtifact,
  BatchArtifactIndex,
  BatchDetail,
  BatchList,
  BatchModelCard,
  ModelDetail,
  ReviewLabel,
  ReviewQueueItem,
  ReviewSummary,
  RunDetail,
  RunArtifact,
  RunList,
  SnapshotIndex,
  StateSnapshot,
} from '@/net/contracts';

export type {
  ArtifactIndex,
  ArtifactIndexEntry,
  ArtifactManifest,
  BatchArtifact,
  BatchArtifactIndex,
  BatchDetail,
  BatchList,
  BatchListItem,
  BatchModelCard,
  JsonArtifact,
  JsonlArtifact,
  ModelDetail,
  ReplayFlag,
  ReplayReport,
  ReplayStep,
  ReviewLabel,
  ReviewQueueItem,
  ReviewSummary,
  RunDetail,
  RunArtifact,
  RunList,
  RunListItem,
  ScorecardArtifact,
  SnapshotIndex,
  SnapshotIndexEntry,
  TraceFinding,
  UsageReport,
} from '@/net/contracts';

const apiGet = async <T>(path: string): Promise<T> => {
  const res = await fetch(`${getApiBaseUrl()}${path}`);
  if (!res.ok) {
    throw new Error(`Request failed (${res.status})`);
  }
  return (await res.json()) as T;
};

const apiPost = async <T>(path: string, body: unknown): Promise<T> => {
  const res = await fetch(`${getApiBaseUrl()}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`Request failed (${res.status})`);
  }
  return (await res.json()) as T;
};

export const fetchRuns = (): Promise<RunList> => apiGet('/runs');

export const fetchRun = (runId: string): Promise<RunDetail> =>
  apiGet(`/runs/${encodeURIComponent(runId)}`);

export const fetchModel = (modelId: string): Promise<ModelDetail> =>
  apiGet(`/models/${encodeURIComponent(modelId)}`);

export const fetchRunArtifacts = (runId: string): Promise<ArtifactIndex> =>
  apiGet(`/runs/${encodeURIComponent(runId)}/artifacts`);

export const fetchRunArtifact = <T = unknown>(runId: string, artifactName: string): Promise<RunArtifact<T>> =>
  apiGet(`/runs/${encodeURIComponent(runId)}/artifacts/${encodeURIComponent(artifactName)}`);

export const fetchRunSnapshots = (runId: string): Promise<SnapshotIndex> =>
  apiGet(`/runs/${encodeURIComponent(runId)}/snapshots`);

export const fetchRunSnapshot = (runId: string, snapshotName: string): Promise<StateSnapshot> =>
  apiGet<{ content: StateSnapshot }>(
    `/runs/${encodeURIComponent(runId)}/snapshots/${encodeURIComponent(snapshotName)}`
  ).then((payload) => payload.content);

export const fetchReviewQueue = (runId: string): Promise<ReviewQueueItem[]> =>
  apiGet<{ queue: ReviewQueueItem[] }>(`/runs/${encodeURIComponent(runId)}/review/queue`).then(
    (payload) => payload.queue ?? []
  );

export const addReviewQueueItem = (
  runId: string,
  body: {
    decision_id?: string | null;
    turn_index?: number | null;
    player_id?: string | null;
    model_id?: string | null;
    severity?: string | null;
    reason_for_review?: string | null;
    suggested_labels?: string[];
    reviewer_id?: string | null;
  }
): Promise<{ queue_item: ReviewQueueItem }> =>
  apiPost(`/runs/${encodeURIComponent(runId)}/review/queue`, body);

export const fetchReviewLabels = (runId: string): Promise<ReviewLabel[]> =>
  apiGet<{ labels: ReviewLabel[] }>(`/runs/${encodeURIComponent(runId)}/review/labels`).then(
    (payload) => payload.labels ?? []
  );

export const fetchReviewSummary = (runId: string): Promise<ReviewSummary> =>
  apiGet(`/runs/${encodeURIComponent(runId)}/review/summary`);

export const saveReviewLabel = (
  runId: string,
  body: {
    queue_item_id?: string | null;
    reviewer_id?: string | null;
    selected_labels: string[];
    confidence?: number | null;
    notes?: string | null;
    adjudication_status?: string | null;
    gold_label?: boolean;
    evidence_references?: unknown[];
  }
): Promise<{ label: ReviewLabel; summary: ReviewSummary }> =>
  apiPost(`/runs/${encodeURIComponent(runId)}/review/labels`, body);

export const fetchBatches = (): Promise<BatchList> => apiGet('/batches');

export const fetchBatch = (batchId: string): Promise<BatchDetail> =>
  apiGet(`/batches/${encodeURIComponent(batchId)}`);

export const fetchBatchArtifacts = (batchId: string): Promise<BatchArtifactIndex> =>
  apiGet(`/batches/${encodeURIComponent(batchId)}/artifacts`);

export const fetchBatchArtifact = <T = unknown>(
  batchId: string,
  artifactName: string
): Promise<BatchArtifact<T>> =>
  apiGet(`/batches/${encodeURIComponent(batchId)}/artifacts/${encodeURIComponent(artifactName)}`);

export const fetchBatchModelCard = (batchId: string, cardId: string): Promise<BatchModelCard> =>
  apiGet(`/batches/${encodeURIComponent(batchId)}/model_cards/${encodeURIComponent(cardId)}`);

export type ResearchArtifactEntry = {
  name: string;
  path: string;
  exists: boolean;
  kind: 'json' | 'jsonl' | 'csv' | 'markdown' | 'text' | string;
};

export type CampaignListItem = {
  campaign_id: string;
  campaign_dir: string;
  run_count?: number | null;
  completed_run_count?: number | null;
  execution_status?: string | null;
  manifest_exists?: boolean;
};

export type CampaignDetail = {
  campaign_id: string;
  campaign_dir: string;
  manifest: Record<string, unknown>;
  config: Record<string, unknown>;
  leaderboard: Record<string, unknown>;
  statistics: Record<string, unknown>;
  baseline_comparison: Record<string, unknown>;
};

export type MicroResearchReportListItem = {
  report_id: string;
  report_dir: string;
  suite_id?: string | null;
  suite_family?: string | null;
  scenario_count?: number | null;
  joined_result_count?: number | null;
  human_label_count?: number | null;
};

export type MicroResearchReportDetail = {
  report_id: string;
  report_dir: string;
  micro_report: Record<string, unknown>;
  category_breakdown: Record<string, unknown>;
  counterfactual_report: Record<string, unknown>;
  safety_report: Record<string, unknown>;
  campaign_report: Record<string, unknown>;
  result_join: Record<string, unknown>;
  label_summary: Record<string, unknown>;
};

export type ResearchArtifact<T = unknown> = {
  artifact: string;
  kind: string;
  content?: T;
  rows?: T[];
  text?: string;
};

export const fetchCampaigns = (): Promise<{ campaigns: CampaignListItem[] }> => apiGet('/campaigns');

export const fetchCampaign = (campaignId: string): Promise<CampaignDetail> =>
  apiGet(`/campaigns/${encodeURIComponent(campaignId)}`);

export const fetchCampaignArtifacts = (campaignId: string): Promise<{ campaign_id: string; artifacts: ResearchArtifactEntry[] }> =>
  apiGet(`/campaigns/${encodeURIComponent(campaignId)}/artifacts`);

export const fetchCampaignArtifact = <T = unknown>(campaignId: string, artifactName: string): Promise<ResearchArtifact<T>> =>
  apiGet(`/campaigns/${encodeURIComponent(campaignId)}/artifacts/${encodeURIComponent(artifactName)}`);

export const fetchMicroResearchReports = (): Promise<{ reports: MicroResearchReportListItem[] }> =>
  apiGet('/micro/research-reports');

export const fetchMicroResearchReport = (reportId: string): Promise<MicroResearchReportDetail> =>
  apiGet(`/micro/research-reports/${encodeURIComponent(reportId)}`);

export const fetchMicroResearchArtifacts = (
  reportId: string
): Promise<{ report_id: string; artifacts: ResearchArtifactEntry[] }> =>
  apiGet(`/micro/research-reports/${encodeURIComponent(reportId)}/artifacts`);

export const fetchMicroResearchArtifact = <T = unknown>(reportId: string, artifactName: string): Promise<ResearchArtifact<T>> =>
  apiGet(`/micro/research-reports/${encodeURIComponent(reportId)}/artifacts/${encodeURIComponent(artifactName)}`);
