import { startTransition, useEffect, useMemo, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { NeoBadge, NeoButton } from '@/components/ui/NeoPrimitive'
import { cn } from '@/components/ui/cn'
import type { MicroScenario } from '@/net/contracts'
import {
  fetchMicroRun,
  fetchMicroScenarios,
  fetchMicroSuites,
  runMicroBatchStream,
  runMicroScenarioStream,
  type MicroLeaderboard,
  type MicroRunDetail,
  type MicroScenarioSummary,
} from '@/net/micro'

type ScenarioCategory = MicroScenario['category']
type RunState = 'idle' | 'running' | 'cancelled'
type BatchResponseCard = {
  scenarioId: string
  title: string
  status: 'running' | 'complete' | 'error'
  reasoning: string
  output: string
  scoreLabel?: string
  scoreTotal?: number
  actionName?: string
  startedAt: number
}

const CATEGORY_ORDER: ScenarioCategory[] = [
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

const formatLabel = (value: string): string =>
  value
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, (char) => char.toUpperCase())

const PageLink = ({ href, label, active }: { href: string; label: string; active: boolean }) => (
  <a
    href={href}
    className={cn(
      'inline-flex min-h-8 items-center rounded-[2px] border-[1.5px] border-black px-3 py-1 text-[10px] font-black uppercase transition-all duration-100',
      active ? 'bg-black text-white shadow-none' : 'bg-white text-black shadow-neo-sm hover:-translate-y-px hover:shadow-neo'
    )}
  >
    {label}
  </a>
)

const categoryTone = (category: ScenarioCategory): string => {
  const tones: Record<ScenarioCategory, string> = {
    BUY_OR_AUCTION: 'bg-neo-yellow/25',
    AUCTION: 'bg-neo-orange/20',
    TRADE_PROPOSE: 'bg-neo-cyan/25',
    TRADE_RESPONSE: 'bg-neo-blue/10',
    BUILD_OR_MORTGAGE: 'bg-neo-green/20',
    LIQUIDATION: 'bg-neo-pink/10',
    JAIL: 'bg-neo-purple/10',
    POST_TURN_STRATEGY: 'bg-white',
  }
  return tones[category]
}

const ScenarioCheckbox = ({
  checked,
  disabled,
  label,
  onChange,
}: {
  checked: boolean
  disabled?: boolean
  label: string
  onChange: () => void
}) => (
  <button
    type="button"
    disabled={disabled}
    onClick={onChange}
    aria-pressed={checked}
    aria-label={label}
    className={cn(
      'grid size-8 shrink-0 place-items-center rounded-[3px] border-2 border-black bg-white text-[14px] font-black leading-none transition-all duration-100',
      checked && 'bg-black text-white',
      disabled ? 'cursor-not-allowed opacity-45' : 'hover:-translate-y-px hover:shadow-neo-sm'
    )}
  >
    {checked ? '✓' : ''}
  </button>
)

const FieldLabel = ({ children }: { children: ReactNode }) => (
  <span className="text-[9px] font-black uppercase tracking-[0.18em] text-gray-500">{children}</span>
)

const FieldShell = ({ children, className }: { children: ReactNode; className?: string }) => (
  <label className={cn('block min-w-0', className)}>{children}</label>
)

const inputClass =
  'mt-1 h-10 w-full min-w-0 rounded-[3px] border-2 border-black bg-white px-3 text-[12px] font-semibold shadow-neo-sm outline-none transition-shadow focus:shadow-neo'

const CollapsibleOutput = ({
  title,
  value,
  expanded,
  onToggle,
}: {
  title: string
  value: string
  expanded: boolean
  onToggle: () => void
}) => (
  <div className="rounded-[8px] border border-black/15 bg-white">
    <button
      type="button"
      onClick={onToggle}
      className="flex w-full items-center justify-between gap-3 border-b border-black/10 px-3 py-2 text-left"
    >
      <span className="text-[10px] font-black uppercase tracking-[0.18em] text-gray-500">{title}</span>
      <span className="text-base font-black leading-none">{expanded ? '↑' : '↓'}</span>
    </button>
    {expanded ? (
      <pre className="max-h-56 overflow-y-auto whitespace-pre-wrap break-words p-3 font-mono text-[11px] leading-relaxed text-gray-700 brutal-scroll">
        {value || 'No text captured yet.'}
      </pre>
    ) : null}
  </div>
)

export const MicroDashboardPage = () => {
  const [scenarios, setScenarios] = useState<MicroScenarioSummary[]>([])
  const [suiteId, setSuiteId] = useState('micro-v1')
  const [suiteIds, setSuiteIds] = useState<string[]>(['micro-v1'])
  const [expandedCategories, setExpandedCategories] = useState<Set<ScenarioCategory>>(new Set(CATEGORY_ORDER.slice(0, 3)))
  const [selectedScenarioIds, setSelectedScenarioIds] = useState<Set<string>>(new Set())
  const [modelId, setModelId] = useState('openai/gpt-oss-120b')
  const [displayName, setDisplayName] = useState('Micro Agent')
  const [reasoningEffort, setReasoningEffort] = useState<(typeof reasoningOptions)[number]>('medium')
  const [loading, setLoading] = useState(true)
  const [configExpanded, setConfigExpanded] = useState(true)
  const [reasoningExpanded, setReasoningExpanded] = useState(true)
  const [outputExpanded, setOutputExpanded] = useState(true)
  const [streamingReasoning, setStreamingReasoning] = useState('')
  const [streamingOutput, setStreamingOutput] = useState('')
  const [batchReasoning, setBatchReasoning] = useState<Record<string, string>>({})
  const [batchOutput, setBatchOutput] = useState<Record<string, string>>({})
  const [batchResponses, setBatchResponses] = useState<Record<string, BatchResponseCard>>({})
  const [expandedScenarioResponses, setExpandedScenarioResponses] = useState<Record<string, boolean>>({})
  const [batchCompleted, setBatchCompleted] = useState(0)
  const [batchTotal, setBatchTotal] = useState(0)
  const [streamStatus, setStreamStatus] = useState<string | null>(null)
  const [runState, setRunState] = useState<RunState>('idle')
  const [error, setError] = useState<string | null>(null)
  const [leaderboard, setLeaderboard] = useState<MicroLeaderboard | null>(null)
  const [batchId, setBatchId] = useState<string | null>(null)
  const [latestRun, setLatestRun] = useState<MicroRunDetail | null>(null)
  const runTokenRef = useRef(0)
  const streamAbortRef = useRef<AbortController | null>(null)

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      try {
        setLoading(true)
        const [scenarioItems, suites] = await Promise.all([fetchMicroScenarios(), fetchMicroSuites()])
        if (cancelled) return
        setScenarios(scenarioItems)
        setSuiteIds(suites.map((suite) => suite.suite_id))
        startTransition(() => {
          setSuiteId((current) => current || suites[0]?.suite_id || 'micro-v1')
        })
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load micro dashboard data.')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }
    void load()
    return () => {
      cancelled = true
    }
  }, [])

  const scenariosByCategory = useMemo(() => {
    const grouped = new Map<ScenarioCategory, MicroScenarioSummary[]>()
    for (const category of CATEGORY_ORDER) {
      grouped.set(category, [])
    }
    for (const scenario of scenarios) {
      grouped.get(scenario.category)?.push(scenario)
    }
    return grouped
  }, [scenarios])

  const selectedScenarios = useMemo(
    () => scenarios.filter((scenario) => selectedScenarioIds.has(scenario.scenario_id)),
    [scenarios, selectedScenarioIds]
  )

  const scenarioTitleById = useMemo(() => {
    const titles = new Map<string, string>()
    for (const scenario of scenarios) {
      titles.set(scenario.scenario_id, scenario.title)
    }
    return titles
  }, [scenarios])

  const selectedCategoryCount = useMemo(() => {
    let count = 0
    for (const category of CATEGORY_ORDER) {
      const categoryScenarios = scenariosByCategory.get(category) ?? []
      if (categoryScenarios.length && categoryScenarios.every((scenario) => selectedScenarioIds.has(scenario.scenario_id))) {
        count += 1
      }
    }
    return count
  }, [scenariosByCategory, selectedScenarioIds])

  const targetLabel =
    loading
      ? 'Loading suite'
      : selectedScenarios.length === 0
      ? `Full suite (${scenarios.length})`
      : selectedScenarios.length === 1
        ? selectedScenarios[0]?.title ?? 'Selected scenario'
        : `${selectedScenarios.length} selected scenarios`

  const selectedCategoryLabels = CATEGORY_ORDER.filter((category) =>
    (scenariosByCategory.get(category) ?? []).some((scenario) => selectedScenarioIds.has(scenario.scenario_id))
  )

  const isRunning = runState === 'running'

  const setCategorySelected = (category: ScenarioCategory, checked: boolean) => {
    const categoryScenarios = scenariosByCategory.get(category) ?? []
    setSelectedScenarioIds((current) => {
      const next = new Set(current)
      for (const scenario of categoryScenarios) {
        if (checked) {
          next.add(scenario.scenario_id)
        } else {
          next.delete(scenario.scenario_id)
        }
      }
      return next
    })
  }

  const toggleCategoryOpen = (category: ScenarioCategory) => {
    setExpandedCategories((current) => {
      const next = new Set(current)
      if (next.has(category)) {
        next.delete(category)
      } else {
        next.add(category)
      }
      return next
    })
  }

  const toggleScenario = (scenarioId: string) => {
    setSelectedScenarioIds((current) => {
      const next = new Set(current)
      if (next.has(scenarioId)) {
        next.delete(scenarioId)
      } else {
        next.add(scenarioId)
      }
      return next
    })
  }

  const handleRun = async () => {
    const token = runTokenRef.current + 1
    runTokenRef.current = token
    try {
      setRunState('running')
      setError(null)
      setLatestRun(null)
      setLeaderboard(null)
      setBatchId(null)
      setStreamingReasoning('')
      setStreamingOutput('')
      setBatchReasoning({})
      setBatchOutput({})
      setBatchResponses({})
      setExpandedScenarioResponses({})
      setBatchCompleted(0)
      setBatchTotal(0)
      setStreamStatus(null)
      const modelValue = modelId.trim()
      if (!modelValue) {
        throw new Error('Model ID is required.')
      }
      streamAbortRef.current?.abort()
      streamAbortRef.current = null

      if (selectedScenarios.length === 1) {
        const payload = {
          scenario_id: selectedScenarios[0].scenario_id,
          openrouter_model_id: modelValue,
          name: displayName,
          prompt_condition: MICRO_PROMPT_CONDITION,
          reasoning: { effort: reasoningEffort },
        }
        const controller = new AbortController()
        streamAbortRef.current = controller
        const runResult = await runMicroScenarioStream(payload, {
          signal: controller.signal,
          onStatus: (event) => setStreamStatus(event.state),
          onDelta: (event) => {
            const text = event.text ?? ''
            if (!text) return
            if (event.type === 'reasoning_delta') {
              setStreamingReasoning((current) => current + text)
            } else if (event.type === 'content_delta') {
              setStreamingOutput((current) => current + text)
            } else if (event.type === 'tool_name_delta') {
              setStreamingOutput((current) => current + (current ? '\n' : '') + `tool: ${text}`)
            } else if (event.type === 'tool_arguments_delta' || event.type === 'raw_delta') {
              setStreamingOutput((current) => current + text)
            }
          },
        })
        streamAbortRef.current = null
        const { run_id } = runResult
        if (runTokenRef.current !== token) return
        const detail = await fetchMicroRun(run_id)
        if (runTokenRef.current !== token) return
        setLatestRun(detail)
        return
      }

      const batchPayload = {
        suite_id: suiteId,
        openrouter_model_ids: [modelValue],
        prompt_condition: MICRO_PROMPT_CONDITION,
        reasoning: { effort: reasoningEffort },
        scenario_ids: selectedScenarios.length ? selectedScenarios.map((scenario) => scenario.scenario_id) : null,
      }
      const firstWave = (selectedScenarios.length ? selectedScenarios : scenarios).slice(0, 20)
      setBatchResponses(Object.fromEntries(firstWave.map((scenario, index) => [
        scenario.scenario_id,
        {
          scenarioId: scenario.scenario_id,
          title: scenario.title,
          status: 'running' as const,
          reasoning: '',
          output: `Sent in wave 1 slot ${index + 1}. Waiting for streamed response...`,
          startedAt: Date.now() + index,
        },
      ])))
      const controller = new AbortController()
      streamAbortRef.current = controller
      const batch = await runMicroBatchStream(batchPayload, {
          signal: controller.signal,
          onStatus: (event) => {
            const wave = event.wave_index ? `wave ${event.wave_index}` : event.state
            const completed = typeof event.completed_count === 'number' && typeof event.task_count === 'number'
              ? ` ${event.completed_count}/${event.task_count}`
              : ''
            setStreamStatus(`${wave}${completed}`)
            if (typeof event.task_count === 'number') {
              setBatchTotal(event.task_count)
            }
            const waveScenarioIds = event.wave_scenario_ids ?? []
            if (event.state === 'wave_started' && waveScenarioIds.length) {
              setBatchResponses((current) => {
                const next = { ...current }
                for (const [index, scenarioId] of waveScenarioIds.entries()) {
                  const previous = next[scenarioId]
                  next[scenarioId] = {
                    scenarioId,
                    title: previous?.title ?? scenarioTitleById.get(scenarioId) ?? scenarioId,
                    status: previous?.status ?? 'running',
                    reasoning: previous?.reasoning ?? '',
                    output: previous?.output ?? `Sent in wave ${event.wave_index ?? '?'} slot ${index + 1}. Waiting for streamed response...`,
                    scoreLabel: previous?.scoreLabel,
                    scoreTotal: previous?.scoreTotal,
                    actionName: previous?.actionName,
                    startedAt: previous?.startedAt ?? Date.now() + index,
                  }
                }
                return next
              })
            }
          },
          onDelta: (event) => {
            const text = event.text ?? ''
            if (!text) return
            const scenarioId = event.scenario_id
            if (event.type === 'reasoning_delta') {
              setBatchReasoning((current) => ({ ...current, [scenarioId]: `${current[scenarioId] ?? ''}${text}` }))
              setBatchResponses((current) => ({
                ...current,
                [scenarioId]: {
                  ...current[scenarioId],
                  scenarioId,
                  title: current[scenarioId]?.title ?? scenarioTitleById.get(scenarioId) ?? scenarioId,
                  status: current[scenarioId]?.status ?? 'running',
                  reasoning: `${current[scenarioId]?.reasoning ?? ''}${text}`,
                  output: current[scenarioId]?.output ?? '',
                  startedAt: current[scenarioId]?.startedAt ?? Date.now(),
                },
              }))
            } else if (event.type === 'content_delta') {
              setBatchOutput((current) => ({ ...current, [scenarioId]: `${current[scenarioId] ?? ''}${text}` }))
              setBatchResponses((current) => ({
                ...current,
                [scenarioId]: {
                  ...current[scenarioId],
                  scenarioId,
                  title: current[scenarioId]?.title ?? scenarioTitleById.get(scenarioId) ?? scenarioId,
                  status: current[scenarioId]?.status ?? 'running',
                  reasoning: current[scenarioId]?.reasoning ?? '',
                  output: `${current[scenarioId]?.output ?? ''}${text}`,
                  startedAt: current[scenarioId]?.startedAt ?? Date.now(),
                },
              }))
            } else if (event.type === 'tool_name_delta') {
              setBatchOutput((current) => ({
                ...current,
                [scenarioId]: `${current[scenarioId] ? `${current[scenarioId]}\n` : ''}tool: ${text}`,
              }))
              setBatchResponses((current) => {
                const previous = current[scenarioId]
                return {
                  ...current,
                  [scenarioId]: {
                    ...previous,
                    scenarioId,
                    title: previous?.title ?? scenarioTitleById.get(scenarioId) ?? scenarioId,
                    status: previous?.status ?? 'running',
                    reasoning: previous?.reasoning ?? '',
                    output: `${previous?.output ? `${previous.output}\n` : ''}tool: ${text}`,
                    startedAt: previous?.startedAt ?? Date.now(),
                  },
                }
              })
            } else if (event.type === 'tool_arguments_delta' || event.type === 'raw_delta') {
              setBatchOutput((current) => ({ ...current, [scenarioId]: `${current[scenarioId] ?? ''}${text}` }))
              setBatchResponses((current) => ({
                ...current,
                [scenarioId]: {
                  ...current[scenarioId],
                  scenarioId,
                  title: current[scenarioId]?.title ?? scenarioTitleById.get(scenarioId) ?? scenarioId,
                  status: current[scenarioId]?.status ?? 'running',
                  reasoning: current[scenarioId]?.reasoning ?? '',
                  output: `${current[scenarioId]?.output ?? ''}${text}`,
                  startedAt: current[scenarioId]?.startedAt ?? Date.now(),
                },
              }))
            }
          },
          onScenarioStarted: (event) => {
            setBatchOutput((current) => ({ ...current, [event.scenario_id]: current[event.scenario_id] ?? 'Started...' }))
            setBatchResponses((current) => {
              const previous = current[event.scenario_id]
              return {
                ...current,
                [event.scenario_id]: {
                  ...previous,
                  scenarioId: event.scenario_id,
                  title: previous?.title ?? scenarioTitleById.get(event.scenario_id) ?? event.scenario_id,
                  status: 'running',
                  reasoning: previous?.reasoning ?? '',
                  output: previous?.output ?? 'Started. Waiting for streamed response...',
                  startedAt: previous?.startedAt ?? Date.now(),
                },
              }
            })
          },
          onScenarioResult: (event) => {
            setBatchCompleted((current) => current + 1)
            setBatchOutput((current) => ({
              ...current,
              [event.scenario_id]: JSON.stringify(event.action, null, 2),
            }))
            setBatchReasoning((current) => ({
              ...current,
              [event.scenario_id]: current[event.scenario_id] || event.action.private_thought || '',
            }))
            setBatchResponses((current) => ({
              ...current,
              [event.scenario_id]: {
                ...current[event.scenario_id],
                scenarioId: event.scenario_id,
                title: current[event.scenario_id]?.title ?? scenarioTitleById.get(event.scenario_id) ?? event.scenario_id,
                status: 'complete',
                reasoning: current[event.scenario_id]?.reasoning || event.action.private_thought || '',
                output: JSON.stringify(event.action, null, 2),
                scoreLabel: event.score.label,
                scoreTotal: event.score.total,
                actionName: event.action.action,
                startedAt: current[event.scenario_id]?.startedAt ?? Date.now(),
              },
            }))
          },
          onScenarioError: (event) => {
            if (!event.scenario_id) return
            setBatchCompleted((current) => current + 1)
            setBatchResponses((current) => {
              const previous = current[event.scenario_id!]
              return {
                ...current,
                [event.scenario_id!]: {
                  ...previous,
                  scenarioId: event.scenario_id!,
                  title: previous?.title ?? scenarioTitleById.get(event.scenario_id!) ?? event.scenario_id!,
                  status: 'error',
                  reasoning: previous?.reasoning ?? '',
                  output: event.message ?? 'Scenario failed.',
                  startedAt: previous?.startedAt ?? Date.now(),
                },
              }
            })
          },
        })
      streamAbortRef.current = null
      if (runTokenRef.current !== token) return
      setBatchId(batch.batch_id)
      setLeaderboard(batch.leaderboard)
    } catch (err) {
      if (runTokenRef.current === token) {
        if (err instanceof DOMException && err.name === 'AbortError') {
          setRunState('cancelled')
        } else {
          setError(err instanceof Error ? err.message : 'Micro run failed.')
        }
      }
    } finally {
      if (runTokenRef.current === token) {
        setRunState('idle')
      }
    }
  }

  const handleCancel = () => {
    runTokenRef.current += 1
    streamAbortRef.current?.abort()
    streamAbortRef.current = null
    setRunState('cancelled')
  }

  const handleClear = () => {
    setSelectedScenarioIds(new Set())
    setLatestRun(null)
    setLeaderboard(null)
    setBatchId(null)
    setError(null)
    setStreamingReasoning('')
    setStreamingOutput('')
    setBatchReasoning({})
    setBatchOutput({})
    setBatchResponses({})
    setExpandedScenarioResponses({})
    setBatchCompleted(0)
    setBatchTotal(0)
    setStreamStatus(null)
    setRunState('idle')
  }

  const formatBatchText = (items: Record<string, string>) =>
    Object.entries(items)
      .map(([scenarioId, text]) => `### ${scenarioId}\n${text || 'No text captured.'}`)
      .join('\n\n')

  const finalReasoning = streamingReasoning || formatBatchText(batchReasoning) || latestRun?.decision_bundle?.final_action?.private_thought || ''
  const finalOutput = streamingOutput || formatBatchText(batchOutput) || (
    latestRun?.decision_bundle?.final_action
      ? JSON.stringify(latestRun.decision_bundle.final_action, null, 2)
      : ''
  )

  const toggleScenarioResponse = (scenarioId: string) => {
    setExpandedScenarioResponses((current) => ({
      ...current,
      [scenarioId]: !current[scenarioId],
    }))
  }

  return (
    <div className="h-screen overflow-y-auto bg-[#f6f4ef] text-black brutal-scroll">
      <div
        className="fixed inset-0 pointer-events-none opacity-70"
        style={{ backgroundImage: 'url(/background.png)', backgroundSize: 'cover', backgroundPosition: 'center' }}
      />
      <div className="relative mx-auto flex min-h-screen w-full max-w-[96rem] flex-col px-3 py-3 sm:px-5 lg:px-7">
        <header className="flex flex-col gap-3 rounded-[8px] border-2 border-black bg-white/95 px-4 py-3 shadow-neo md:flex-row md:items-center md:justify-between">
          <div>
            <div className="text-xl font-black uppercase tracking-normal">
              Monopoly<span className="ml-0.5 text-neo-pink">Bench</span>
            </div>
            <div className="mt-1 text-[10px] font-black uppercase tracking-[0.24em] text-gray-500">
              Micro Decision Console
            </div>
          </div>
          <nav className="flex flex-wrap items-center gap-2">
            <PageLink href="/" label="Live" active={false} />
            <PageLink href="/micro" label="Micro" active />
            <PageLink href="/micro/detail" label="Detail" active={false} />
          </nav>
        </header>

        <main className="flex flex-1 flex-col gap-5 py-5">
          <section className="mx-auto w-full max-w-[70rem] rounded-[8px] border-2 border-black bg-white/96 p-4 shadow-neo-lg sm:p-5 lg:p-6">
            <div className="flex flex-col gap-5 xl:flex-row xl:items-start">
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <div className="text-[10px] font-black uppercase tracking-[0.25em] text-gray-500">Run Config</div>
                    <h1 className="mt-1 text-2xl font-black uppercase leading-tight tracking-normal sm:text-3xl">
                      {targetLabel}
                    </h1>
                  </div>
                  <div className="flex flex-wrap items-center gap-2">
                    <NeoBadge variant="warning">{modelId}</NeoBadge>
                    <NeoBadge variant="info">live_game</NeoBadge>
                    <NeoBadge variant="neutral">{reasoningEffort}</NeoBadge>
                    {batchTotal ? <NeoBadge variant="info">{batchCompleted}/{batchTotal}</NeoBadge> : null}
                    {streamStatus ? <NeoBadge variant="warning">{streamStatus}</NeoBadge> : null}
                    <button
                      type="button"
                      onClick={() => setConfigExpanded((current) => !current)}
                      className="grid size-9 place-items-center rounded-[3px] border-2 border-black bg-white text-xl font-black leading-none shadow-neo-sm transition-all duration-100 hover:-translate-y-px hover:shadow-neo"
                      aria-expanded={configExpanded}
                      aria-label="Toggle run configuration"
                    >
                      {configExpanded ? '↑' : '↓'}
                    </button>
                  </div>
                </div>

                {configExpanded ? (
                  <>
                    <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                      <FieldShell>
                        <FieldLabel>Suite</FieldLabel>
                        <select value={suiteId} onChange={(event) => setSuiteId(event.target.value)} className={inputClass}>
                          {suiteIds.map((item) => (
                            <option key={item} value={item}>
                              {item}
                            </option>
                          ))}
                        </select>
                      </FieldShell>

                      <FieldShell>
                        <FieldLabel>Reasoning</FieldLabel>
                        <select
                          value={reasoningEffort}
                          onChange={(event) => setReasoningEffort(event.target.value as (typeof reasoningOptions)[number])}
                          className={inputClass}
                        >
                          {reasoningOptions.map((item) => (
                            <option key={item} value={item}>
                              {item}
                            </option>
                          ))}
                        </select>
                      </FieldShell>
                    </div>

                    <div className="mt-3 grid gap-3 lg:grid-cols-[minmax(0,1.25fr)_minmax(0,1fr)]">
                      <FieldShell>
                        <FieldLabel>Model ID</FieldLabel>
                        <input
                          value={modelId}
                          onChange={(event) => setModelId(event.target.value)}
                          className={cn(inputClass, 'font-mono')}
                        />
                      </FieldShell>
                      <FieldShell>
                        <FieldLabel>Display Name</FieldLabel>
                        <input value={displayName} onChange={(event) => setDisplayName(event.target.value)} className={inputClass} />
                      </FieldShell>
                    </div>

                    <div className="mt-3 rounded-[6px] border border-black/10 bg-neo-bg/70 px-3 py-2 text-[11px] font-semibold text-gray-600">
                      Prompt mode is fixed to live_game, matching the normal Monopoly LLM prompt path.
                    </div>
                  </>
                ) : null}
              </div>

              <aside className="grid gap-3 xl:w-[18rem]">
                <div className="rounded-[8px] border-2 border-black bg-neo-bg p-3">
                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div>
                      <div className="text-2xl font-black tabular-nums">{loading ? '...' : scenarios.length}</div>
                      <div className="text-[9px] font-black uppercase tracking-[0.14em] text-gray-500">Suite</div>
                    </div>
                    <div>
                      <div className="text-2xl font-black tabular-nums">{loading ? '...' : selectedScenarios.length || scenarios.length}</div>
                      <div className="text-[9px] font-black uppercase tracking-[0.14em] text-gray-500">Target</div>
                    </div>
                    <div>
                      <div className="text-2xl font-black tabular-nums">{selectedCategoryCount || CATEGORY_ORDER.length}</div>
                      <div className="text-[9px] font-black uppercase tracking-[0.14em] text-gray-500">Groups</div>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <NeoButton type="button" className="justify-center text-[11px]" disabled={isRunning || loading || !scenarios.length} onClick={() => void handleRun()}>
                    {isRunning ? 'Running' : 'Start'}
                  </NeoButton>
                  <NeoButton type="button" variant="ghost" className="justify-center text-[11px]" disabled={!isRunning} onClick={handleCancel}>
                    Cancel
                  </NeoButton>
                  <NeoButton type="button" variant="ghost" className="justify-center text-[11px]" disabled title="Micro jobs currently run as synchronous API requests.">
                    Pause
                  </NeoButton>
                  <NeoButton type="button" variant="secondary" className="justify-center text-[11px]" disabled={isRunning} onClick={handleClear}>
                    Clear
                  </NeoButton>
                </div>

                <a
                  href="/micro/detail"
                  className="rounded-[3px] border-2 border-black bg-white px-3 py-2 text-center text-[11px] font-black uppercase shadow-neo-sm transition-all duration-100 hover:-translate-y-px hover:shadow-neo"
                >
                  Open Detail Inspector
                </a>
              </aside>
            </div>
          </section>

          <section className="grid gap-4 xl:grid-cols-3">
            {CATEGORY_ORDER.map((category) => {
              const categoryScenarios = scenariosByCategory.get(category) ?? []
              const selectedCount = categoryScenarios.filter((scenario) => selectedScenarioIds.has(scenario.scenario_id)).length
              const allSelected = categoryScenarios.length > 0 && selectedCount === categoryScenarios.length
              const isExpanded = expandedCategories.has(category)
              return (
                <article key={category} className="min-h-[18rem] rounded-[8px] border-2 border-black bg-white/96 p-3 shadow-neo">
                  <div className={cn('rounded-[8px] border-2 border-black p-3', categoryTone(category))}>
                    <div className="flex min-w-0 items-center gap-3">
                      <ScenarioCheckbox
                        checked={allSelected}
                        disabled={!categoryScenarios.length}
                        label={`Toggle ${formatLabel(category)}`}
                        onChange={() => setCategorySelected(category, !allSelected)}
                      />
                      <button
                        type="button"
                        onClick={() => toggleCategoryOpen(category)}
                        className="flex min-h-8 min-w-0 flex-1 items-center justify-between gap-2 text-left"
                      >
                        <span className="truncate text-sm font-black uppercase tracking-normal">{formatLabel(category)}</span>
                        <span className="text-xl font-black leading-none">{isExpanded ? '↑' : '↓'}</span>
                      </button>
                    </div>
                    <div className="mt-2 flex items-center justify-between gap-3 text-[10px] font-black uppercase tracking-[0.16em] text-gray-500">
                      <span>{loading ? 'Loading' : `${categoryScenarios.length} scenarios`}</span>
                      <span>{selectedCount} selected</span>
                    </div>
                  </div>

                  {isExpanded ? (
                    <div className="mt-3 max-h-[18rem] space-y-2 overflow-y-auto pr-1 brutal-scroll">
                      {categoryScenarios.map((scenario) => {
                        const checked = selectedScenarioIds.has(scenario.scenario_id)
                        const response = batchResponses[scenario.scenario_id]
                        const expandedResponse = Boolean(expandedScenarioResponses[scenario.scenario_id])
                        const responseStatus = response?.status ?? (checked && isRunning ? 'running' : null)
                        return (
                          <div
                            key={scenario.scenario_id}
                            className={cn(
                              'w-full rounded-[6px] border border-black/15 px-3 py-2 text-left transition-all duration-100',
                              checked ? 'bg-black text-white shadow-neo-sm' : 'bg-white hover:-translate-y-px hover:shadow-neo-sm'
                            )}
                          >
                            <div className="flex items-start gap-2">
                              <button
                                type="button"
                                onClick={() => toggleScenario(scenario.scenario_id)}
                                className={cn(
                                  'mt-0.5 grid size-8 shrink-0 place-items-center rounded-[2px] border-[1.5px] text-[12px] font-black',
                                  checked ? 'border-white bg-white text-black' : 'border-black bg-white text-black'
                                )}
                                aria-label={`Toggle ${scenario.title}`}
                              >
                                {checked ? '✓' : ''}
                              </button>
                              <button
                                type="button"
                                onClick={() => toggleScenario(scenario.scenario_id)}
                                className="min-w-0 flex-1 text-left"
                              >
                                <span className="block text-[11px] font-black uppercase leading-tight">{scenario.title}</span>
                                <span className={cn('mt-1 block text-[10px] leading-snug', checked ? 'text-white/70' : 'text-gray-600')}>
                                  {scenario.description}
                                </span>
                                <span className={cn('mt-1 block font-mono text-[9px]', checked ? 'text-white/55' : 'text-gray-400')}>
                                  {scenario.difficulty} / {scenario.scoring_mode}
                                </span>
                                {scenario.research_metadata ? (
                                  <span className={cn('mt-1 block font-mono text-[9px]', checked ? 'text-white/55' : 'text-gray-400')}>
                                    {scenario.research_metadata.target_capability.replace(/_/g, ' ')}
                                  </span>
                                ) : null}
                              </button>
                            </div>
                            {checked ? (
                              <div className="mt-3 border-t border-white/15 pt-2">
                                <div className="flex flex-wrap items-center gap-2">
                                  <button
                                    type="button"
                                    onClick={() => toggleScenarioResponse(scenario.scenario_id)}
                                    className={cn(
                                      'rounded-[3px] border px-2 py-1 text-[9px] font-black uppercase transition-all duration-100',
                                      expandedResponse
                                        ? 'border-white bg-white text-black'
                                        : 'border-white/35 bg-black text-white hover:border-white'
                                    )}
                                  >
                                    {expandedResponse ? 'Hide Response' : 'Show Response'}
                                  </button>
                                  {responseStatus ? (
                                    <NeoBadge variant={responseStatus === 'complete' ? 'success' : 'warning'}>
                                      {responseStatus}
                                    </NeoBadge>
                                  ) : null}
                                  {response?.scoreLabel ? <NeoBadge variant="success">{response.scoreLabel}</NeoBadge> : null}
                                </div>
                                {expandedResponse ? (
                                  <div className="mt-2 grid gap-2">
                                    <div className="rounded-[6px] border border-white/15 bg-white p-2">
                                      <div className="text-[9px] font-black uppercase tracking-[0.16em] text-gray-500">Reasoning</div>
                                      <pre className="mt-1 max-h-40 overflow-y-auto whitespace-pre-wrap break-words font-mono text-[10px] leading-relaxed text-gray-800 brutal-scroll">
                                        {response?.reasoning || 'Waiting for reasoning...'}
                                      </pre>
                                    </div>
                                    <div className="rounded-[6px] border border-white/15 bg-white p-2">
                                      <div className="text-[9px] font-black uppercase tracking-[0.16em] text-gray-500">Output</div>
                                      <pre className="mt-1 max-h-40 overflow-y-auto whitespace-pre-wrap break-words font-mono text-[10px] leading-relaxed text-gray-800 brutal-scroll">
                                        {response?.output || 'Waiting for output...'}
                                      </pre>
                                    </div>
                                  </div>
                                ) : null}
                              </div>
                            ) : null}
                          </div>
                        )
                      })}
                      {loading ? (
                        <div className="rounded-[8px] border border-dashed border-black/20 bg-neo-bg p-3 text-[11px] text-gray-500">
                          Loading scenarios...
                        </div>
                      ) : !categoryScenarios.length ? (
                        <div className="rounded-[8px] border border-dashed border-black/20 bg-neo-bg p-3 text-[11px] text-gray-500">
                          No scenarios loaded for this category.
                        </div>
                      ) : null}
                    </div>
                  ) : (
                    <div className="mt-3 flex min-h-[12rem] flex-col justify-between rounded-[8px] border border-dashed border-black/20 bg-neo-bg/70 p-3">
                      <div className="text-[12px] font-semibold text-gray-600">
                        {loading ? 'Loading scenarios...' : selectedCount ? `${selectedCount} selected in this category.` : 'Collapsed'}
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {categoryScenarios.slice(0, 5).map((scenario) => (
                          <NeoBadge key={scenario.scenario_id} variant="neutral" className="bg-white">
                            {scenario.difficulty}
                          </NeoBadge>
                        ))}
                      </div>
                    </div>
                  )}
                </article>
              )
            })}
          </section>

          <section className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_22rem]">
            <div className="rounded-[8px] border-2 border-black bg-white/96 p-4 shadow-neo">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <div className="text-[10px] font-black uppercase tracking-[0.22em] text-gray-500">Latest Output</div>
                  <div className="mt-1 text-xl font-black uppercase">
                    {latestRun ? 'Single Run' : leaderboard ? 'Batch Leaderboard' : isRunning ? 'Streaming Run' : runState === 'cancelled' ? 'Cancelled Locally' : 'Ready'}
                  </div>
                </div>
                {batchId ? <NeoBadge variant="info">{batchId}</NeoBadge> : latestRun ? <NeoBadge variant="success">{latestRun.result?.score.label}</NeoBadge> : null}
              </div>

              {latestRun || isRunning || streamingReasoning || streamingOutput ? (
                <div className="mt-4 grid gap-3 md:grid-cols-3">
                  <div className="rounded-[8px] border border-black/10 bg-neo-bg/70 p-3">
                    <div className="text-[9px] font-black uppercase tracking-[0.18em] text-gray-500">Action</div>
                    <div className="mt-1 font-mono text-sm">{latestRun?.decision_bundle?.final_action?.action ?? 'n/a'}</div>
                  </div>
                  <div className="rounded-[8px] border border-black/10 bg-white p-3">
                    <div className="text-[9px] font-black uppercase tracking-[0.18em] text-gray-500">Score</div>
                    <div className="mt-1 text-2xl font-black">{latestRun?.result?.score.total ?? latestRun?.summary.result.score?.total ?? 'n/a'}</div>
                  </div>
                  <div className="rounded-[8px] border border-black/10 bg-white p-3">
                    <div className="text-[9px] font-black uppercase tracking-[0.18em] text-gray-500">Latency</div>
                    <div className="mt-1 text-2xl font-black">{latestRun?.summary.result.latency_ms ?? 0} ms</div>
                  </div>
                  <div className="rounded-[8px] border border-black/10 bg-white p-3 text-[11px] leading-relaxed text-gray-600 md:col-span-3">
                    {latestRun?.decision_bundle?.final_action?.public_message || 'No public message.'}
                  </div>
                  <div className="grid gap-3 md:col-span-3">
                    <CollapsibleOutput
                      title="Reasoning"
                      value={finalReasoning}
                      expanded={reasoningExpanded}
                      onToggle={() => setReasoningExpanded((current) => !current)}
                    />
                    <CollapsibleOutput
                      title="Output"
                      value={finalOutput}
                      expanded={outputExpanded}
                      onToggle={() => setOutputExpanded((current) => !current)}
                    />
                  </div>
                </div>
              ) : leaderboard?.rows.length ? (
                <div className="mt-4 overflow-x-auto brutal-scroll">
                  <table className="w-full min-w-[42rem] border-collapse text-left text-[11px]">
                    <thead>
                      <tr className="border-b-2 border-black">
                        {['Model', 'Cases', 'Avg', 'Retry', 'Invalid', 'Latency'].map((item) => (
                          <th key={item} className="px-2 py-2 font-black uppercase text-gray-500">
                            {item}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {leaderboard.rows.map((row) => (
                        <tr key={row.model} className="border-b border-black/10">
                          <td className="px-2 py-2 font-mono">{row.model}</td>
                          <td className="px-2 py-2">{row.scenario_count}</td>
                          <td className="px-2 py-2 font-black">{row.average_score}</td>
                          <td className="px-2 py-2">{row.retry_rate}</td>
                          <td className="px-2 py-2">{row.invalid_rate}</td>
                          <td className="px-2 py-2">{row.average_latency_ms} ms</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="mt-4 rounded-[8px] border border-dashed border-black/20 bg-neo-bg/70 p-4 text-sm text-gray-600">
                  Select categories or individual scenarios, then start a run. With no selection, Start targets the full suite.
                </div>
              )}
            </div>

            <aside className="rounded-[8px] border-2 border-black bg-white/96 p-4 shadow-neo">
              <div className="text-[10px] font-black uppercase tracking-[0.22em] text-gray-500">Selected Categories</div>
              <div className="mt-3 flex flex-wrap gap-2">
                {selectedCategoryLabels.length ? (
                  selectedCategoryLabels.map((category) => (
                    <NeoBadge key={category} variant="info">
                      {formatLabel(category)}
                    </NeoBadge>
                  ))
                ) : (
                  <NeoBadge variant="neutral">Full Suite</NeoBadge>
                )}
              </div>
              {error ? (
                <div className="mt-4 rounded-[8px] border border-neo-pink/50 bg-neo-pink/10 p-3 text-[11px] leading-relaxed text-gray-700">
                  <div className="font-black uppercase text-neo-red">Error</div>
                  <div className="mt-1">{error}</div>
                </div>
              ) : null}
            </aside>
          </section>
        </main>
      </div>
    </div>
  )
}
