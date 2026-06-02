import { useEffect, useMemo, useState } from 'react';
import { NeoBadge } from '@/components/ui/NeoPrimitive';
import { fetchRun, fetchRuns, type RunDetail, type RunListItem } from '@/net/artifacts';

const parseRunId = (): string | null => {
  const parts = window.location.pathname.split('/').filter(Boolean);
  return parts[0] === 'runs' ? parts[1] ?? null : null;
};

const getRecord = (value: unknown): Record<string, unknown> =>
  value && typeof value === 'object' && !Array.isArray(value) ? (value as Record<string, unknown>) : {};

const getArray = (value: unknown): Record<string, unknown>[] =>
  Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === 'object') : [];

const numberText = (value: unknown): string => {
  if (typeof value !== 'number') return '-';
  return Number.isInteger(value) ? value.toLocaleString('en-US') : value.toFixed(4);
};

export const RunsPage = () => {
  const runId = useMemo(() => parseRunId(), []);
  const [runs, setRuns] = useState<RunListItem[]>([]);
  const [detail, setDetail] = useState<RunDetail | null>(null);
  const [status, setStatus] = useState('Loading runs...');

  useEffect(() => {
    let active = true;
    if (runId) {
      fetchRun(runId)
        .then((payload) => {
          if (!active) return;
          setDetail(payload);
          setStatus('Run loaded.');
        })
        .catch((err) => {
          if (!active) return;
          setStatus(err instanceof Error ? err.message : 'Failed to load run.');
        });
    } else {
      fetchRuns()
        .then((payload) => {
          if (!active) return;
          setRuns(payload.runs ?? []);
          setStatus(payload.runs?.length ? 'Runs loaded.' : 'No runs found.');
        })
        .catch((err) => {
          if (!active) return;
          setStatus(err instanceof Error ? err.message : 'Failed to load runs.');
        });
    }
    return () => {
      active = false;
    };
  }, [runId]);

  if (!runId) {
    return (
      <div className="min-h-screen bg-neo-bg text-black p-6 overflow-y-auto brutal-scroll">
        <header className="mx-auto flex max-w-screen-2xl flex-wrap items-center justify-between gap-4 border-b-2 border-black pb-4">
          <a href="/" className="inline-flex min-h-8 items-center text-xl font-black uppercase tracking-normal">
            Monopoly<span className="text-neo-pink">Bench</span>
          </a>
          <NeoBadge variant="info">{status}</NeoBadge>
        </header>
        <main className="mx-auto mt-5 grid max-w-screen-2xl grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {runs.map((run) => (
            <a
              key={run.run_id}
              href={`/runs/${encodeURIComponent(run.run_id)}`}
              className="border-2 border-black bg-white rounded-[3px] shadow-neo p-4 hover:-translate-y-px hover:shadow-neo-lg transition-all"
            >
              <div className="flex items-center justify-between gap-3">
                <div className="text-sm font-black uppercase truncate">{run.run_id}</div>
                <NeoBadge variant={run.replay_report_exists ? 'success' : 'warning'}>
                  {run.replay_report_exists ? 'replay' : 'partial'}
                </NeoBadge>
              </div>
              <div className="mt-3 grid grid-cols-3 gap-2">
                <Metric label="Turns" value={numberText(run.turn_count)} />
                <Metric label="Seed" value={numberText(run.seed)} />
                <Metric label="Winner" value={run.winner_player_id ?? '-'} />
              </div>
              <div className="mt-3 text-[11px] font-mono text-gray-500 break-all">{run.run_dir}</div>
            </a>
          ))}
          {runs.length === 0 ? (
            <div className="rounded-[6px] border-2 border-dashed border-black/20 bg-white/70 p-5 text-sm text-gray-500">
              No run artifact directories found.
            </div>
          ) : null}
        </main>
      </div>
    );
  }

  const scorecardRun = getRecord(detail?.scorecard.run);
  const players = getArray(detail?.scorecard.players);
  const replayReport = getRecord(detail?.replay_report);
  const traceSummary = getRecord(detail?.trace_summary);
  const failureSummary = getRecord(detail?.failure_summary);
  const usageTotals = getRecord(detail?.usage.totals);

  return (
    <div className="min-h-screen bg-neo-bg text-black p-6 overflow-y-auto brutal-scroll">
      <header className="mx-auto flex max-w-screen-2xl flex-wrap items-center justify-between gap-4 border-b-2 border-black pb-4">
        <div>
          <a href="/runs" className="inline-flex min-h-8 items-center text-xl font-black uppercase tracking-normal">
            Runs
          </a>
          <div className="mt-1 text-[11px] font-mono text-gray-500 break-all">{runId}</div>
        </div>
        <div className="flex flex-wrap gap-2">
          <a className="inline-flex min-h-8 items-center border-2 border-black bg-white px-3 py-1 text-[10px] font-black uppercase shadow-neo" href={`/runs/${encodeURIComponent(runId)}/replay`}>
            Replay
          </a>
          <a className="inline-flex min-h-8 items-center border-2 border-black bg-white px-3 py-1 text-[10px] font-black uppercase shadow-neo" href={`/runs/${encodeURIComponent(runId)}/review`}>
            Review
          </a>
          <NeoBadge variant="info">{status}</NeoBadge>
        </div>
      </header>
      <main className="mx-auto mt-5 max-w-screen-2xl space-y-5">
        <section className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <Metric label="Winner" value={String(scorecardRun.winner_player_id ?? '-')} />
          <Metric label="Replay" value={String(replayReport.status ?? '-')} />
          <Metric label="Events" value={numberText(scorecardRun.total_event_count)} />
          <Metric label="Tokens" value={numberText(usageTotals.total_tokens)} />
          <Metric label="Cost" value={numberText(usageTotals.cost)} />
        </section>
        <section className="grid grid-cols-1 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)] gap-4">
          <div className="border-2 border-black rounded-[3px] bg-white shadow-neo overflow-hidden">
            <div className="px-3 py-2 border-b-2 border-black bg-neo-bg/70 text-[10px] font-black uppercase">Players</div>
            <div className="overflow-x-auto brutal-scroll">
              <table className="w-full min-w-[44rem] text-left text-[11px]">
                <thead className="bg-black text-white uppercase text-[9px]">
                  <tr>
                    <th className="px-3 py-2">Player</th>
                    <th className="px-3 py-2">Model</th>
                    <th className="px-3 py-2">Rank</th>
                    <th className="px-3 py-2">Net Worth</th>
                    <th className="px-3 py-2">Fallbacks</th>
                  </tr>
                </thead>
                <tbody>
                  {players.map((player) => (
                    <tr key={String(player.player_id)} className="border-b border-black/10">
                      <td className="px-3 py-2 font-mono">{String(player.player_id ?? '-')}</td>
                      <td className="px-3 py-2 font-mono">
                        <a href={`/models/${String(player.openrouter_model_id ?? 'unknown').replace(/\//g, '__')}`}>
                          {String(player.openrouter_model_id ?? 'unknown')}
                        </a>
                      </td>
                      <td className="px-3 py-2 font-mono">{numberText(player.final_rank)}</td>
                      <td className="px-3 py-2 font-mono">{numberText(player.final_net_worth_estimate)}</td>
                      <td className="px-3 py-2 font-mono">{numberText(player.fallbacks_used)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <div className="border-2 border-black rounded-[3px] bg-white shadow-neo p-4">
            <div className="text-[10px] font-black uppercase">Trace / Failure Summary</div>
            <pre className="mt-3 max-h-[380px] overflow-auto brutal-scroll text-[11px] font-mono bg-black text-white p-3 rounded-[2px]">
              {JSON.stringify({ traceSummary, failureSummary, replayReport }, null, 2)}
            </pre>
          </div>
        </section>
      </main>
    </div>
  );
};

const Metric = ({ label, value }: { label: string; value: string }) => (
  <div className="border-2 border-black rounded-[3px] bg-white p-3 shadow-neo min-w-0">
    <div className="text-[9px] font-black uppercase text-gray-500">{label}</div>
    <div className="mt-1 text-sm font-mono font-black truncate">{value}</div>
  </div>
);
