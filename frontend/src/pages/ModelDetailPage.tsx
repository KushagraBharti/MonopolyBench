import { useEffect, useMemo, useState } from 'react';
import { NeoBadge } from '@/components/ui/NeoPrimitive';
import { fetchModel, type ModelDetail } from '@/net/artifacts';

const parseModelId = (): string => {
  const marker = '/models/';
  const index = window.location.pathname.indexOf(marker);
  return index >= 0 ? decodeURIComponent(window.location.pathname.slice(index + marker.length)) : '';
};

const numberText = (value: unknown): string => {
  if (typeof value !== 'number') return '-';
  return Number.isInteger(value) ? value.toLocaleString('en-US') : value.toFixed(4);
};

export const ModelDetailPage = () => {
  const modelId = useMemo(() => parseModelId(), []);
  const [model, setModel] = useState<ModelDetail | null>(null);
  const [status, setStatus] = useState('Loading model...');

  useEffect(() => {
    let active = true;
    fetchModel(modelId)
      .then((payload) => {
        if (!active) return;
        setModel(payload);
        setStatus('Model loaded.');
      })
      .catch((err) => {
        if (!active) return;
        setStatus(err instanceof Error ? err.message : 'Failed to load model.');
      });
    return () => {
      active = false;
    };
  }, [modelId]);

  const runs = model?.runs ?? [];

  return (
    <div className="min-h-screen bg-neo-bg text-black p-6 overflow-y-auto brutal-scroll">
      <header className="mx-auto flex max-w-screen-2xl flex-wrap items-center justify-between gap-4 border-b-2 border-black pb-4">
        <div>
          <a href="/runs" className="inline-flex min-h-8 items-center text-xl font-black uppercase tracking-normal">
            Model
          </a>
          <div className="mt-1 text-[11px] font-mono text-gray-500 break-all">{modelId}</div>
        </div>
        <NeoBadge variant="info">{status}</NeoBadge>
      </header>
      <main className="mx-auto mt-5 max-w-screen-2xl space-y-5">
        <section className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <Metric label="Games" value={numberText(model?.game_count)} />
          <Metric label="Wins" value={numberText(model?.win_count)} />
          <Metric label="Win Rate" value={numberText(model?.win_rate)} />
          <Metric label="Avg Net" value={numberText(model?.average_final_net_worth)} />
          <Metric label="Tokens" value={numberText(model?.total_tokens)} />
        </section>
        <section className="border-2 border-black rounded-[3px] bg-white shadow-neo overflow-hidden">
          <div className="px-3 py-2 border-b-2 border-black bg-neo-bg/70 text-[10px] font-black uppercase">Runs</div>
          <div className="overflow-x-auto brutal-scroll">
            <table className="w-full min-w-[36rem] text-left text-[11px]">
              <thead className="bg-black text-white uppercase text-[9px]">
                <tr>
                  <th className="px-3 py-2">Run</th>
                  <th className="px-3 py-2">Players</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((run, index) => (
                  <tr key={`${run.run_id ?? index}`} className="border-b border-black/10">
                    <td className="px-3 py-2 font-mono">
                      <a href={`/runs/${encodeURIComponent(String(run.run_id ?? ''))}`}>
                        {String(run.run_id ?? '-')}
                      </a>
                    </td>
                    <td className="px-3 py-2 font-mono">{Array.isArray(run.players) ? run.players.length : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {runs.length === 0 ? <div className="p-4 text-sm text-gray-500">No runs found for this model.</div> : null}
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
