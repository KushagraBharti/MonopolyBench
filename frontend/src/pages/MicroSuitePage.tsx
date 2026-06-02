import {
  startTransition,
  useDeferredValue,
  useEffect,
  useMemo,
  useState,
} from 'react'
import { Board } from '@/components/board/Board'
import { PlayerCard } from '@/components/panels/PlayerCard'
import { NeoBadge, NeoButton, NeoCard } from '@/components/ui/NeoPrimitive'
import { cn } from '@/components/ui/cn'
import type { MicroScenario, StateSnapshot } from '@/net/contracts'
import {
  fetchMicroRun,
  fetchMicroScenario,
  fetchMicroScenarios,
  legalActionArgKeys,
  runMicroBatch,
  runMicroScenario,
  type MicroLeaderboard,
  type MicroRunDetail,
  type MicroScenarioSummary,
} from '@/net/micro'
import { computeNetWorthSimple, selectOwnedSpaces } from '@/domain/monopoly/selectors'

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

const reasoningOptions = ['low', 'medium', 'high'] as const
const MICRO_PROMPT_CONDITION = 'live_game'

const PageLink = ({ href, label, active }: { href: string; label: string; active: boolean }) => (
  <a
    href={href}
    className={cn(
      'inline-flex min-h-8 items-center px-3 py-1 text-[10px] font-black uppercase border-[1.5px] border-black rounded-[2px] transition-all duration-100',
      active ? 'bg-black text-white shadow-none' : 'bg-white text-black shadow-neo-sm hover:-translate-y-px hover:shadow-neo'
    )}
  >
    {label}
  </a>
)

const boardCenter = (
  <div className="z-10 flex max-w-[22rem] flex-col items-center gap-3 text-center px-6">
    <span className="bg-white/85 px-2 py-1 text-[10px] font-black uppercase tracking-[0.25em] border-[1.5px] border-black">
      Micro Decision Suite
    </span>
    <div className="rotate-[-4deg] border-2 border-black bg-white px-5 py-4 shadow-neo">
      <div className="text-3xl font-black uppercase tracking-normal leading-none">One Move</div>
      <div className="mt-1 text-[11px] font-medium text-gray-600">
        Curated board states for auctions, trades, jail timing, and cash-management choices.
      </div>
    </div>
  </div>
)

const scenarioHighlightIndices = (
  scenario: MicroScenario | null,
  selectedActionName: string | null
): number[] => {
  if (!scenario) return []
  const actions = scenario.decision_point.legal_actions
  if (selectedActionName) {
    const matching = actions.find((action) => action.action === selectedActionName)
    return matching?.ui_hints?.highlight_space_indices ?? []
  }
  return Array.from(
    new Set(actions.flatMap((action) => action.ui_hints?.highlight_space_indices ?? []))
  )
}

const formatActionLabel = (value: string): string =>
  value
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, (char) => char.toUpperCase())

const formatArgLabel = (value: string): string =>
  value
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())

const extractAttemptErrors = (run: MicroRunDetail | null): string[] => {
  if (!run?.decision_bundle?.attempts?.length) return []
  return run.decision_bundle.attempts.flatMap((attempt) => attempt.validation_errors ?? [])
}

const playerCards = (
  snapshot: StateSnapshot | null,
  focalPlayerId: string | null,
  focalModelId: string,
  deedHighlight: number | null,
  setDeedHighlight: (index: number | null) => void,
  run: MicroRunDetail | null
) => {
  if (!snapshot) return null
  return snapshot.players.map((player) => {
    const properties = selectOwnedSpaces(snapshot, player.player_id)
    const latestThought =
      player.player_id === focalPlayerId
        ? run?.decision_bundle?.final_action?.private_thought ?? null
        : null
    return (
      <PlayerCard
        key={player.player_id}
        playerId={player.player_id}
        name={player.name}
        modelId={player.player_id === focalPlayerId ? focalModelId : 'fixture player'}
        cash={player.cash}
        propertyCount={properties.length}
        netWorth={computeNetWorthSimple(player.cash, properties)}
        inJail={player.in_jail}
        bankrupt={player.bankrupt}
        isActive={snapshot.active_player_id === player.player_id}
        properties={properties}
        deedHighlight={deedHighlight}
        onToggleHighlight={(index) => setDeedHighlight(deedHighlight === index ? null : index)}
        latestThought={latestThought}
      />
    )
  })
}

export const MicroSuitePage = () => {
  const [scenarios, setScenarios] = useState<MicroScenarioSummary[]>([])
  const [selectedCategory, setSelectedCategory] = useState<ScenarioCategory>('ALL')
  const [search, setSearch] = useState('')
  const deferredSearch = useDeferredValue(search)
  const [selectedScenarioId, setSelectedScenarioId] = useState<string | null>(null)
  const [scenario, setScenario] = useState<MicroScenario | null>(null)
  const [scenarioLoading, setScenarioLoading] = useState(false)
  const [loadingMessage, setLoadingMessage] = useState('Loading scenarios...')
  const [error, setError] = useState<string | null>(null)
  const [selectedActionName, setSelectedActionName] = useState<string | null>(null)
  const [deedHighlight, setDeedHighlight] = useState<number | null>(null)
  const [run, setRun] = useState<MicroRunDetail | null>(null)
  const [running, setRunning] = useState(false)
  const [batchRunning, setBatchRunning] = useState(false)
  const [batchId, setBatchId] = useState<string | null>(null)
  const [leaderboard, setLeaderboard] = useState<MicroLeaderboard | null>(null)
  const [modelId, setModelId] = useState('openai/gpt-oss-120b')
  const [modelName, setModelName] = useState('Micro Agent')
  const [reasoningEffort, setReasoningEffort] = useState<(typeof reasoningOptions)[number]>('medium')

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      try {
        setLoadingMessage('Loading scenarios...')
        const items = await fetchMicroScenarios()
        if (cancelled) return
        setScenarios(items)
        if (items.length > 0) {
          startTransition(() => {
            setSelectedScenarioId((current) => current ?? items[0].scenario_id)
          })
        }
      } catch (err) {
        if (cancelled) return
        setError(err instanceof Error ? err.message : 'Failed to load micro scenarios.')
      }
    }
    void load()
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (!selectedScenarioId) return
    let cancelled = false
    const loadScenario = async () => {
      try {
        setScenarioLoading(true)
        const payload = await fetchMicroScenario(selectedScenarioId)
        if (cancelled) return
        setScenario(payload)
        setSelectedActionName(payload.decision_point.legal_actions[0]?.action ?? null)
        setDeedHighlight(null)
      } catch (err) {
        if (cancelled) return
        setError(err instanceof Error ? err.message : 'Failed to load selected scenario.')
      } finally {
        if (!cancelled) {
          setScenarioLoading(false)
        }
      }
    }
    void loadScenario()
    return () => {
      cancelled = true
    }
  }, [selectedScenarioId])

  const filteredScenarios = useMemo(() => {
    const query = deferredSearch.trim().toLowerCase()
    return scenarios.filter((item) => {
      if (selectedCategory !== 'ALL' && item.category !== selectedCategory) return false
      if (!query) return true
      return (
        item.title.toLowerCase().includes(query) ||
        item.description.toLowerCase().includes(query) ||
        item.tags.some((tag) => tag.toLowerCase().includes(query)) ||
        item.research_metadata?.target_capability.toLowerCase().includes(query) ||
        item.research_metadata?.expected_failure_modes.some((mode) => mode.toLowerCase().includes(query))
      )
    })
  }, [deferredSearch, scenarios, selectedCategory])

  useEffect(() => {
    if (!filteredScenarios.length) return
    if (selectedScenarioId && filteredScenarios.some((item) => item.scenario_id === selectedScenarioId)) return
    startTransition(() => {
      setSelectedScenarioId(filteredScenarios[0].scenario_id)
      setRun(null)
    })
  }, [filteredScenarios, selectedScenarioId])

  const highlightIndices = useMemo(
    () => scenarioHighlightIndices(scenario, selectedActionName),
    [scenario, selectedActionName]
  )
  const snapshot = scenario?.decision_point.state ?? null
  const focalPlayerId = scenario?.focal_player_id ?? null
  const focalPlayerName =
    snapshot?.players.find((player) => player.player_id === focalPlayerId)?.name ?? focalPlayerId ?? 'Focal player'
  const attemptErrors = extractAttemptErrors(run)

  const handleRun = async () => {
    if (!scenario) return
    try {
      const modelValue = modelId.trim()
      if (!modelValue) {
        throw new Error('Model ID is required.')
      }
      setRunning(true)
      setError(null)
      setLoadingMessage('Running selected micro scenario...')
      const { run_id } = await runMicroScenario({
        scenario_id: scenario.scenario_id,
        openrouter_model_id: modelValue,
        name: modelName || null,
        reasoning: { effort: reasoningEffort },
        prompt_condition: MICRO_PROMPT_CONDITION,
      })
      const detail = await fetchMicroRun(run_id)
      setRun(detail)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run micro scenario.')
    } finally {
      setRunning(false)
      setLoadingMessage('Loading scenarios...')
    }
  }

  const handleBatchRun = async (scope: 'category' | 'suite') => {
    try {
      const modelValue = modelId.trim()
      if (!modelValue) {
        throw new Error('Model ID is required.')
      }
      setBatchRunning(true)
      setError(null)
      const scenarioIds =
        scope === 'category'
          ? filteredScenarios.map((item) => item.scenario_id)
          : null
      const payload = await runMicroBatch({
        suite_id: 'micro-v1',
        openrouter_model_ids: [modelValue],
        prompt_condition: MICRO_PROMPT_CONDITION,
        reasoning: { effort: reasoningEffort },
        scenario_ids: scenarioIds,
      })
      setBatchId(payload.batch_id)
      setLeaderboard(payload.leaderboard)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run micro batch.')
    } finally {
      setBatchRunning(false)
    }
  }

  return (
    <div className="min-h-screen bg-neo-bg text-black">
      <div className="absolute inset-0 pointer-events-none opacity-80"
        style={{
          backgroundImage: 'url(/background.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      />
      <div className="relative grid min-h-screen grid-cols-1 xl:grid-cols-[22rem_minmax(0,1fr)_22rem] 2xl:grid-cols-[24rem_minmax(0,1fr)_23rem]">
        <aside className="min-w-0 border-b-2 border-black bg-white/95 backdrop-blur flex flex-col xl:h-screen xl:border-b-0 xl:border-r-2">
          <header className="px-4 py-3 border-b-2 border-black bg-neo-bg/70">
            <div className="flex flex-col gap-3">
              <div className="min-w-0">
                <div className="text-base font-black uppercase tracking-normal leading-none">
                  Monopoly<span className="text-neo-pink ml-0.5">Bench</span>
                </div>
                <div className="mt-1 text-[10px] font-medium uppercase tracking-[0.24em] text-gray-500">
                  Micro Decision Suite
                </div>
              </div>
              <div className="flex flex-wrap items-center gap-1.5">
                <PageLink href="/" label="Live" active={false} />
                <PageLink href="/micro" label="Dashboard" active={false} />
                <PageLink href="/micro/detail" label="Detail" active />
              </div>
            </div>
          </header>

          <div className="flex-1 overflow-y-auto brutal-scroll p-3 space-y-3">
            <NeoCard className="p-3 bg-white">
              <div className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Model Config</div>
              <div className="mt-2 space-y-2">
                <label className="block">
                  <span className="text-[9px] font-bold uppercase text-gray-500">Model Id</span>
                  <input
                    value={modelId}
                    onChange={(event) => setModelId(event.target.value)}
                    className="mt-1 w-full border-2 border-black bg-neo-bg px-2.5 py-2 text-[12px] font-mono shadow-neo-sm outline-none"
                  />
                </label>
                <label className="block">
                  <span className="text-[9px] font-bold uppercase text-gray-500">Display Name</span>
                  <input
                    value={modelName}
                    onChange={(event) => setModelName(event.target.value)}
                    className="mt-1 w-full border-2 border-black bg-white px-2.5 py-2 text-[12px] font-semibold shadow-neo-sm outline-none"
                  />
                </label>
                <label className="block">
                  <span className="text-[9px] font-bold uppercase text-gray-500">Reasoning</span>
                  <select
                    value={reasoningEffort}
                    onChange={(event) => setReasoningEffort(event.target.value as (typeof reasoningOptions)[number])}
                    className="mt-1 w-full border-2 border-black bg-white px-2.5 py-2 text-[12px] font-semibold shadow-neo-sm outline-none"
                  >
                    {reasoningOptions.map((effort) => (
                      <option key={effort} value={effort}>
                        {effort}
                      </option>
                    ))}
                  </select>
                </label>
                <div className="rounded-[4px] border border-black/10 bg-neo-bg/70 px-3 py-2 text-[11px] font-semibold text-gray-600">
                  Prompt mode is fixed to live_game, matching the normal Monopoly LLM prompt path.
                </div>
                <NeoButton
                  type="button"
                  className="w-full justify-center text-[11px]"
                  onClick={() => void handleRun()}
                  disabled={!scenario || running}
                >
                  {running ? 'Running Scenario...' : 'Run Scenario'}
                </NeoButton>
                <div className="grid grid-cols-2 gap-2">
                  <NeoButton
                    type="button"
                    className="justify-center text-[10px]"
                    onClick={() => void handleBatchRun('category')}
                    disabled={batchRunning || !filteredScenarios.length}
                  >
                    {batchRunning ? 'Running...' : 'Run Category'}
                  </NeoButton>
                  <NeoButton
                    type="button"
                    className="justify-center text-[10px]"
                    onClick={() => void handleBatchRun('suite')}
                    disabled={batchRunning}
                  >
                    Run Suite
                  </NeoButton>
                </div>
              </div>
            </NeoCard>

            <NeoCard className="p-3 bg-white">
              <div className="flex items-center justify-between gap-2">
                <div className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Catalog</div>
                <NeoBadge variant="info">{filteredScenarios.length}</NeoBadge>
              </div>
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search scenarios"
                className="mt-2 w-full border-2 border-black bg-neo-bg px-2.5 py-2 text-[12px] shadow-neo-sm outline-none"
              />
                <div className="mt-2 flex flex-wrap gap-2">
                {CATEGORY_ORDER.map((category) => (
                  <button
                    key={category}
                    type="button"
                    onClick={() => setSelectedCategory(category)}
                    className={cn(
                      'min-h-8 px-2.5 py-1 text-[9px] font-black uppercase border-[1.5px] border-black rounded-[2px] transition-all duration-100',
                      selectedCategory === category
                        ? 'bg-black text-white shadow-none'
                        : 'bg-white text-black shadow-neo-sm hover:-translate-y-px hover:shadow-neo'
                    )}
                  >
                    {category === 'ALL' ? 'All' : formatActionLabel(category)}
                  </button>
                ))}
              </div>
              <div className="mt-3 space-y-2 max-h-[28rem] overflow-y-auto brutal-scroll pr-1">
                {filteredScenarios.map((item) => (
                  <button
                    key={item.scenario_id}
                    type="button"
                    onClick={() => {
                      startTransition(() => {
                        setSelectedScenarioId(item.scenario_id)
                        setRun(null)
                      })
                    }}
                    className={cn(
                      'w-full text-left border-2 border-black rounded-[3px] px-3 py-2 transition-all duration-100',
                      item.scenario_id === selectedScenarioId
                        ? 'bg-neo-yellow/35 shadow-neo'
                        : 'bg-white shadow-neo-sm hover:-translate-y-px hover:shadow-neo'
                    )}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[11px] font-black uppercase leading-tight">{item.title}</span>
                      <NeoBadge variant={item.category === 'JAIL' ? 'warning' : item.category.startsWith('TRADE') ? 'info' : 'neutral'}>
                        {formatActionLabel(item.category)}
                      </NeoBadge>
                    </div>
                    <div className="mt-1 text-[10px] leading-snug text-gray-600">{item.description}</div>
                    {item.research_metadata ? (
                      <div className="mt-1 text-[9px] font-mono uppercase text-gray-400">
                        {item.research_metadata.target_capability.replace(/_/g, ' ')}
                      </div>
                    ) : null}
                  </button>
                ))}
                {!filteredScenarios.length && (
                  <div className="rounded-[3px] border border-black/15 bg-neo-bg px-3 py-3 text-[11px] text-gray-500">
                    No scenarios match the current filter.
                  </div>
                )}
              </div>
            </NeoCard>
          </div>
        </aside>

        <main className="min-w-0 overflow-x-auto p-4 xl:max-h-screen xl:overflow-y-auto xl:p-5 brutal-scroll">
          <div className="mx-auto flex max-w-[72rem] flex-col gap-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="min-w-0">
                <div className="text-[11px] font-black uppercase tracking-[0.24em] text-gray-500">
                  Fixture Snapshot
                </div>
                <div className="mt-1 truncate text-2xl font-black uppercase tracking-normal">
                  {scenario?.title ?? 'Micro Scenario'}
                </div>
              </div>
              <div className="flex items-center gap-2">
                {scenarioLoading && <NeoBadge variant="warning">Loading</NeoBadge>}
                {run ? <NeoBadge variant="success">Resolved</NeoBadge> : null}
              </div>
            </div>

            <Board
              spaces={snapshot?.board ?? []}
              players={snapshot?.players ?? []}
              activePlayerId={snapshot?.active_player_id ?? null}
              highlightState={{
                deedHighlight,
                decisionHighlight: highlightIndices,
                eventHighlight: [],
              }}
              className="w-full min-w-[34rem] max-w-[min(52rem,100%,calc(100vh-7rem))] self-center aspect-square lg:min-w-0"
              centerContent={boardCenter}
            />

            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              {playerCards(snapshot, focalPlayerId, modelId, deedHighlight, setDeedHighlight, run)}
            </div>
          </div>
        </main>

        <aside className="min-w-0 border-t-2 border-black bg-white/95 backdrop-blur p-3 xl:h-screen xl:overflow-y-auto xl:border-l-2 xl:border-t-0 xl:p-4 space-y-3 brutal-scroll">
          <NeoCard className="p-3 bg-white">
            <div className="flex items-center justify-between gap-2">
              <div className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Scenario Brief</div>
              {scenario ? <NeoBadge variant="info">{scenario.decision_point.decision_type}</NeoBadge> : null}
            </div>
            <div className="mt-2 text-sm font-black uppercase">{scenario?.title ?? 'Select a scenario'}</div>
            <div className="mt-2 text-[12px] leading-relaxed text-gray-700">
              {scenario?.description ?? loadingMessage}
            </div>
            {scenario ? (
              <>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {scenario.tags.map((tag) => (
                    <NeoBadge key={tag} variant="neutral" className="bg-neo-bg">
                      {tag}
                    </NeoBadge>
                  ))}
                </div>
                <div className="mt-3 rounded-[3px] border border-black/10 bg-neo-bg/60 p-2.5 text-[11px] space-y-1">
                  <div className="flex justify-between gap-2">
                    <span className="text-gray-500 uppercase font-bold">Focal Player</span>
                    <span className="font-mono">{focalPlayerName}</span>
                  </div>
                  <div className="flex justify-between gap-2">
                    <span className="text-gray-500 uppercase font-bold">Turn</span>
                    <span className="font-mono">{scenario.decision_point.turn_index}</span>
                  </div>
                  <div className="flex justify-between gap-2">
                    <span className="text-gray-500 uppercase font-bold">Run Mode</span>
                    <span className="font-mono">Single Decision</span>
                  </div>
                </div>
                {scenario.research_metadata ? (
                  <div className="mt-3 rounded-[3px] border border-black/10 bg-white p-2.5 text-[11px]">
                    <div className="text-[9px] font-black uppercase tracking-[0.18em] text-gray-500">Research Metadata</div>
                    <div className="mt-2 space-y-1">
                      <div className="flex justify-between gap-2">
                        <span className="text-gray-500 uppercase font-bold">Capability</span>
                        <span className="font-mono text-right">{scenario.research_metadata.target_capability}</span>
                      </div>
                      <div className="flex justify-between gap-2">
                        <span className="text-gray-500 uppercase font-bold">Priority</span>
                        <span className="font-mono">{scenario.research_metadata.review_priority}</span>
                      </div>
                      <div className="flex justify-between gap-2">
                        <span className="text-gray-500 uppercase font-bold">Visibility</span>
                        <span className="font-mono text-right">{scenario.research_metadata.visibility}</span>
                      </div>
                    </div>
                  </div>
                ) : null}
              </>
            ) : null}
          </NeoCard>

          <NeoCard className="p-3 bg-white">
            <div className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Legal Actions</div>
            <div className="mt-3 space-y-2">
              {(scenario?.decision_point.legal_actions ?? []).map((action) => {
                const argKeys = legalActionArgKeys(action)
                const isSelected = selectedActionName === action.action
                return (
                  <button
                    key={action.action}
                    type="button"
                    onMouseEnter={() => setSelectedActionName(action.action)}
                    onFocus={() => setSelectedActionName(action.action)}
                    onClick={() => setSelectedActionName(action.action)}
                    className={cn(
                      'w-full rounded-[3px] border-2 border-black px-3 py-2 text-left transition-all duration-100',
                      isSelected ? 'bg-neo-cyan/25 shadow-neo' : 'bg-white shadow-neo-sm hover:-translate-y-px hover:shadow-neo'
                    )}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[11px] font-black uppercase">{formatActionLabel(action.action)}</span>
                      <NeoBadge variant={argKeys.length ? 'info' : 'neutral'}>
                        {argKeys.length ? `${argKeys.length} args` : 'No args'}
                      </NeoBadge>
                    </div>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {argKeys.length ? argKeys.map((key) => (
                        <span key={key} className="text-[10px] font-mono border border-black/15 bg-neo-bg px-1.5 py-px rounded-[2px]">
                          {formatArgLabel(key)}
                        </span>
                      )) : (
                        <span className="text-[10px] text-gray-500">Tool schema takes no structured args.</span>
                      )}
                    </div>
                  </button>
                )
              })}
            </div>
          </NeoCard>

          <NeoCard className="p-3 bg-white">
            <div className="flex items-center justify-between gap-2">
              <div className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Latest Result</div>
              {run?.summary.player.reasoning?.effort ? (
                <NeoBadge variant="warning">{run.summary.player.reasoning.effort}</NeoBadge>
              ) : null}
            </div>
            {run ? (
              <div className="mt-3 space-y-3 text-[11px]">
                <div className="rounded-[3px] border border-black/10 bg-neo-bg/70 p-2.5 space-y-1">
                  <div className="flex justify-between gap-2">
                    <span className="uppercase font-bold text-gray-500">Run Id</span>
                    <span className="font-mono text-[10px]">{run.run_id}</span>
                  </div>
                  <div className="flex justify-between gap-2">
                    <span className="uppercase font-bold text-gray-500">Model</span>
                    <span className="font-mono text-right">{run.summary.player.openrouter_model_id}</span>
                  </div>
                  <div className="flex justify-between gap-2">
                    <span className="uppercase font-bold text-gray-500">Prompt</span>
                    <span className="font-mono text-right">{run.summary.prompt_condition ?? run.result?.prompt_condition ?? 'default'}</span>
                  </div>
                  <div className="flex justify-between gap-2">
                    <span className="uppercase font-bold text-gray-500">Action</span>
                    <span className="font-mono">{run.decision_bundle?.final_action?.action ?? 'n/a'}</span>
                  </div>
                  <div className="flex justify-between gap-2">
                    <span className="uppercase font-bold text-gray-500">Latency</span>
                    <span className="font-mono">{run.summary.result.latency_ms ?? 0} ms</span>
                  </div>
                  <div className="flex justify-between gap-2">
                    <span className="uppercase font-bold text-gray-500">Score</span>
                    <span className="font-mono">
                      {run.result?.score.total ?? run.summary.result.score?.total ?? 'n/a'}{' '}
                      {run.result?.score.label ?? run.summary.result.score?.label ?? ''}
                    </span>
                  </div>
                </div>

                <div>
                  <NeoBadge variant={run.summary.result.retry_used ? 'warning' : 'success'}>
                    {run.summary.result.retry_used ? 'Retry Used' : 'First Pass'}
                  </NeoBadge>
                </div>

                <div>
                  <div className="text-[9px] font-black uppercase tracking-[0.2em] text-gray-500">Public Message</div>
                  <div className="mt-1 rounded-[3px] border border-black/10 bg-white p-2.5 leading-relaxed text-gray-700">
                    {run.decision_bundle?.final_action?.public_message || <span className="text-gray-400 italic">No public message.</span>}
                  </div>
                </div>

                <div>
                  <div className="text-[9px] font-black uppercase tracking-[0.2em] text-gray-500">Private Thought</div>
                  <div className="mt-1 rounded-[3px] border border-black/10 bg-neo-bg/70 p-2.5 leading-relaxed text-gray-700">
                    {run.decision_bundle?.final_action?.private_thought || <span className="text-gray-400 italic">No private thought.</span>}
                  </div>
                </div>

                {attemptErrors.length ? (
                  <div>
                    <div className="text-[9px] font-black uppercase tracking-[0.2em] text-gray-500">Validation Notes</div>
                    <div className="mt-1 space-y-1">
                      {attemptErrors.map((entry, index) => (
                        <div key={`${entry}-${index}`} className="rounded-[3px] border border-neo-pink/40 bg-neo-pink/8 px-2.5 py-2 text-[10px] text-gray-700">
                          {entry}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}

                {(run.result?.score.breakdown ?? run.summary.result.score?.breakdown ?? []).length ? (
                  <div>
                    <div className="text-[9px] font-black uppercase tracking-[0.2em] text-gray-500">Score Breakdown</div>
                    <div className="mt-1 space-y-1">
                      {(run.result?.score.breakdown ?? run.summary.result.score?.breakdown ?? []).map((entry) => (
                        <div key={entry.criterion_id} className="rounded-[3px] border border-black/10 bg-white px-2.5 py-2">
                          <div className="flex justify-between gap-2 font-mono text-[10px]">
                            <span>{entry.criterion_id}</span>
                            <span>{entry.points}/{entry.max_points}</span>
                          </div>
                          <div className="mt-1 text-[10px] leading-snug text-gray-600">{entry.message}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}

                {run.artifact_paths ? (
                  <div>
                    <div className="text-[9px] font-black uppercase tracking-[0.2em] text-gray-500">Artifacts</div>
                    <div className="mt-1 rounded-[3px] border border-black/10 bg-neo-bg/70 p-2.5 space-y-1 font-mono text-[10px] text-gray-700">
                      <div>result: {run.artifact_paths.result}</div>
                      <div>summary: {run.artifact_paths.summary}</div>
                      <div>prompts: {run.artifact_paths.prompts.length}</div>
                    </div>
                  </div>
                ) : null}
              </div>
            ) : (
              <div className="mt-3 rounded-[3px] border border-dashed border-black/20 bg-neo-bg/60 p-3 text-[11px] text-gray-500 leading-relaxed">
                Run the selected scenario to capture the chosen action, retry behavior, and prompt-attempt outcome.
              </div>
            )}
          </NeoCard>

          <NeoCard className="p-3 bg-white">
            <div className="flex items-center justify-between gap-2">
              <div className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Batch Leaderboard</div>
              {batchId ? <NeoBadge variant="info">{batchId}</NeoBadge> : null}
            </div>
            {leaderboard?.rows.length ? (
              <div className="mt-3 space-y-2">
                {leaderboard.rows.map((row) => (
                  <div key={row.model} className="rounded-[3px] border border-black/10 bg-neo-bg/70 p-2.5 text-[11px]">
                    <div className="flex justify-between gap-2 font-mono">
                      <span className="truncate">{row.model}</span>
                      <span>{row.average_score}</span>
                    </div>
                    <div className="mt-1 grid grid-cols-4 gap-1 text-[9px] uppercase text-gray-500">
                      <span>{row.scenario_count} cases</span>
                      <span>retry {row.retry_rate}</span>
                      <span>bad {row.invalid_rate}</span>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {Object.entries(row.category_scores).map(([category, score]) => (
                        <NeoBadge key={category} variant="neutral" className="bg-white">
                          {formatActionLabel(category)} {score}
                        </NeoBadge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="mt-3 rounded-[3px] border border-dashed border-black/20 bg-neo-bg/60 p-3 text-[11px] text-gray-500 leading-relaxed">
                Run a category or suite batch to compare model scores by category.
              </div>
            )}
          </NeoCard>

          {error ? (
            <NeoCard className="p-3 bg-neo-pink/10 border-neo-pink/70">
              <div className="text-[10px] font-black uppercase tracking-[0.2em] text-neo-red">Error</div>
              <div className="mt-2 text-[11px] leading-relaxed text-gray-700">{error}</div>
            </NeoCard>
          ) : null}
        </aside>
      </div>
    </div>
  )
}
