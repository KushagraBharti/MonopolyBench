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
