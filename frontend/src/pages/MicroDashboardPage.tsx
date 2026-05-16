import { startTransition, useEffect, useMemo, useState } from 'react'
import { NeoBadge, NeoButton, NeoCard } from '@/components/ui/NeoPrimitive'
import { cn } from '@/components/ui/cn'
import type { MicroScenario } from '@/net/contracts'
import {
  fetchMicroRun,
  fetchMicroScenarios,
  fetchMicroSuites,
  runMicroBatch,
  runMicroScenario,
  type MicroLeaderboard,
  type MicroRunDetail,
  type MicroScenarioSummary,
} from '@/net/micro'

type RunScope = 'suite' | 'category' | 'scenario'
type ScenarioCategory = 'ALL' | MicroScenario['category']

const CATEGORY_ORDER: ScenarioCategory[] = [
  'ALL',
  'BUY_OR_AUCTION',
  'AUCTION',
  'TRADE_PROPOSE',
  'TRADE_RESPONSE',
  'BUILD_OR_MORTGAGE',
  'LIQUIDATION',
  'JAIL',
  'POST_TURN_STRATEGY',
]

const promptConditions = ['default', 'minimal', 'pro_strategy_cheatsheet', 'no_private_thought', 'full_state', 'compact_state'] as const
const baselineOptions = ['', 'first_legal', 'random_legal', 'haliem_fixed_v1', 'pro_heuristic_v1'] as const
const reasoningOptions = ['low', 'medium', 'high'] as const

const formatLabel = (value: string): string =>
  value
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, (char) => char.toUpperCase())

const PageLink = ({ href, label, active }: { href: string; label: string; active: boolean }) => (
  <a
    href={href}
    className={cn(
      'px-3 py-1 text-[10px] font-black uppercase border-[1.5px] border-black rounded-[2px] transition-all duration-100',
      active ? 'bg-black text-white shadow-none' : 'bg-white text-black shadow-neo-sm hover:-translate-y-px hover:shadow-neo'
    )}
  >
    {label}
  </a>
)

const metric = (label: string, value: string | number, tone: 'neutral' | 'info' | 'success' | 'warning' = 'neutral') => (
  <NeoCard className="p-3 bg-white" variant="flat">
    <div className="text-[9px] font-black uppercase tracking-[0.2em] text-gray-500">{label}</div>
    <div className={cn(
      'mt-1 text-2xl font-black tabular-nums',
      tone === 'info' && 'text-neo-blue',
      tone === 'success' && 'text-emerald-700',
      tone === 'warning' && 'text-amber-700'
    )}>
      {value}
    </div>
  </NeoCard>
)

export const MicroDashboardPage = () => {
  const [scenarios, setScenarios] = useState<MicroScenarioSummary[]>([])
  const [suiteId, setSuiteId] = useState('micro-v1')
  const [suiteIds, setSuiteIds] = useState<string[]>(['micro-v1'])
  const [scope, setScope] = useState<RunScope>('suite')
  const [category, setCategory] = useState<ScenarioCategory>('BUY_OR_AUCTION')
  const [scenarioId, setScenarioId] = useState('')
  const [baseline, setBaseline] = useState<(typeof baselineOptions)[number]>('pro_heuristic_v1')
  const [modelId, setModelId] = useState('openai/gpt-oss-120b')
  const [displayName, setDisplayName] = useState('Micro Agent')
  const [promptCondition, setPromptCondition] = useState<(typeof promptConditions)[number]>('default')
  const [reasoningEffort, setReasoningEffort] = useState<(typeof reasoningOptions)[number]>('medium')
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [leaderboard, setLeaderboard] = useState<MicroLeaderboard | null>(null)
  const [batchId, setBatchId] = useState<string | null>(null)
  const [latestRun, setLatestRun] = useState<MicroRunDetail | null>(null)

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      try {
        const [scenarioItems, suites] = await Promise.all([fetchMicroScenarios(), fetchMicroSuites()])
        if (cancelled) return
        setScenarios(scenarioItems)
        setSuiteIds(suites.map((suite) => suite.suite_id))
        startTransition(() => {
          setScenarioId((current) => current || scenarioItems[0]?.scenario_id || '')
          setSuiteId((current) => current || suites[0]?.suite_id || 'micro-v1')
        })
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load micro dashboard data.')
        }
      }
    }
    void load()
    return () => {
      cancelled = true
    }
  }, [])

  const categoryCounts = useMemo(() => {
    const counts = new Map<MicroScenario['category'], number>()
    for (const item of scenarios) {
      counts.set(item.category, (counts.get(item.category) ?? 0) + 1)
    }
    return counts
  }, [scenarios])

  const scopedScenarios = useMemo(() => {
    if (category === 'ALL') return scenarios
    return scenarios.filter((item) => item.category === category)
  }, [category, scenarios])

  useEffect(() => {
    if (!scopedScenarios.length) return
    if (scenarioId && scopedScenarios.some((item) => item.scenario_id === scenarioId)) return
    setScenarioId(scopedScenarios[0].scenario_id)
  }, [scenarioId, scopedScenarios])

  const selectedScenario = scenarios.find((item) => item.scenario_id === scenarioId) ?? null
  const selectedCategoryCount = category === 'ALL' ? scenarios.length : categoryCounts.get(category) ?? 0
  const currentTarget =
    scope === 'suite'
      ? `${scenarios.length} scenarios`
      : scope === 'category'
        ? `${selectedCategoryCount} ${formatLabel(category)} scenarios`
        : selectedScenario?.title ?? 'No scenario selected'

  const handleRun = async () => {
    try {
      setRunning(true)
      setError(null)
      setLatestRun(null)
      if (scope === 'scenario') {
        const { run_id } = await runMicroScenario({
          scenario_id: scenarioId,
          openrouter_model_id: baseline ? null : modelId,
          name: displayName,
          baseline: baseline || null,
          prompt_condition: promptCondition,
          reasoning: { effort: reasoningEffort },
        })
        const detail = await fetchMicroRun(run_id)
        setLatestRun(detail)
        setLeaderboard(null)
        setBatchId(null)
        return
      }

      const scenarioIds =
        scope === 'category'
          ? scopedScenarios.map((item) => item.scenario_id)
          : null
      const batch = await runMicroBatch({
        suite_id: suiteId,
        openrouter_model_ids: baseline ? [] : [modelId],
        baseline: baseline || null,
        prompt_condition: promptCondition,
        reasoning: { effort: reasoningEffort },
        scenario_ids: scenarioIds,
      })
      setBatchId(batch.batch_id)
      setLeaderboard(batch.leaderboard)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Micro run failed.')
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="min-h-screen bg-neo-bg text-black">
      <div
        className="fixed inset-0 pointer-events-none opacity-80"
        style={{ backgroundImage: 'url(/background.png)', backgroundSize: 'cover', backgroundPosition: 'center' }}
      />
      <div className="relative mx-auto flex min-h-screen w-full max-w-[88rem] flex-col px-4 py-4 lg:px-6">
        <header className="flex flex-col gap-3 border-2 border-black bg-white/95 px-4 py-3 shadow-neo md:flex-row md:items-center md:justify-between">
          <div>
            <div className="text-xl font-black uppercase tracking-tight">
              Monopoly<span className="text-neo-pink ml-0.5">Bench</span>
            </div>
            <div className="mt-1 text-[10px] font-black uppercase tracking-[0.24em] text-gray-500">
              Micro Run Dashboard
            </div>
          </div>
          <nav className="flex flex-wrap items-center gap-2">
            <PageLink href="/" label="Live" active={false} />
            <PageLink href="/micro" label="Dashboard" active />
            <PageLink href="/micro/detail" label="Detail" active={false} />
          </nav>
        </header>

        <main className="grid flex-1 gap-4 py-4 xl:grid-cols-[25rem_minmax(0,1fr)]">
          <section className="space-y-4">
            <NeoCard className="p-4 bg-white/95">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Run Setup</div>
                  <div className="mt-1 text-lg font-black uppercase">Choose Scope</div>
                </div>
                <NeoBadge variant={baseline ? 'success' : 'warning'}>{baseline || 'Live Model'}</NeoBadge>
              </div>

              <div className="mt-4 grid grid-cols-3 gap-2">
                {(['suite', 'category', 'scenario'] as const).map((item) => (
                  <button
                    key={item}
                    type="button"
                    onClick={() => setScope(item)}
                    className={cn(
                      'border-2 border-black rounded-[3px] px-2 py-2 text-[10px] font-black uppercase transition-all duration-100',
                      scope === item ? 'bg-black text-white shadow-none' : 'bg-white shadow-neo-sm hover:-translate-y-px hover:shadow-neo'
                    )}
                  >
                    {item}
                  </button>
                ))}
              </div>

              <div className="mt-4 space-y-3">
                <label className="block">
                  <span className="text-[9px] font-bold uppercase text-gray-500">Suite</span>
                  <select
                    value={suiteId}
                    onChange={(event) => setSuiteId(event.target.value)}
                    className="mt-1 w-full border-2 border-black bg-white px-2.5 py-2 text-[12px] font-semibold shadow-neo-sm outline-none"
                  >
                    {suiteIds.map((item) => (
                      <option key={item} value={item}>{item}</option>
                    ))}
                  </select>
                </label>

                <label className="block">
                  <span className="text-[9px] font-bold uppercase text-gray-500">Category</span>
                  <select
                    value={category}
                    onChange={(event) => setCategory(event.target.value as ScenarioCategory)}
                    className="mt-1 w-full border-2 border-black bg-white px-2.5 py-2 text-[12px] font-semibold shadow-neo-sm outline-none"
                  >
                    {CATEGORY_ORDER.map((item) => (
                      <option key={item} value={item}>
                        {item === 'ALL' ? 'All categories' : `${formatLabel(item)} (${categoryCounts.get(item as MicroScenario['category']) ?? 0})`}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="block">
                  <span className="text-[9px] font-bold uppercase text-gray-500">Scenario</span>
                  <select
                    value={scenarioId}
                    onChange={(event) => setScenarioId(event.target.value)}
                    className="mt-1 w-full border-2 border-black bg-white px-2.5 py-2 text-[12px] font-semibold shadow-neo-sm outline-none"
                  >
                    {scopedScenarios.map((item) => (
                      <option key={item.scenario_id} value={item.scenario_id}>
                        {item.title}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
            </NeoCard>

            <NeoCard className="p-4 bg-white/95">
              <div className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Agent</div>
              <div className="mt-3 space-y-3">
                <label className="block">
                  <span className="text-[9px] font-bold uppercase text-gray-500">Baseline</span>
                  <select
                    value={baseline}
                    onChange={(event) => setBaseline(event.target.value as (typeof baselineOptions)[number])}
                    className="mt-1 w-full border-2 border-black bg-white px-2.5 py-2 text-[12px] font-semibold shadow-neo-sm outline-none"
                  >
                    {baselineOptions.map((item) => (
                      <option key={item || 'openrouter'} value={item}>{item || 'OpenRouter model'}</option>
                    ))}
                  </select>
                </label>
                <label className="block">
                  <span className="text-[9px] font-bold uppercase text-gray-500">Model ID</span>
                  <input
                    value={modelId}
                    onChange={(event) => setModelId(event.target.value)}
                    className="mt-1 w-full border-2 border-black bg-neo-bg px-2.5 py-2 text-[12px] font-mono shadow-neo-sm outline-none"
                  />
                </label>
                <label className="block">
                  <span className="text-[9px] font-bold uppercase text-gray-500">Display Name</span>
                  <input
                    value={displayName}
                    onChange={(event) => setDisplayName(event.target.value)}
                    className="mt-1 w-full border-2 border-black bg-white px-2.5 py-2 text-[12px] font-semibold shadow-neo-sm outline-none"
                  />
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <label className="block">
                    <span className="text-[9px] font-bold uppercase text-gray-500">Prompt</span>
                    <select
                      value={promptCondition}
                      onChange={(event) => setPromptCondition(event.target.value as (typeof promptConditions)[number])}
                      className="mt-1 w-full border-2 border-black bg-white px-2.5 py-2 text-[12px] font-semibold shadow-neo-sm outline-none"
                    >
                      {promptConditions.map((item) => (
                        <option key={item} value={item}>{item}</option>
                      ))}
                    </select>
                  </label>
                  <label className="block">
                    <span className="text-[9px] font-bold uppercase text-gray-500">Reasoning</span>
                    <select
                      value={reasoningEffort}
                      onChange={(event) => setReasoningEffort(event.target.value as (typeof reasoningOptions)[number])}
                      className="mt-1 w-full border-2 border-black bg-white px-2.5 py-2 text-[12px] font-semibold shadow-neo-sm outline-none"
                    >
                      {reasoningOptions.map((item) => (
                        <option key={item} value={item}>{item}</option>
                      ))}
                    </select>
                  </label>
                </div>
                <NeoButton
                  type="button"
                  className="w-full justify-center"
                  disabled={running || !scenarios.length || (scope === 'scenario' && !scenarioId)}
                  onClick={() => void handleRun()}
                >
                  {running ? 'Running...' : `Run ${formatLabel(scope)}`}
                </NeoButton>
              </div>
            </NeoCard>
          </section>

          <section className="space-y-4">
            <NeoCard className="overflow-hidden bg-white/95">
              <div className="border-b-2 border-black bg-black px-4 py-3 text-white">
                <div className="text-[10px] font-black uppercase tracking-[0.22em] text-white/65">Current Target</div>
                <div className="mt-1 text-2xl font-black uppercase leading-tight">{currentTarget}</div>
              </div>
              <div className="grid gap-2 p-3 sm:grid-cols-2 lg:grid-cols-4">
                {metric('Scenarios', scenarios.length, 'info')}
                {metric('Selected', selectedCategoryCount, 'neutral')}
                {metric('Categories', categoryCounts.size, 'success')}
                {metric('Last Avg', leaderboard?.rows[0]?.average_score ?? latestRun?.result?.score.total ?? '-', 'warning')}
              </div>
            </NeoCard>

            <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_20rem]">
              <NeoCard className="p-4 bg-white/95">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Latest Output</div>
                    <div className="mt-1 text-lg font-black uppercase">{latestRun ? 'Single Run' : leaderboard ? 'Batch Leaderboard' : 'Ready'}</div>
                  </div>
                  {batchId ? <NeoBadge variant="info">{batchId}</NeoBadge> : latestRun ? <NeoBadge variant="success">{latestRun.result?.score.label}</NeoBadge> : null}
                </div>

                {latestRun ? (
                  <div className="mt-4 grid gap-3 md:grid-cols-2">
                    <div className="rounded-[3px] border border-black/10 bg-neo-bg/70 p-3 text-[11px]">
                      <div className="text-[9px] font-black uppercase tracking-[0.18em] text-gray-500">Action</div>
                      <div className="mt-1 font-mono text-sm">{latestRun.decision_bundle?.final_action?.action ?? 'n/a'}</div>
                      <div className="mt-2 text-gray-600">{latestRun.decision_bundle?.final_action?.public_message || 'No public message.'}</div>
                    </div>
                    <div className="rounded-[3px] border border-black/10 bg-white p-3 text-[11px]">
                      <div className="text-[9px] font-black uppercase tracking-[0.18em] text-gray-500">Score</div>
                      <div className="mt-1 text-2xl font-black">{latestRun.result?.score.total ?? latestRun.summary.result.score?.total}</div>
                      <div className="mt-1 font-mono text-[10px] text-gray-600">{latestRun.run_id}</div>
                    </div>
                    <a
                      href="/micro/detail"
                      className="md:col-span-2 border-2 border-black bg-neo-yellow px-3 py-2 text-center text-[11px] font-black uppercase shadow-neo-sm transition-all duration-100 hover:-translate-y-px hover:shadow-neo"
                    >
                      Open Detail Inspector
                    </a>
                  </div>
                ) : leaderboard?.rows.length ? (
                  <div className="mt-4 overflow-x-auto brutal-scroll">
                    <table className="w-full min-w-[42rem] border-collapse text-left text-[11px]">
                      <thead>
                        <tr className="border-b-2 border-black">
                          {['Model', 'Cases', 'Avg', 'Fallback', 'Retry', 'Invalid', 'Latency'].map((item) => (
                            <th key={item} className="px-2 py-2 font-black uppercase text-gray-500">{item}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {leaderboard.rows.map((row) => (
                          <tr key={row.model} className="border-b border-black/10">
                            <td className="px-2 py-2 font-mono">{row.model}</td>
                            <td className="px-2 py-2">{row.scenario_count}</td>
                            <td className="px-2 py-2 font-black">{row.average_score}</td>
                            <td className="px-2 py-2">{row.fallback_rate}</td>
                            <td className="px-2 py-2">{row.retry_rate}</td>
                            <td className="px-2 py-2">{row.invalid_rate}</td>
                            <td className="px-2 py-2">{row.average_latency_ms} ms</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="mt-4 rounded-[3px] border border-dashed border-black/20 bg-neo-bg/70 p-4 text-sm text-gray-600">
                    Pick a scope and run a baseline first. Baselines do not need an API key and are the fastest way to check the suite.
                  </div>
                )}
              </NeoCard>

              <NeoCard className="p-4 bg-white/95">
                <div className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Category Mix</div>
                <div className="mt-3 space-y-2">
                  {CATEGORY_ORDER.filter((item) => item !== 'ALL').map((item) => {
                    const count = categoryCounts.get(item) ?? 0
                    const active = item === category
                    return (
                      <button
                        key={item}
                        type="button"
                        onClick={() => {
                          setCategory(item)
                          setScope('category')
                        }}
                        className={cn(
                          'w-full rounded-[3px] border border-black/15 px-2.5 py-2 text-left transition-all duration-100',
                          active ? 'bg-neo-cyan/25 shadow-neo-sm' : 'bg-white hover:-translate-y-px hover:shadow-neo-sm'
                        )}
                      >
                        <div className="flex items-center justify-between gap-2">
                          <span className="text-[10px] font-black uppercase">{formatLabel(item)}</span>
                          <span className="font-mono text-[10px]">{count}</span>
                        </div>
                      </button>
                    )
                  })}
                </div>
              </NeoCard>
            </div>

            {selectedScenario ? (
              <NeoCard className="p-4 bg-white/95">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <div className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Selected Scenario</div>
                    <div className="mt-1 text-lg font-black uppercase">{selectedScenario.title}</div>
                    <p className="mt-2 max-w-3xl text-[12px] leading-relaxed text-gray-600">{selectedScenario.description}</p>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    <NeoBadge variant="info">{formatLabel(selectedScenario.category)}</NeoBadge>
                    <NeoBadge variant="neutral">{selectedScenario.difficulty}</NeoBadge>
                    <NeoBadge variant="warning">{selectedScenario.scoring_mode}</NeoBadge>
                  </div>
                </div>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {selectedScenario.tags.map((tag) => (
                    <NeoBadge key={tag} variant="neutral" className="bg-neo-bg">{tag}</NeoBadge>
                  ))}
                </div>
              </NeoCard>
            ) : null}

            {error ? (
              <NeoCard className="p-4 bg-neo-pink/10 border-neo-pink/70">
                <div className="text-[10px] font-black uppercase tracking-[0.2em] text-neo-red">Error</div>
                <div className="mt-2 text-[12px] leading-relaxed text-gray-700">{error}</div>
              </NeoCard>
            ) : null}
          </section>
        </main>
      </div>
    </div>
  )
}
