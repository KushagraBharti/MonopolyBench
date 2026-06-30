import { useEffect, useMemo, useState } from 'react';
import { NeoBadge } from '@/components/ui/NeoPrimitive';
import { cn } from '@/components/ui/cn';
import {
  fetchBatch,
  fetchBatchArtifact,
  fetchBatchArtifacts,
  fetchBatchModelCard,
  fetchBatches,
  type BatchArtifactIndex,
  type BatchDetail,
  type BatchListItem,
  type BatchModelCard,
} from '@/net/artifacts';

const parseBatchId = (): string | null => {
  const parts = window.location.pathname.split('/').filter(Boolean);
  return parts[0] === 'batches' ? parts[1] ?? null : null;
};

const formatJson = (value: unknown): string => {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
};

const getArray = (value: unknown): Record<string, unknown>[] => {
  return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === 'object') : [];
};

const getRecord = (value: unknown): Record<string, unknown> => {
  return value && typeof value === 'object' && !Array.isArray(value) ? (value as Record<string, unknown>) : {};
};

const numberText = (value: unknown): string => {
  if (typeof value !== 'number') return '-';
  return Number.isInteger(value) ? value.toLocaleString('en-US') : value.toFixed(4);
};

export const BatchDashboardPage = () => {
  const batchId = useMemo(() => parseBatchId(), []);
  const [batches, setBatches] = useState<BatchListItem[]>([]);
  const [detail, setDetail] = useState<BatchDetail | null>(null);
  const [artifacts, setArtifacts] = useState<BatchArtifactIndex | null>(null);
  const [costReport, setCostReport] = useState<Record<string, unknown> | null>(null);
  const [tokenReport, setTokenReport] = useState<Record<string, unknown> | null>(null);
  const [replayReport, setReplayReport] = useState<Record<string, unknown> | null>(null);
  const [failureSummary, setFailureSummary] = useState<Record<string, unknown> | null>(null);
  const [traceSummary, setTraceSummary] = useState<Record<string, unknown> | null>(null);
  const [selectedCardId, setSelectedCardId] = useState<string | null>(null);
  const [modelCardState, setModelCardState] = useState<{ cardId: string; card: BatchModelCard | null } | null>(null);
  const [status, setStatus] = useState('Loading batches...');
  const modelCard = selectedCardId && modelCardState?.cardId === selectedCardId ? modelCardState.card : null;

  useEffect(() => {
    if (batchId) return;
    let active = true;
    fetchBatches()
      .then((payload) => {
        if (!active) return;
        setBatches(payload.batches ?? []);
        setStatus(payload.batches?.length ? 'Batches loaded.' : 'No batches found.');
      })
      .catch((err) => {
        if (!active) return;
        setStatus(err instanceof Error ? err.message : 'Failed to load batches.');
      });
    return () => {
      active = false;
    };
  }, [batchId]);

  useEffect(() => {
    if (!batchId) return;
    let active = true;
    const load = async () => {
      setStatus('Loading batch artifacts...');
      const [batchDetail, artifactIndex, cost, token, replay, failure, trace] = await Promise.all([
        fetchBatch(batchId),
        fetchBatchArtifacts(batchId),
        fetchBatchArtifact<Record<string, unknown>>(batchId, 'cost_report').catch(() => null),
        fetchBatchArtifact<Record<string, unknown>>(batchId, 'token_report').catch(() => null),
        fetchBatchArtifact<Record<string, unknown>>(batchId, 'replay_report').catch(() => null),
        fetchBatchArtifact<Record<string, unknown>>(batchId, 'failure_summary').catch(() => null),
        fetchBatchArtifact<Record<string, unknown>>(batchId, 'trace_summary').catch(() => null),
      ]);
      if (!active) return;
      setDetail(batchDetail);
      setArtifacts(artifactIndex);
      setCostReport(cost?.kind === 'json' ? cost.content : null);
      setTokenReport(token?.kind === 'json' ? token.content : null);
      setReplayReport(replay?.kind === 'json' ? replay.content : null);
      setFailureSummary(failure?.kind === 'json' ? failure.content : null);
      setTraceSummary(trace?.kind === 'json' ? trace.content : null);
      setSelectedCardId(artifactIndex.model_cards[0]?.card_id ?? null);
      setStatus('Batch loaded.');
    };
    void load().catch((err) => {
      if (active) setStatus(err instanceof Error ? err.message : 'Failed to load batch.');
    });
    return () => {
      active = false;
    };
  }, [batchId]);

  useEffect(() => {
    if (!batchId || !selectedCardId) return;
    let active = true;
    const cardId = selectedCardId;
    fetchBatchModelCard(batchId, selectedCardId)
      .then((card) => {
        if (active) setModelCardState({ cardId, card });
      })
      .catch(() => {
        if (active) setModelCardState({ cardId, card: null });
      });
    return () => {
      active = false;
    };
  }, [batchId, selectedCardId]);

  if (!batchId) {
    return (
      <div className="min-h-screen bg-neo-bg text-black p-6 overflow-y-auto brutal-scroll">
        <header className="mx-auto flex max-w-screen-2xl flex-wrap items-center justify-between gap-4 border-b-2 border-black pb-4">
          <div>
            <a href="/" className="inline-flex min-h-8 items-center text-xl font-black uppercase tracking-normal">
              Monopoly<span className="text-neo-pink">Bench</span>
            </a>
            <div className="text-[11px] font-mono text-gray-500 mt-1">Batch artifacts and model cards</div>
          </div>
          <NeoBadge variant="info">{status}</NeoBadge>
        </header>
        <main className="mx-auto mt-5 grid max-w-screen-2xl grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {batches.map((batch) => (
            <a
              key={batch.batch_id}
              href={`/batches/${encodeURIComponent(batch.batch_id)}`}
              className="border-2 border-black bg-white rounded-[3px] shadow-neo p-4 hover:-translate-y-px hover:shadow-neo-lg transition-all"
            >
              <div className="flex items-center justify-between gap-3">
                <div className="text-sm font-black uppercase">{batch.batch_id}</div>
                <NeoBadge variant={batch.manifest_exists ? 'success' : 'warning'}>
                  {batch.manifest_exists ? 'manifest' : 'partial'}
                </NeoBadge>
              </div>
              <div className="mt-3 text-[11px] font-mono text-gray-500 break-all">{batch.batch_dir}</div>
              <div className="mt-3 text-2xl font-mono font-black">{batch.run_count ?? '-'}</div>
              <div className="text-[9px] font-black uppercase text-gray-500">runs</div>
            </a>
          ))}
          {batches.length === 0 ? (
            <div className="rounded-[6px] border-2 border-dashed border-black/20 bg-white/70 p-5 text-sm text-gray-500">
              No batch artifact directories found.
            </div>
          ) : null}
        </main>
      </div>
    );
  }

  const leaderboardRows = getArray(getRecord(detail?.leaderboard).rankings);
  const replayStatusCounts = getRecord(replayReport?.status_counts);
  const stateReplayStatusCounts = getRecord(replayReport?.state_status_counts);
  const artifactReplayStatusCounts = getRecord(replayReport?.artifact_status_counts);
  const costTotals = getRecord(costReport);
  const tokenTotals = getRecord(tokenReport?.totals);
  const failureCounts = getRecord(failureSummary?.by_finding_type);
  const traceCounts = getRecord(traceSummary?.by_finding_type);

  return (
    <div className="flex min-h-screen w-full flex-col overflow-y-auto bg-neo-bg text-black lg:h-screen lg:flex-row lg:overflow-hidden">
      <aside className="flex w-full flex-col border-b-2 border-black bg-white lg:h-full lg:w-80 lg:border-b-0 lg:border-r-2">
        <header className="p-3 border-b-2 border-black bg-neo-bg/70">
          <a href="/batches" className="inline-flex min-h-8 items-center text-base font-black uppercase tracking-normal">
            Batches
          </a>
          <div className="mt-2 text-[11px] font-mono break-all text-gray-500">{batchId}</div>
          <div className="mt-3 grid grid-cols-2 gap-2">
            <Metric label="Runs" value={String(getRecord(detail?.manifest).run_count ?? '-')} />
            <Metric label="Replay Pass" value={numberText(replayReport?.pass_rate)} />
            <Metric label="State Pass" value={numberText(replayReport?.state_pass_rate)} />
            <Metric label="Artifact Pass" value={numberText(replayReport?.artifact_pass_rate)} />
          </div>
        </header>
        <section className="p-3 border-b border-black/10">
          <div className="text-[10px] font-black uppercase mb-2">Model Cards</div>
          <div className="space-y-1.5">
            {(artifacts?.model_cards ?? []).map((card) => (
              <button
                key={card.card_id}
                type="button"
                onClick={() => setSelectedCardId(card.card_id)}
                className={cn(
                  'w-full text-left border rounded-[2px] px-2 py-1.5 text-[10px] font-mono',
                  selectedCardId === card.card_id ? 'border-black bg-neo-yellow/20' : 'border-black/15 bg-white'
                )}
              >
                {card.card_id}
              </button>
            ))}
          </div>
        </section>
        <section className="flex-1 min-h-0 overflow-y-auto p-3 brutal-scroll">
          <div className="text-[10px] font-black uppercase mb-2">Artifacts</div>
          <div className="space-y-1.5">
            {(artifacts?.artifacts ?? []).map((artifact) => (
              <div key={artifact.name} className="flex items-center justify-between gap-2 border border-black/10 rounded-[2px] px-2 py-1 bg-white">
                <span className="text-[10px] font-mono truncate">{artifact.name}</span>
                <NeoBadge variant={artifact.exists ? 'success' : 'neutral'}>{artifact.kind}</NeoBadge>
              </div>
            ))}
          </div>
        </section>
      </aside>

      <main className="min-w-0 flex-1 overflow-y-auto brutal-scroll p-4 lg:p-5">
        <header className="flex flex-wrap items-center justify-between gap-3 border-b-2 border-black pb-4">
          <div>
            <h1 className="text-2xl font-black uppercase tracking-normal">Batch Dashboard</h1>
            <div className="text-[11px] font-mono text-gray-500 mt-1">{status}</div>
          </div>
          <div className="flex gap-2">
            <NeoBadge variant="info">render-only</NeoBadge>
            <NeoBadge variant="neutral">prompt unchanged</NeoBadge>
          </div>
        </header>

        <section className="mt-5 grid grid-cols-1 md:grid-cols-4 gap-3">
          <Metric label="Actual Cost" value={numberText(costTotals.total_actual_cost)} />
          <Metric label="Prompt Tokens" value={numberText(tokenTotals.prompt_tokens)} />
          <Metric label="Completion Tokens" value={numberText(tokenTotals.completion_tokens)} />
          <Metric
            label="Replay Passed"
            value={`${String(replayStatusCounts.passed ?? 0)} / ${String(stateReplayStatusCounts.passed ?? 0)} / ${String(
              artifactReplayStatusCounts.passed ?? 0
            )}`}
          />
        </section>

        <section className="mt-5 grid grid-cols-1 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)] gap-4">
          <div className="border-2 border-black rounded-[3px] bg-white shadow-neo overflow-hidden">
            <div className="px-3 py-2 border-b-2 border-black bg-neo-bg/70 text-[10px] font-black uppercase">Leaderboard</div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-[11px]">
                <thead className="bg-black text-white uppercase text-[9px]">
                  <tr>
                    <th className="px-3 py-2">Model</th>
                    <th className="px-3 py-2">Games</th>
                    <th className="px-3 py-2">Win Rate</th>
                    <th className="px-3 py-2">Avg Net</th>
                    <th className="px-3 py-2">Cost</th>
                  </tr>
                </thead>
                <tbody>
                  {leaderboardRows.map((row, index) => (
                    <tr key={`${row.model_id ?? index}`} className="border-b border-black/10">
                      <td className="px-3 py-2 font-mono">{String(row.model_id ?? 'unknown')}</td>
                      <td className="px-3 py-2 font-mono">{numberText(row.game_count)}</td>
                      <td className="px-3 py-2 font-mono">{numberText(row.win_rate)}</td>
                      <td className="px-3 py-2 font-mono">{numberText(row.average_final_net_worth)}</td>
                      <td className="px-3 py-2 font-mono">{numberText(row.total_cost)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="border-2 border-black rounded-[3px] bg-white shadow-neo overflow-hidden">
            <div className="px-3 py-2 border-b-2 border-black bg-neo-bg/70 text-[10px] font-black uppercase">Trace / Failure</div>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-1 gap-3 p-3">
              <SummaryBlock title="Failures" values={failureCounts} />
              <SummaryBlock title="Trace" values={traceCounts} />
            </div>
          </div>
        </section>

        <section className="mt-5 grid grid-cols-1 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)] gap-4">
          <div className="border-2 border-black rounded-[3px] bg-white shadow-neo overflow-hidden">
            <div className="px-3 py-2 border-b-2 border-black bg-neo-bg/70 text-[10px] font-black uppercase">Model Card JSON</div>
            <pre className="p-3 text-[11px] font-mono whitespace-pre-wrap max-h-[460px] overflow-auto brutal-scroll">
              {modelCard ? formatJson(modelCard.json) : 'Select a model card.'}
            </pre>
          </div>
          <div className="border-2 border-black rounded-[3px] bg-white shadow-neo overflow-hidden">
            <div className="px-3 py-2 border-b-2 border-black bg-neo-bg/70 text-[10px] font-black uppercase">Model Card Markdown</div>
            <pre className="p-3 text-[11px] font-mono whitespace-pre-wrap max-h-[460px] overflow-auto brutal-scroll">
              {modelCard?.markdown ?? 'Select a model card.'}
            </pre>
          </div>
        </section>
      </main>
    </div>
  );
};

const Metric = ({ label, value }: { label: string; value: string }) => (
  <div className="border border-black/15 bg-white rounded-[2px] px-3 py-2">
    <div className="text-[9px] uppercase font-black text-gray-500">{label}</div>
    <div className="text-lg font-mono font-black">{value}</div>
  </div>
);

const SummaryBlock = ({ title, values }: { title: string; values: Record<string, unknown> }) => {
  const rows = Object.entries(values);
  return (
    <div>
      <div className="text-[10px] font-black uppercase mb-2">{title}</div>
      <div className="space-y-1.5">
        {rows.map(([key, value]) => (
          <div key={key} className="flex items-center justify-between gap-2 border border-black/10 rounded-[2px] px-2 py-1">
            <span className="text-[10px] font-mono truncate">{key}</span>
            <span className="text-[10px] font-mono font-black">{numberText(value)}</span>
          </div>
        ))}
        {rows.length === 0 ? <div className="text-sm text-gray-500">No rows.</div> : null}
      </div>
    </div>
  );
};
