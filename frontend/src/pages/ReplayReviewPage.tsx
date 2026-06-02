import { useEffect, useMemo, useState } from 'react';
import { Board } from '@/components/board/Board';
import { NeoBadge } from '@/components/ui/NeoPrimitive';
import { cn } from '@/components/ui/cn';
import { getPlayerColor } from '@/domain/monopoly/colors';
import { fetchDecisionBundle, type DecisionBundle } from '@/net/decisions';
import {
  addReviewQueueItem,
  fetchReviewLabels,
  fetchReviewQueue,
  fetchReviewSummary,
  fetchRunArtifact,
  fetchRunSnapshot,
  fetchRunSnapshots,
  saveReviewLabel,
  type ReplayFlag,
  type ReplayStep,
  type ReviewLabel,
  type ReviewQueueItem,
  type ReviewSummary,
  type SnapshotIndexEntry,
  type TraceFinding,
} from '@/net/artifacts';
import type { StateSnapshot } from '@/net/contracts';

type SkipMode = 'all' | 'important' | 'trace' | 'failures' | 'negotiations' | 'auctions' | 'bankruptcies' | 'model';
type InspectorTab = 'timeline' | 'findings' | 'review' | 'decision' | 'diff';

const skipModes: { id: SkipMode; label: string }[] = [
  { id: 'all', label: 'All' },
  { id: 'important', label: 'Important' },
  { id: 'trace', label: 'Trace' },
  { id: 'failures', label: 'Failures' },
  { id: 'negotiations', label: 'Trades' },
  { id: 'auctions', label: 'Auctions' },
  { id: 'bankruptcies', label: 'Bankruptcy' },
  { id: 'model', label: 'Model' },
];

const parseRunId = (): string => {
  const parts = window.location.pathname.split('/').filter(Boolean);
  return parts[1] ?? '';
};

const formatJson = (value: unknown): string => {
  if (value === null || value === undefined) return 'null';
  if (typeof value === 'string') return value;
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
};

const asRows = <T,>(artifact: { kind: string; rows?: T[] } | null): T[] =>
  artifact?.kind === 'jsonl' && Array.isArray(artifact.rows) ? artifact.rows : [];

const asContent = <T,>(artifact: { kind: string; content?: T } | null): T | null =>
  artifact?.kind === 'json' && artifact.content !== undefined ? artifact.content : null;

const safeLoadArtifact = async <T,>(runId: string, name: string) => {
  try {
    return await fetchRunArtifact<T>(runId, name);
  } catch {
    return null;
  }
};

const turnFromSnapshotName = (name: string): number => {
  const match = /^turn_(\d{4})/.exec(name);
  return match ? Number(match[1]) : 0;
};

const snapshotForTurn = (snapshots: SnapshotIndexEntry[], turnIndex: number | null | undefined): string | null => {
  if (!snapshots.length) return null;
  if (turnIndex === null || turnIndex === undefined) return snapshots[snapshots.length - 1]?.name ?? null;
  const exact = snapshots.find((snapshot) => turnFromSnapshotName(snapshot.name) === turnIndex);
  if (exact) return exact.name;
  const earlier = [...snapshots].reverse().find((snapshot) => turnFromSnapshotName(snapshot.name) <= turnIndex);
  return earlier?.name ?? snapshots[0]?.name ?? null;
};

const decisionIdFromStep = (step: ReplayStep | null): string | null => {
  const value = step?.payload?.decision_id;
  return typeof value === 'string' ? value : null;
};

const eventPlayerId = (step: ReplayStep | null): string | null => {
  const payloadPlayer = step?.payload?.player_id;
  if (typeof payloadPlayer === 'string') return payloadPlayer;
  const actorPlayer = step?.actor?.player_id;
  return typeof actorPlayer === 'string' ? actorPlayer : null;
};

const severityVariant = (severity?: string): 'neutral' | 'success' | 'warning' | 'error' | 'info' => {
  if (severity === 'error' || severity === 'critical' || severity === 'high') return 'error';
  if (severity === 'warning' || severity === 'medium') return 'warning';
  if (severity === 'info' || severity === 'low') return 'info';
  return 'neutral';
};

const isBankruptcyLike = (step: ReplayStep): boolean => {
  const reason = step.payload?.reason;
  return step.event_type === 'GAME_ENDED' || (typeof reason === 'string' && reason.includes('BANKRUPTCY'));
};

const filterSteps = (
  steps: ReplayStep[],
  mode: SkipMode,
  flags: ReplayFlag[],
  traceFindings: TraceFinding[],
  failureFindings: TraceFinding[]
): ReplayStep[] => {
  const important = new Set(flags.map((flag) => flag.step_index).filter((value): value is number => typeof value === 'number'));
  const traceSeqs = new Set(traceFindings.flatMap(findingSeqs));
  const failureSeqs = new Set(failureFindings.flatMap(findingSeqs));
  switch (mode) {
    case 'important':
      return steps.filter((step) => important.has(step.step_index));
    case 'trace':
      return steps.filter((step) => typeof step.event_seq === 'number' && traceSeqs.has(step.event_seq));
    case 'failures':
      return steps.filter((step) => typeof step.event_seq === 'number' && failureSeqs.has(step.event_seq));
    case 'negotiations':
      return steps.filter((step) => step.event_type.startsWith('TRADE_'));
    case 'auctions':
      return steps.filter((step) => step.event_type.startsWith('AUCTION_'));
    case 'bankruptcies':
      return steps.filter(isBankruptcyLike);
    case 'model':
      return steps.filter((step) => step.event_type.startsWith('LLM_'));
    default:
      return steps;
  }
};

const findingSeqs = (finding: TraceFinding): number[] => {
  const direct = (finding as TraceFinding & { event_seq_start?: number | null; event_seq_end?: number | null }).event_seq;
  const start = (finding as TraceFinding & { event_seq_start?: number | null; event_seq_end?: number | null }).event_seq_start;
  const end = (finding as TraceFinding & { event_seq_start?: number | null; event_seq_end?: number | null }).event_seq_end ?? start;
  if (typeof direct === 'number') return [direct];
  if (typeof start !== 'number' || typeof end !== 'number') return [];
  const seqs: number[] = [];
  for (let seq = start; seq <= end; seq += 1) seqs.push(seq);
  return seqs;
};

const playerName = (snapshot: StateSnapshot | null, playerId: string | null): string => {
  if (!playerId) return 'system';
  const player = snapshot?.players.find((entry) => entry.player_id === playerId);
  return player?.name ?? playerId;
};

const compactMoney = (value: unknown): string => {
  if (typeof value !== 'number') return '-';
  return `$${value.toLocaleString('en-US')}`;
};

export const ReplayReviewPage = () => {
  const runId = useMemo(() => parseRunId(), []);
  const [steps, setSteps] = useState<ReplayStep[]>([]);
  const [flags, setFlags] = useState<ReplayFlag[]>([]);
  const [traceFindings, setTraceFindings] = useState<TraceFinding[]>([]);
  const [failureFindings, setFailureFindings] = useState<TraceFinding[]>([]);
  const [reviewQueue, setReviewQueue] = useState<ReviewQueueItem[]>([]);
  const [reviewLabels, setReviewLabels] = useState<ReviewLabel[]>([]);
  const [reviewSummary, setReviewSummary] = useState<ReviewSummary | null>(null);
  const [replayReport, setReplayReport] = useState<Record<string, unknown> | null>(null);
  const [replayDiff, setReplayDiff] = useState<Record<string, unknown> | null>(null);
  const [eventHashes, setEventHashes] = useState<Record<string, unknown> | null>(null);
  const [snapshots, setSnapshots] = useState<SnapshotIndexEntry[]>([]);
  const [snapshotState, setSnapshotState] = useState<{ name: string; snapshot: StateSnapshot | null } | null>(null);
  const [selectedStepIndex, setSelectedStepIndex] = useState(0);
  const [selectedSnapshotName, setSelectedSnapshotName] = useState<string | null>(null);
  const [skipMode, setSkipMode] = useState<SkipMode>('all');
  const [tab, setTab] = useState<InspectorTab>('timeline');
  const [decisionBundleState, setDecisionBundleState] = useState<{ decisionId: string; bundle: DecisionBundle | null } | null>(null);
  const [selectedReviewItem, setSelectedReviewItem] = useState<ReviewQueueItem | null>(null);
  const [reviewerId, setReviewerId] = useState(() => window.localStorage.getItem('monopolybench.reviewer_id') ?? 'local_reviewer');
  const [reviewLabelsText, setReviewLabelsText] = useState('');
  const [reviewNotes, setReviewNotes] = useState('');
  const [status, setStatus] = useState('Loading replay artifacts...');

  const selectedStep = steps.find((step) => step.step_index === selectedStepIndex) ?? steps[0] ?? null;
  const selectedDecisionId = selectedReviewItem?.decision_id ?? decisionIdFromStep(selectedStep);
  const snapshot = selectedSnapshotName && snapshotState?.name === selectedSnapshotName ? snapshotState.snapshot : null;
  const decisionBundle =
    selectedDecisionId && decisionBundleState?.decisionId === selectedDecisionId ? decisionBundleState.bundle : null;
  const filteredSteps = useMemo(
    () => filterSteps(steps, skipMode, flags, traceFindings, failureFindings),
    [steps, skipMode, flags, traceFindings, failureFindings]
  );
  const selectedPlayerId = eventPlayerId(selectedStep);

  useEffect(() => {
    let active = true;
    const load = async () => {
      setStatus('Loading replay artifacts...');
      const [
        replayReportArtifact,
        replayDiffArtifact,
        eventHashesArtifact,
        replayStepsArtifact,
        replayFlagsArtifact,
        traceArtifact,
        failureArtifact,
        snapshotIndex,
        queue,
        labels,
        summary,
      ] = await Promise.all([
        safeLoadArtifact<Record<string, unknown>>(runId, 'replay_report'),
        safeLoadArtifact<Record<string, unknown>>(runId, 'replay_diff'),
        safeLoadArtifact<Record<string, unknown>>(runId, 'event_hashes'),
        safeLoadArtifact<ReplayStep>(runId, 'replay_steps'),
        safeLoadArtifact<ReplayFlag>(runId, 'replay_flags'),
        safeLoadArtifact<TraceFinding>(runId, 'trace_findings'),
        safeLoadArtifact<TraceFinding>(runId, 'failure_findings'),
        fetchRunSnapshots(runId).catch(() => ({ run_id: runId, snapshots: [] })),
        fetchReviewQueue(runId).catch(() => []),
        fetchReviewLabels(runId).catch(() => []),
        fetchReviewSummary(runId).catch(() => null),
      ]);
      if (!active) return;
      const loadedSteps = asRows<ReplayStep>(replayStepsArtifact);
      setReplayReport(asContent<Record<string, unknown>>(replayReportArtifact));
      setReplayDiff(asContent<Record<string, unknown>>(replayDiffArtifact));
      setEventHashes(asContent<Record<string, unknown>>(eventHashesArtifact));
      setSteps(loadedSteps);
      setFlags(asRows<ReplayFlag>(replayFlagsArtifact));
      setTraceFindings(asRows<TraceFinding>(traceArtifact));
      setFailureFindings(asRows<TraceFinding>(failureArtifact));
      setSnapshots(snapshotIndex.snapshots ?? []);
      setReviewQueue(queue);
      setReviewLabels(labels);
      setReviewSummary(summary);
      setSelectedStepIndex(loadedSteps[0]?.step_index ?? 0);
      setSelectedSnapshotName(snapshotForTurn(snapshotIndex.snapshots ?? [], loadedSteps[0]?.turn_index));
      setStatus(loadedSteps.length ? 'Replay loaded.' : 'No replay steps found for this run.');
    };
    void load();
    return () => {
      active = false;
    };
  }, [runId]);

  useEffect(() => {
    if (!selectedSnapshotName) return;
    let active = true;
    const snapshotName = selectedSnapshotName;
    fetchRunSnapshot(runId, snapshotName)
      .then((loaded) => {
        if (active) setSnapshotState({ name: snapshotName, snapshot: loaded });
      })
      .catch(() => {
        if (active) setSnapshotState({ name: snapshotName, snapshot: null });
      });
    return () => {
      active = false;
    };
  }, [runId, selectedSnapshotName]);

  useEffect(() => {
    if (!selectedDecisionId) return;
    let active = true;
    const decisionId = selectedDecisionId;
    fetchDecisionBundle(runId, decisionId)
      .then((bundle) => {
        if (active) setDecisionBundleState({ decisionId, bundle });
      })
      .catch(() => {
        if (active) setDecisionBundleState({ decisionId, bundle: null });
      });
    return () => {
      active = false;
    };
  }, [runId, selectedDecisionId]);

  const selectStep = (stepIndex: number) => {
    const nextStep = steps.find((step) => step.step_index === stepIndex) ?? null;
    setSelectedStepIndex(stepIndex);
    setSelectedSnapshotName(snapshotForTurn(snapshots, nextStep?.turn_index));
    setSelectedReviewItem(null);
  };

  const moveWithinMode = (direction: -1 | 1) => {
    if (!filteredSteps.length) return;
    const current = filteredSteps.findIndex((step) => step.step_index === selectedStepIndex);
    const currentIndex = current >= 0 ? current : 0;
    const next = filteredSteps[Math.max(0, Math.min(filteredSteps.length - 1, currentIndex + direction))];
    if (next) selectStep(next.step_index);
  };

  const jumpToFinding = (finding: TraceFinding) => {
    const step = steps.find((item) => item.event_seq === finding.event_seq);
    if (step) selectStep(step.step_index);
    if (finding.decision_id) {
      setSelectedReviewItem({
        queue_item_id: `finding-${finding.finding_id ?? finding.decision_id}`,
        run_id: runId,
        decision_id: finding.decision_id,
        turn_index: finding.turn_index,
        player_id: finding.player_id,
        model_id: finding.model_id,
        severity: finding.severity,
        reason_for_review: finding.finding_type,
        suggested_labels: finding.finding_type ? [finding.finding_type] : [],
        status: finding.human_review_status,
      });
    }
    setTab('findings');
  };

  const jumpToQueueItem = (item: ReviewQueueItem) => {
    setSelectedReviewItem(item);
    const step = steps.find((entry) => entry.turn_index === item.turn_index && (!item.decision_id || decisionIdFromStep(entry) === item.decision_id));
    if (step) selectStep(step.step_index);
    setReviewLabelsText((item.suggested_labels ?? []).join(', '));
    setTab('review');
  };

  const saveReview = async () => {
    const selectedLabels = reviewLabelsText
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean);
    const response = await saveReviewLabel(runId, {
      queue_item_id: selectedReviewItem?.queue_item_id ?? null,
      reviewer_id: reviewerId,
      selected_labels: selectedLabels,
      notes: reviewNotes,
      confidence: null,
      adjudication_status: 'unadjudicated',
      gold_label: false,
      evidence_references: selectedReviewItem ? [{ queue_item_id: selectedReviewItem.queue_item_id }] : [],
    });
    window.localStorage.setItem('monopolybench.reviewer_id', reviewerId);
    setReviewLabels((current) => [response.label, ...current]);
    setReviewSummary(response.summary);
    setReviewNotes('');
    setStatus('Review label saved.');
  };

  const queueSelectedDecision = async () => {
    if (!selectedDecisionId) {
      setStatus('No decision selected to queue.');
      return;
    }
    const response = await addReviewQueueItem(runId, {
      decision_id: selectedDecisionId,
      turn_index: selectedStep?.turn_index ?? null,
      player_id: selectedPlayerId,
      model_id: selectedReviewItem?.model_id ?? null,
      severity: 'medium',
      reason_for_review: 'user_selected_decision',
      suggested_labels: ['user_selected_decision'],
      reviewer_id: reviewerId,
    });
    setReviewQueue((current) => [response.queue_item, ...current]);
    setSelectedReviewItem(response.queue_item);
    setTab('review');
    setStatus('Selected decision queued for human review.');
  };

  const timelineRows = filteredSteps.length ? filteredSteps : steps;
  const activeFlagCount = flags.length;
  const replayStatus = String(replayReport?.status ?? 'unknown');

  return (
    <div className="flex min-h-screen w-full flex-col overflow-y-auto bg-neo-bg text-black lg:h-screen lg:flex-row lg:overflow-hidden">
      <aside className="flex w-full flex-col border-b-2 border-black bg-white lg:h-full lg:w-[22rem] lg:border-b-0 lg:border-r-2">
        <header className="p-3 border-b-2 border-black bg-neo-bg/70">
          <div className="flex items-center justify-between gap-2">
            <a href="/" className="inline-flex min-h-8 items-center text-base font-black uppercase tracking-normal">
              Monopoly<span className="text-neo-pink">Bench</span>
            </a>
            <NeoBadge variant={replayStatus === 'passed' ? 'success' : replayStatus === 'failed' ? 'error' : 'neutral'}>
              {replayStatus}
            </NeoBadge>
          </div>
          <div className="mt-2 text-[10px] font-mono text-gray-500 break-all">{runId}</div>
          <div className="mt-3 grid grid-cols-3 gap-2 text-center">
            <Metric label="Steps" value={steps.length} />
            <Metric label="Flags" value={activeFlagCount} />
            <Metric label="Labels" value={reviewSummary?.label_count ?? reviewLabels.length} />
          </div>
        </header>

        <section className="p-3 border-b border-black/10">
          <div className="text-[10px] font-black uppercase mb-2">Skip Mode</div>
          <div className="grid grid-cols-2 gap-1.5">
            {skipModes.map((mode) => (
              <button
                key={mode.id}
                type="button"
                onClick={() => setSkipMode(mode.id)}
                className={cn(
                  'min-h-8 px-2 py-1.5 border border-black/20 rounded-[2px] text-[9px] font-black uppercase',
                  skipMode === mode.id ? 'bg-black text-white' : 'bg-white hover:bg-neo-bg'
                )}
              >
                {mode.label}
              </button>
            ))}
          </div>
          <div className="mt-2 flex gap-2">
            <button type="button" onClick={() => moveWithinMode(-1)} className="brutal-btn text-[10px] px-3 py-1 flex-1">
              Prev
            </button>
            <button type="button" onClick={() => moveWithinMode(1)} className="brutal-btn text-[10px] px-3 py-1 flex-1">
              Next
            </button>
          </div>
        </section>

        <section className="p-3 border-b border-black/10">
          <div className="text-[10px] font-black uppercase mb-2">Snapshot</div>
          <select
            value={selectedSnapshotName ?? ''}
            onChange={(event) => setSelectedSnapshotName(event.target.value || null)}
            className="w-full border border-black/25 rounded-[2px] px-2 py-1.5 text-[11px] font-mono bg-white"
          >
            {snapshots.map((item) => (
              <option key={item.name} value={item.name}>
                {item.name}
              </option>
            ))}
          </select>
        </section>

        <section className="flex-1 min-h-0 overflow-y-auto brutal-scroll p-3">
          <div className="text-[10px] font-black uppercase mb-2">Players</div>
          <div className="space-y-2">
            {(snapshot?.players ?? []).map((player) => (
              <div key={player.player_id} className="border border-black/15 rounded-[2px] bg-white p-2">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="w-3 h-3 rounded-[2px] border border-black shrink-0" style={{ backgroundColor: getPlayerColor(player.player_id) }} />
                    <span className="text-[11px] font-black uppercase truncate">{player.name}</span>
                  </div>
                  {player.bankrupt ? <NeoBadge variant="error">Out</NeoBadge> : null}
                </div>
                <div className="mt-1 grid grid-cols-3 gap-1 text-[10px] font-mono">
                  <span>{compactMoney(player.cash)}</span>
                  <span>Pos {player.position}</span>
                  <span>{player.in_jail ? 'Jail' : 'Active'}</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      </aside>

      <main className="relative flex min-h-[32rem] min-w-0 flex-1 items-center justify-start overflow-x-auto bg-neo-bg p-3 brutal-scroll lg:h-full lg:justify-center lg:overflow-hidden lg:p-4">
        <Board
          spaces={snapshot?.board ?? []}
          players={snapshot?.players ?? []}
          activePlayerId={selectedPlayerId ?? snapshot?.active_player_id ?? null}
          highlightState={{ eventHighlight: selectedStep?.payload?.space_index && typeof selectedStep.payload.space_index === 'number' ? [selectedStep.payload.space_index] : null }}
          className="aspect-square w-full min-w-[34rem] max-w-[min(100%,calc(100vh-2rem))] lg:min-w-0"
          centerContent={
            <div className="z-10 rotate-[-6deg] text-center">
              <div className="text-4xl font-black uppercase leading-none tracking-normal">Replay</div>
              <div className="mt-2 text-[11px] font-mono uppercase tracking-wide">
                Step {selectedStep?.step_index ?? 0} / {steps.length}
              </div>
            </div>
          }
        />
      </main>

      <aside className="flex w-full flex-col border-t-2 border-black bg-white lg:h-full lg:w-[27rem] lg:border-l-2 lg:border-t-0">
        <header className="px-3 py-2 border-b-2 border-black bg-neo-bg/70">
          <div className="flex items-center gap-1.5">
            {(['timeline', 'findings', 'review', 'decision', 'diff'] as const).map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => setTab(item)}
                className={cn(
                  'min-h-8 px-2.5 py-1 border border-black/25 rounded-[2px] text-[9px] font-black uppercase',
                  tab === item ? 'bg-black text-white' : 'bg-white'
                )}
              >
                {item}
              </button>
            ))}
          </div>
          <div className="mt-2 text-[10px] font-mono text-gray-500">{status}</div>
          <div className="mt-2">
            <button
              type="button"
              onClick={queueSelectedDecision}
              className="brutal-btn text-[10px] px-3 py-1 w-full"
              disabled={!selectedDecisionId}
            >
              Queue Selected Decision
            </button>
          </div>
        </header>

        <div className="flex-1 min-h-0 overflow-y-auto brutal-scroll p-3">
          {tab === 'timeline' ? (
            <TimelinePanel rows={timelineRows} selectedStepIndex={selectedStepIndex} onSelect={selectStep} />
          ) : null}
          {tab === 'findings' ? (
            <FindingsPanel trace={traceFindings} failures={failureFindings} onJump={jumpToFinding} />
          ) : null}
          {tab === 'review' ? (
            <ReviewPanel
              queue={reviewQueue}
              labels={reviewLabels}
              summary={reviewSummary}
              selected={selectedReviewItem}
              reviewerId={reviewerId}
              labelsText={reviewLabelsText}
              notes={reviewNotes}
              onSelect={jumpToQueueItem}
              onReviewerId={setReviewerId}
              onLabelsText={setReviewLabelsText}
              onNotes={setReviewNotes}
              onSave={saveReview}
            />
          ) : null}
          {tab === 'decision' ? (
            <DecisionPanel step={selectedStep} bundle={decisionBundle} snapshot={snapshot} />
          ) : null}
          {tab === 'diff' ? (
            <DiffPanel replayReport={replayReport} replayDiff={replayDiff} eventHashes={eventHashes} />
          ) : null}
        </div>
      </aside>
    </div>
  );
};

const Metric = ({ label, value }: { label: string; value: number }) => (
  <div className="border border-black/15 bg-white rounded-[2px] px-2 py-1">
    <div className="text-[8px] uppercase font-bold text-gray-500">{label}</div>
    <div className="text-sm font-mono font-black">{value}</div>
  </div>
);

const TimelinePanel = ({
  rows,
  selectedStepIndex,
  onSelect,
}: {
  rows: ReplayStep[];
  selectedStepIndex: number;
  onSelect: (stepIndex: number) => void;
}) => (
  <div className="space-y-2">
    {rows.map((step) => (
      <button
        key={`${step.step_index}-${step.event_id ?? step.event_type}`}
        type="button"
        onClick={() => onSelect(step.step_index)}
        className={cn(
          'w-full text-left border rounded-[2px] p-2 bg-white',
          step.step_index === selectedStepIndex ? 'border-black bg-neo-yellow/20' : 'border-black/15 hover:border-black/40'
        )}
      >
        <div className="flex items-center justify-between gap-2">
          <span className="text-[10px] font-black uppercase">{step.event_type}</span>
          <span className="text-[9px] font-mono text-gray-500">#{step.step_index}</span>
        </div>
        <div className="mt-1 text-[10px] font-mono text-gray-500">turn {step.turn_index ?? '-'}</div>
      </button>
    ))}
  </div>
);

const FindingsPanel = ({
  trace,
  failures,
  onJump,
}: {
  trace: TraceFinding[];
  failures: TraceFinding[];
  onJump: (finding: TraceFinding) => void;
}) => {
  const rows = [...failures.map((finding) => ({ ...finding, kind: 'failure' })), ...trace.map((finding) => ({ ...finding, kind: 'trace' }))];
  return (
    <div className="space-y-2">
      {rows.length === 0 ? <div className="text-sm text-gray-500">No trace or failure findings.</div> : null}
      {rows.map((finding, index) => (
        <button
          key={`${finding.finding_id ?? index}`}
          type="button"
          onClick={() => onJump(finding)}
          className="w-full text-left border border-black/15 rounded-[2px] bg-white p-2 hover:border-black/40"
        >
          <div className="flex items-center justify-between gap-2">
            <span className="text-[10px] font-black uppercase">{finding.finding_type ?? 'finding'}</span>
            <NeoBadge variant={severityVariant(finding.severity)}>{finding.kind ?? 'trace'}</NeoBadge>
          </div>
          <div className="mt-1 text-[10px] font-mono text-gray-500">
            turn {finding.turn_index ?? '-'} / seq {finding.event_seq ?? '-'}
          </div>
        </button>
      ))}
    </div>
  );
};

const ReviewPanel = ({
  queue,
  labels,
  summary,
  selected,
  reviewerId,
  labelsText,
  notes,
  onSelect,
  onReviewerId,
  onLabelsText,
  onNotes,
  onSave,
}: {
  queue: ReviewQueueItem[];
  labels: ReviewLabel[];
  summary: ReviewSummary | null;
  selected: ReviewQueueItem | null;
  reviewerId: string;
  labelsText: string;
  notes: string;
  onSelect: (item: ReviewQueueItem) => void;
  onReviewerId: (value: string) => void;
  onLabelsText: (value: string) => void;
  onNotes: (value: string) => void;
  onSave: () => void;
}) => (
  <div className="space-y-3">
    <div className="grid grid-cols-3 gap-2">
      <Metric label="Queue" value={queue.length} />
      <Metric label="Labels" value={summary?.label_count ?? labels.length} />
      <Metric label="Gold" value={summary?.gold_label_count ?? 0} />
    </div>
    <div className="border border-black/15 rounded-[2px] bg-white p-2">
      <div className="text-[10px] font-black uppercase mb-2">Reviewer</div>
      <input
        value={reviewerId}
        onChange={(event) => onReviewerId(event.target.value)}
        className="w-full border border-black/25 rounded-[2px] px-2 py-1 text-[11px] font-mono"
      />
    </div>
    <div className="space-y-2">
      {queue.map((item) => (
        <button
          key={item.queue_item_id}
          type="button"
          onClick={() => onSelect(item)}
          className={cn(
            'w-full text-left border rounded-[2px] p-2 bg-white',
            selected?.queue_item_id === item.queue_item_id ? 'border-black bg-neo-yellow/20' : 'border-black/15'
          )}
        >
          <div className="text-[10px] font-black uppercase">{item.reason_for_review ?? item.queue_item_id}</div>
          <div className="text-[10px] font-mono text-gray-500">turn {item.turn_index ?? '-'} / {item.status ?? 'unreviewed'}</div>
        </button>
      ))}
      {queue.length === 0 ? <div className="text-sm text-gray-500">No queued review items.</div> : null}
    </div>
    <div className="border border-black/15 rounded-[2px] bg-white p-2 space-y-2">
      <div className="text-[10px] font-black uppercase">Label Selected Item</div>
      <input
        value={labelsText}
        onChange={(event) => onLabelsText(event.target.value)}
        placeholder="comma,separated,labels"
        className="w-full border border-black/25 rounded-[2px] px-2 py-1 text-[11px] font-mono"
      />
      <textarea
        value={notes}
        onChange={(event) => onNotes(event.target.value)}
        placeholder="review notes"
        className="w-full min-h-24 border border-black/25 rounded-[2px] px-2 py-1 text-[11px] font-mono"
      />
      <button type="button" onClick={onSave} className="brutal-btn brutal-btn-primary text-[10px] px-3 py-1">
        Save Label
      </button>
    </div>
  </div>
);

const DecisionPanel = ({
  step,
  bundle,
  snapshot,
}: {
  step: ReplayStep | null;
  bundle: DecisionBundle | null;
  snapshot: StateSnapshot | null;
}) => {
  const privateThought = step?.event_type === 'LLM_PRIVATE_THOUGHT' ? step.payload?.thought : null;
  const publicMessage = step?.event_type === 'LLM_PUBLIC_MESSAGE' ? step.payload?.message : null;
  return (
    <div className="space-y-3">
      <div className="border border-black/15 rounded-[2px] bg-white p-2">
        <div className="text-[10px] font-black uppercase mb-1">Selected Event</div>
        <div className="text-[11px] font-mono whitespace-pre-wrap">{formatJson(step)}</div>
      </div>
      <div className="border border-black/15 rounded-[2px] bg-white p-2">
        <div className="text-[10px] font-black uppercase mb-1">Public / Private Text</div>
        <div className="text-[11px] leading-snug">
          <div><span className="font-black uppercase">Player:</span> {playerName(snapshot, eventPlayerId(step))}</div>
          <div className="mt-2"><span className="font-black uppercase">Public:</span> {typeof publicMessage === 'string' ? publicMessage : '-'}</div>
          <div className="mt-2"><span className="font-black uppercase">Private:</span> {typeof privateThought === 'string' ? privateThought : '-'}</div>
        </div>
      </div>
      <div className="border border-black/15 rounded-[2px] bg-white p-2">
        <div className="text-[10px] font-black uppercase mb-1">Decision Bundle</div>
        <div className="text-[11px] font-mono whitespace-pre-wrap">{bundle ? formatJson(bundle) : 'No decision artifact for this event.'}</div>
      </div>
    </div>
  );
};

const DiffPanel = ({
  replayReport,
  replayDiff,
  eventHashes,
}: {
  replayReport: Record<string, unknown> | null;
  replayDiff: Record<string, unknown> | null;
  eventHashes: Record<string, unknown> | null;
}) => (
  <div className="space-y-3">
    <div className="border border-black/15 rounded-[2px] bg-white p-2">
      <div className="text-[10px] font-black uppercase mb-1">Replay Diff</div>
      <div className="grid grid-cols-3 gap-2 mb-2">
        <TextMetric label="Status" value={typeof replayDiff?.status === 'string' ? replayDiff.status : 'missing'} />
        <Metric label="Mismatch" value={typeof replayDiff?.first_mismatch_index === 'number' ? replayDiff.first_mismatch_index : 0} />
        <Metric label="Errors" value={Array.isArray(replayDiff?.errors) ? replayDiff.errors.length : 0} />
      </div>
      <pre className="text-[11px] font-mono whitespace-pre-wrap bg-black text-white p-3 rounded-[2px] max-h-64 overflow-auto brutal-scroll">
        {formatJson(replayDiff ?? { status: 'missing_replay_diff' })}
      </pre>
    </div>
    <div className="border border-black/15 rounded-[2px] bg-white p-2">
      <div className="text-[10px] font-black uppercase mb-1">Replay Report</div>
      <pre className="text-[11px] font-mono whitespace-pre-wrap bg-black text-white p-3 rounded-[2px] max-h-56 overflow-auto brutal-scroll">
        {formatJson(replayReport ?? { status: 'missing_replay_report' })}
      </pre>
    </div>
    <div className="border border-black/15 rounded-[2px] bg-white p-2">
      <div className="text-[10px] font-black uppercase mb-1">Event Hashes</div>
      <pre className="text-[11px] font-mono whitespace-pre-wrap bg-black text-white p-3 rounded-[2px] max-h-56 overflow-auto brutal-scroll">
        {formatJson(eventHashes ?? { status: 'missing_event_hashes' })}
      </pre>
    </div>
  </div>
);

const TextMetric = ({ label, value }: { label: string; value: string }) => (
  <div className="border border-black/15 bg-white rounded-[2px] px-2 py-1">
    <div className="text-[8px] uppercase font-bold text-gray-500">{label}</div>
    <div className="text-sm font-mono font-black truncate">{value}</div>
  </div>
);
