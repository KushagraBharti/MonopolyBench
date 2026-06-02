import { useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { NeoBadge } from '@/components/ui/NeoPrimitive';
import { cn } from '@/components/ui/cn';
import {
  fetchCampaign,
  fetchCampaignArtifact,
  fetchCampaignArtifacts,
  fetchCampaigns,
  fetchMicroResearchArtifact,
  fetchMicroResearchArtifacts,
  fetchMicroResearchReport,
  fetchMicroResearchReports,
  type CampaignDetail,
  type CampaignListItem,
  type MicroResearchReportDetail,
  type MicroResearchReportListItem,
  type ResearchArtifact,
  type ResearchArtifactEntry,
} from '@/net/artifacts';

type ResearchRoute =
  | { kind: 'index' }
  | { kind: 'campaign'; id: string }
  | { kind: 'micro'; id: string };

const parseResearchRoute = (): ResearchRoute => {
  const parts = window.location.pathname.split('/').filter(Boolean);
  if (parts[0] !== 'research') return { kind: 'index' };
  if (parts[1] === 'campaigns' && parts[2]) return { kind: 'campaign', id: parts[2] };
  if (parts[1] === 'micro' && parts[2]) return { kind: 'micro', id: parts[2] };
  return { kind: 'index' };
};

const formatJson = (value: unknown): string => {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
};

const getRecord = (value: unknown): Record<string, unknown> => {
  return value && typeof value === 'object' && !Array.isArray(value) ? (value as Record<string, unknown>) : {};
};

const getArray = (value: unknown): Record<string, unknown>[] => {
  return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === 'object') : [];
};

const numberText = (value: unknown): string => {
  if (typeof value !== 'number') return '-';
  return Number.isInteger(value) ? value.toLocaleString('en-US') : value.toFixed(4);
};

export const ResearchArtifactsPage = () => {
  const route = useMemo(() => parseResearchRoute(), []);
  const [campaigns, setCampaigns] = useState<CampaignListItem[]>([]);
  const [microReports, setMicroReports] = useState<MicroResearchReportListItem[]>([]);
  const [campaign, setCampaign] = useState<CampaignDetail | null>(null);
  const [microReport, setMicroReport] = useState<MicroResearchReportDetail | null>(null);
  const [artifacts, setArtifacts] = useState<ResearchArtifactEntry[]>([]);
  const [selectedArtifact, setSelectedArtifact] = useState<string | null>(null);
  const [artifact, setArtifact] = useState<ResearchArtifact | null>(null);
  const [status, setStatus] = useState('Loading research artifacts...');

  useEffect(() => {
    let active = true;
    if (route.kind === 'index') {
      Promise.all([fetchCampaigns(), fetchMicroResearchReports()])
        .then(([campaignPayload, reportPayload]) => {
          if (!active) return;
          setCampaigns(campaignPayload.campaigns ?? []);
          setMicroReports(reportPayload.reports ?? []);
          setStatus('Research artifact indexes loaded.');
        })
        .catch((err) => {
          if (active) setStatus(err instanceof Error ? err.message : 'Failed to load research artifacts.');
        });
    }
    if (route.kind === 'campaign') {
      Promise.all([fetchCampaign(route.id), fetchCampaignArtifacts(route.id)])
        .then(([detail, artifactIndex]) => {
          if (!active) return;
          setCampaign(detail);
          setArtifacts(artifactIndex.artifacts ?? []);
          setSelectedArtifact((artifactIndex.artifacts ?? []).find((item) => item.exists)?.name ?? null);
          setStatus('Campaign artifacts loaded.');
        })
        .catch((err) => {
          if (active) setStatus(err instanceof Error ? err.message : 'Failed to load campaign artifacts.');
        });
    }
    if (route.kind === 'micro') {
      Promise.all([fetchMicroResearchReport(route.id), fetchMicroResearchArtifacts(route.id)])
        .then(([detail, artifactIndex]) => {
          if (!active) return;
          setMicroReport(detail);
          setArtifacts(artifactIndex.artifacts ?? []);
          setSelectedArtifact((artifactIndex.artifacts ?? []).find((item) => item.exists)?.name ?? null);
          setStatus('Micro research artifacts loaded.');
        })
        .catch((err) => {
          if (active) setStatus(err instanceof Error ? err.message : 'Failed to load micro research artifacts.');
        });
    }
    return () => {
      active = false;
    };
  }, [route]);

  useEffect(() => {
    if (route.kind === 'index' || !selectedArtifact) return;
    let active = true;
    const loader =
      route.kind === 'campaign'
        ? fetchCampaignArtifact(route.id, selectedArtifact)
        : fetchMicroResearchArtifact(route.id, selectedArtifact);
    loader
      .then((payload) => {
        if (active) setArtifact(payload);
      })
      .catch(() => {
        if (active) setArtifact(null);
      });
    return () => {
      active = false;
    };
  }, [route, selectedArtifact]);

  if (route.kind === 'index') {
    return (
      <div className="min-h-screen overflow-y-auto bg-neo-bg p-6 text-black brutal-scroll">
        <ResearchHeader status={status} />
        <main className="mx-auto mt-5 grid max-w-screen-2xl grid-cols-1 gap-4 xl:grid-cols-2">
          <IndexSection title="Long Campaigns">
            {campaigns.map((item) => (
              <a
                key={item.campaign_id}
                href={`/research/campaigns/${encodeURIComponent(item.campaign_id)}`}
                className="block rounded-[3px] border-2 border-black bg-white p-4 shadow-neo transition-all hover:-translate-y-px hover:shadow-neo-lg"
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="text-sm font-black uppercase">{item.campaign_id}</div>
                  <NeoBadge variant={item.manifest_exists ? 'success' : 'warning'}>
                    {item.execution_status ?? 'planned'}
                  </NeoBadge>
                </div>
                <div className="mt-3 grid grid-cols-2 gap-2">
                  <Metric label="Runs" value={numberText(item.run_count)} />
                  <Metric label="Done" value={numberText(item.completed_run_count)} />
                </div>
                <div className="mt-3 break-all text-[11px] font-mono text-gray-500">{item.campaign_dir}</div>
              </a>
            ))}
            {campaigns.length === 0 ? <EmptyText text="No campaign artifact directories found." /> : null}
          </IndexSection>

          <IndexSection title="Micro Research Reports">
            {microReports.map((item) => (
              <a
                key={item.report_id}
                href={`/research/micro/${encodeURIComponent(item.report_id)}`}
                className="block rounded-[3px] border-2 border-black bg-white p-4 shadow-neo transition-all hover:-translate-y-px hover:shadow-neo-lg"
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="text-sm font-black uppercase">{item.report_id}</div>
                  <NeoBadge variant="info">{item.suite_family ?? 'research'}</NeoBadge>
                </div>
                <div className="mt-3 grid grid-cols-3 gap-2">
                  <Metric label="Scenarios" value={numberText(item.scenario_count)} />
                  <Metric label="Results" value={numberText(item.joined_result_count)} />
                  <Metric label="Labels" value={numberText(item.human_label_count)} />
                </div>
                <div className="mt-3 break-all text-[11px] font-mono text-gray-500">{item.report_dir}</div>
              </a>
            ))}
            {microReports.length === 0 ? <EmptyText text="No micro research reports found." /> : null}
          </IndexSection>
        </main>
      </div>
    );
  }

  const summary = route.kind === 'campaign' ? campaignSummary(campaign) : microSummary(microReport);
  const rows =
    route.kind === 'campaign'
      ? getArray(getRecord(campaign?.leaderboard).rows)
      : getArray(getRecord(microReport?.result_join).scenario_rows);

  return (
    <div className="flex min-h-screen w-full flex-col overflow-y-auto bg-neo-bg text-black lg:h-screen lg:flex-row lg:overflow-hidden">
      <aside className="flex w-full flex-col border-b-2 border-black bg-white lg:h-full lg:w-80 lg:border-b-0 lg:border-r-2">
        <header className="border-b-2 border-black bg-neo-bg/70 p-3">
          <a href="/research" className="inline-flex min-h-8 items-center text-base font-black uppercase tracking-normal">
            Research
          </a>
          <div className="mt-2 break-all text-[11px] font-mono text-gray-500">{route.id}</div>
          <div className="mt-3 grid grid-cols-2 gap-2">
            {summary.slice(0, 4).map(([label, value]) => (
              <Metric key={label} label={label} value={numberText(value)} />
            ))}
          </div>
        </header>
        <section className="min-h-0 flex-1 overflow-y-auto p-3 brutal-scroll">
          <div className="mb-2 text-[10px] font-black uppercase">Artifacts</div>
          <div className="space-y-1.5">
            {artifacts.map((item) => (
              <button
                key={item.name}
                type="button"
                onClick={() => setSelectedArtifact(item.name)}
                className={cn(
                  'flex w-full items-center justify-between gap-2 rounded-[2px] border px-2 py-1 text-left',
                  selectedArtifact === item.name ? 'border-black bg-neo-yellow/20' : 'border-black/10 bg-white'
                )}
                disabled={!item.exists}
              >
                <span className="truncate text-[10px] font-mono">{item.name}</span>
                <NeoBadge variant={item.exists ? 'success' : 'neutral'}>{item.kind}</NeoBadge>
              </button>
            ))}
          </div>
        </section>
      </aside>

      <main className="min-w-0 flex-1 overflow-y-auto p-4 brutal-scroll lg:p-5">
        <header className="flex flex-wrap items-center justify-between gap-3 border-b-2 border-black pb-4">
          <div>
            <h1 className="text-2xl font-black uppercase tracking-normal">
              {route.kind === 'campaign' ? 'Campaign Research' : 'Micro Research'}
            </h1>
            <div className="mt-1 text-[11px] font-mono text-gray-500">{status}</div>
          </div>
          <div className="flex gap-2">
            <NeoBadge variant="info">render-only</NeoBadge>
            <NeoBadge variant="neutral">prompt unchanged</NeoBadge>
          </div>
        </header>

        <section className="mt-5 grid grid-cols-1 gap-3 md:grid-cols-4">
          {summary.map(([label, value]) => (
            <Metric key={label} label={label} value={numberText(value)} />
          ))}
        </section>

        <section className="mt-5 grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
          <div className="overflow-hidden rounded-[3px] border-2 border-black bg-white shadow-neo">
            <div className="border-b-2 border-black bg-neo-bg/70 px-3 py-2 text-[10px] font-black uppercase">
              {route.kind === 'campaign' ? 'Leaderboard' : 'Scenario Join'}
            </div>
            <div className="max-h-[520px] overflow-auto brutal-scroll">
              <table className="w-full text-left text-[11px]">
                <thead className="bg-black text-[9px] uppercase text-white">
                  <tr>
                    {(route.kind === 'campaign'
                      ? ['Actor', 'Games', 'Win', 'Net', 'Rank']
                      : ['Scenario', 'Results', 'Models', 'Score', 'Fallback']
                    ).map((column) => (
                      <th key={column} className="px-3 py-2">{column}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.slice(0, 80).map((row, index) => (
                    <tr key={String(row.actor_id ?? row.scenario_id ?? index)} className="border-b border-black/10">
                      {route.kind === 'campaign' ? (
                        <>
                          <td className="px-3 py-2 font-mono">{String(row.actor_id ?? '-')}</td>
                          <td className="px-3 py-2 font-mono">{numberText(row.game_count)}</td>
                          <td className="px-3 py-2 font-mono">{numberText(row.win_rate)}</td>
                          <td className="px-3 py-2 font-mono">{numberText(row.average_final_net_worth)}</td>
                          <td className="px-3 py-2 font-mono">{numberText(row.average_final_rank)}</td>
                        </>
                      ) : (
                        <>
                          <td className="px-3 py-2 font-mono">{String(row.scenario_id ?? '-')}</td>
                          <td className="px-3 py-2 font-mono">{numberText(row.result_count)}</td>
                          <td className="px-3 py-2 font-mono">{numberText(row.model_count)}</td>
                          <td className="px-3 py-2 font-mono">{numberText(row.average_score)}</td>
                          <td className="px-3 py-2 font-mono">{numberText(row.fallback_rate)}</td>
                        </>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
              {rows.length === 0 ? <div className="p-4 text-sm text-gray-500">No rows.</div> : null}
            </div>
          </div>

          <div className="overflow-hidden rounded-[3px] border-2 border-black bg-white shadow-neo">
            <div className="border-b-2 border-black bg-neo-bg/70 px-3 py-2 text-[10px] font-black uppercase">
              Artifact Inspector
            </div>
            <pre className="max-h-[520px] overflow-auto whitespace-pre-wrap p-3 text-[11px] font-mono brutal-scroll">
              {artifactText(artifact)}
            </pre>
          </div>
        </section>
      </main>
    </div>
  );
};

const campaignSummary = (detail: CampaignDetail | null): [string, unknown][] => {
  const manifest = getRecord(detail?.manifest);
  return [
    ['Runs', manifest.run_count],
    ['Completed', manifest.completed_run_count],
    ['Failed', manifest.failed_run_count],
    ['Skipped', manifest.skipped_run_count],
    ['Budget', manifest.cost_budget],
    ['Runnable', manifest.runnable_with_long_runner_count],
  ];
};

const microSummary = (detail: MicroResearchReportDetail | null): [string, unknown][] => {
  const report = getRecord(detail?.micro_report);
  const labels = getRecord(detail?.label_summary);
  return [
    ['Scenarios', report.scenario_count],
    ['Categories', report.category_count],
    ['Results', report.joined_result_count],
    ['Labels', labels.label_count],
    ['Tasks', report.human_review_task_count],
    ['Suite', report.suite_family],
  ];
};

const artifactText = (artifact: ResearchArtifact | null): string => {
  if (!artifact) return 'Select an artifact.';
  if (artifact.kind === 'json') return formatJson(artifact.content);
  if (artifact.kind === 'jsonl') return formatJson(artifact.rows ?? []);
  return artifact.text ?? formatJson(artifact);
};

const ResearchHeader = ({ status }: { status: string }) => (
  <header className="mx-auto flex max-w-screen-2xl flex-wrap items-center justify-between gap-4 border-b-2 border-black pb-4">
    <div>
      <a href="/" className="inline-flex min-h-8 items-center text-xl font-black uppercase tracking-normal">
        Monopoly<span className="text-neo-pink">Bench</span>
      </a>
      <div className="mt-1 text-[11px] font-mono text-gray-500">Research artifact inspection</div>
    </div>
    <NeoBadge variant="info">{status}</NeoBadge>
  </header>
);

const IndexSection = ({ title, children }: { title: string; children: ReactNode }) => (
  <section>
    <div className="mb-2 text-[10px] font-black uppercase text-gray-500">{title}</div>
    <div className="grid grid-cols-1 gap-4">{children}</div>
  </section>
);

const EmptyText = ({ text }: { text: string }) => (
  <div className="rounded-[6px] border-2 border-dashed border-black/20 bg-white/70 p-5 text-sm text-gray-500">
    {text}
  </div>
);

const Metric = ({ label, value }: { label: string; value: string }) => (
  <div className="rounded-[2px] border border-black/15 bg-white px-3 py-2">
    <div className="text-[9px] font-black uppercase text-gray-500">{label}</div>
    <div className="text-lg font-mono font-black">{value}</div>
  </div>
);
