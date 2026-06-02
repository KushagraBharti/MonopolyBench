import { getApiBaseUrl } from '@/net/ws'
import type { LegalAction, MicroResearchMetadata, MicroResult, MicroScenario, MicroSuite } from '@/net/contracts'

export type MicroAction = {
  schema_version: 'v1'
  decision_id: string
  action: string
  args: Record<string, unknown>
  public_message?: string
  private_thought?: string
}

export type MicroScenarioSummary = {
  scenario_id: string
  suite_id: string
  category: MicroScenario['category']
  difficulty: MicroScenario['difficulty']
  title: string
  description: string
  tags: string[]
  focal_player_id: string
  decision_type: string
  scoring_mode: MicroScenario['evaluation']['scoring_mode']
  research_metadata?: MicroResearchMetadata
}

export type MicroDecisionAttempt = {
  parsed_tool_call?: Record<string, unknown> | null
  parsed_tool_calls?: Record<string, unknown>[] | null
  validation_errors?: string[]
  response?: Record<string, unknown> | null
  user_payload?: Record<string, unknown> | null
  system_prompt?: string | null
}

export type MicroDecisionBundle = {
  decision_id: string
  decision_type: string
  final_action?: MicroAction | null
  retry_used?: boolean
  fallback_used?: boolean
  fallback_reason?: string | null
  timing?: {
    latency_ms?: number | null
  } | null
  attempts?: MicroDecisionAttempt[]
}

export type MicroRunSummary = {
  run_id: string
  mode: 'micro'
  scenario_id: string
  suite_id: string
  category: MicroScenario['category']
  title: string
  description: string
  tags: string[]
  focal_player_id: string
  decision_id: string
  decision_type: string
  prompt_condition?: string
  player: {
    player_id: string
    name: string
    openrouter_model_id: string
    model_display_name: string
    reasoning?: {
      effort?: string
    } | null
  }
  result: {
    retry_used: boolean
    fallback_used: boolean
    fallback_reason?: string | null
    final_action?: MicroAction | null
    request_start_ms?: number | null
    response_end_ms?: number | null
    latency_ms?: number | null
    score?: MicroResult['score']
  }
}

export type MicroArtifactPaths = {
  run_dir: string
  scenario: string
  result: string
  summary: string
  actions: string
  decisions: string
  state: string[]
  prompts: string[]
}

export type MicroRunDetail = {
  run_id: string
  summary: MicroRunSummary
  scenario: MicroScenario
  result?: MicroResult
  decision_bundle: MicroDecisionBundle | null
  artifact_paths?: MicroArtifactPaths
}

export type MicroLeaderboardRow = {
  model: string
  scenario_count: number
  average_score: number
  fallback_rate: number
  retry_rate: number
  invalid_rate: number
  average_latency_ms: number
  category_scores: Partial<Record<MicroScenario['category'], number>>
}

export type MicroLeaderboard = {
  rows: MicroLeaderboardRow[]
  category_breakdown: Record<string, Partial<Record<MicroScenario['category'], number>>>
}

export type MicroBatchDetail = {
  batch_id: string
  config: {
    batch_id: string
    suite_id: string
    model_ids: string[]
    prompt_condition: string
    scenario_ids: string[]
  }
  leaderboard: MicroLeaderboard
  results: Record<string, unknown>[]
  failures: Record<string, unknown>[]
}

const expectOk = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(errorText || `Request failed with status ${response.status}`)
  }
  return response.json() as Promise<T>
}

export const fetchMicroScenarios = async (apiBase = getApiBaseUrl()): Promise<MicroScenarioSummary[]> => {
  const payload = await expectOk<{ scenarios: MicroScenarioSummary[] }>(await fetch(`${apiBase}/micro/scenarios`))
  return payload.scenarios
}

export const fetchMicroScenario = async (
  scenarioId: string,
  apiBase = getApiBaseUrl()
): Promise<MicroScenario> => {
  return expectOk<MicroScenario>(await fetch(`${apiBase}/micro/scenarios/${scenarioId}`))
}

export const fetchMicroSuites = async (apiBase = getApiBaseUrl()): Promise<MicroSuite[]> => {
  const payload = await expectOk<{ suites: MicroSuite[] }>(await fetch(`${apiBase}/micro/suites`))
  return payload.suites
}

export const fetchMicroSuite = async (
  suiteId: string,
  apiBase = getApiBaseUrl()
): Promise<MicroSuite> => {
  return expectOk<MicroSuite>(await fetch(`${apiBase}/micro/suites/${suiteId}`))
}

export const runMicroScenario = async (
  payload: {
    scenario_id: string
    openrouter_model_id?: string | null
    name?: string | null
    reasoning?: {
      effort?: string
    } | null
    prompt_condition?: string
  },
  apiBase = getApiBaseUrl()
): Promise<{ run_id: string; result?: MicroResult }> => {
  return expectOk<{ run_id: string; result?: MicroResult }>(
    await fetch(`${apiBase}/micro/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  )
}

type MicroStreamEvent =
  | { event: 'status'; data: { state: string } }
  | { event: 'llm_delta'; data: { type: string; text?: string; scenario_id?: string; model?: string | null } }
  | { event: 'result'; data: { run_id: string; result?: MicroResult } }
  | { event: 'error'; data: { message?: string } }

type MicroBatchStreamEvent =
  | {
      event: 'status'
      data: {
        state: string
        batch_id?: string
        scenario_count?: number
        task_count?: number
        parallel_limit?: number
        wave_index?: number
        wave_size?: number
        wave_scenario_ids?: string[]
        completed_count?: number
      }
    }
  | { event: 'llm_delta'; data: { type: string; text?: string; scenario_id: string; model?: string | null } }
  | { event: 'scenario_started'; data: { scenario_id: string; model?: string | null } }
  | {
      event: 'scenario_result'
      data: {
        scenario_id: string
        model: string
        run_id: string
        action: MicroAction
        score: MicroResult['score']
        retry_used: boolean
        fallback_used: boolean
        latency_ms?: number | null
      }
    }
  | { event: 'batch_result'; data: { batch_id: string; leaderboard: MicroLeaderboard } }
  | { event: 'scenario_error'; data: { scenario_id?: string; model?: string | null; message?: string } }
  | { event: 'error'; data: { message?: string; batch_id?: string } }

export const runMicroScenarioStream = async (
  payload: {
    scenario_id: string
    openrouter_model_id?: string | null
    name?: string | null
    reasoning?: {
      effort?: string
    } | null
    prompt_condition?: string
  },
  handlers: {
    onDelta?: (event: Extract<MicroStreamEvent, { event: 'llm_delta' }>['data']) => void
    onStatus?: (event: Extract<MicroStreamEvent, { event: 'status' }>['data']) => void
    signal?: AbortSignal
  } = {},
  apiBase = getApiBaseUrl()
): Promise<{ run_id: string; result?: MicroResult }> => {
  const response = await fetch(`${apiBase}/micro/run/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
    body: JSON.stringify(payload),
    signal: handlers.signal,
  })
  if (!response.ok || !response.body) {
    return expectOk<{ run_id: string; result?: MicroResult }>(response)
  }
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let result: { run_id: string; result?: MicroResult } | null = null

  const dispatch = (block: string) => {
    const lines = block.split(/\r?\n/)
    const eventName = lines.find((line) => line.startsWith('event:'))?.slice('event:'.length).trim()
    const dataText = lines
      .filter((line) => line.startsWith('data:'))
      .map((line) => line.slice('data:'.length).trim())
      .join('\n')
    if (!eventName || !dataText) return
    const parsed = JSON.parse(dataText) as MicroStreamEvent['data']
    if (eventName === 'llm_delta') {
      handlers.onDelta?.(parsed as Extract<MicroStreamEvent, { event: 'llm_delta' }>['data'])
    } else if (eventName === 'status') {
      handlers.onStatus?.(parsed as Extract<MicroStreamEvent, { event: 'status' }>['data'])
    } else if (eventName === 'result') {
      result = parsed as { run_id: string; result?: MicroResult }
    } else if (eventName === 'error') {
      const error = parsed as { message?: string }
      throw new Error(error.message || 'Micro stream failed.')
    }
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const blocks = buffer.split(/\r?\n\r?\n/)
    buffer = blocks.pop() ?? ''
    for (const block of blocks) {
      dispatch(block)
    }
  }
  buffer += decoder.decode()
  if (buffer.trim()) {
    dispatch(buffer)
  }
  if (!result) {
    throw new Error('Micro stream ended without a result.')
  }
  return result
}

export const runMicroBatchStream = async (
  payload: {
    suite_id?: string
    openrouter_model_ids?: string[]
    prompt_condition?: string
    reasoning?: {
      effort?: string
    } | null
    scenario_ids?: string[] | null
  },
  handlers: {
    onDelta?: (event: Extract<MicroBatchStreamEvent, { event: 'llm_delta' }>['data']) => void
    onStatus?: (event: Extract<MicroBatchStreamEvent, { event: 'status' }>['data']) => void
    onScenarioStarted?: (event: Extract<MicroBatchStreamEvent, { event: 'scenario_started' }>['data']) => void
    onScenarioResult?: (event: Extract<MicroBatchStreamEvent, { event: 'scenario_result' }>['data']) => void
    onScenarioError?: (event: Extract<MicroBatchStreamEvent, { event: 'scenario_error' }>['data']) => void
    signal?: AbortSignal
  } = {},
  apiBase = getApiBaseUrl()
): Promise<{ batch_id: string; leaderboard: MicroLeaderboard }> => {
  const response = await fetch(`${apiBase}/micro/batches/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
    body: JSON.stringify(payload),
    signal: handlers.signal,
  })
  if (!response.ok || !response.body) {
    return expectOk<{ batch_id: string; leaderboard: MicroLeaderboard }>(response)
  }
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let result: { batch_id: string; leaderboard: MicroLeaderboard } | null = null

  const dispatch = (block: string) => {
    const lines = block.split(/\r?\n/)
    const eventName = lines.find((line) => line.startsWith('event:'))?.slice('event:'.length).trim()
    const dataText = lines
      .filter((line) => line.startsWith('data:'))
      .map((line) => line.slice('data:'.length).trim())
      .join('\n')
    if (!eventName || !dataText) return
    const parsed = JSON.parse(dataText) as MicroBatchStreamEvent['data']
    if (eventName === 'llm_delta') {
      handlers.onDelta?.(parsed as Extract<MicroBatchStreamEvent, { event: 'llm_delta' }>['data'])
    } else if (eventName === 'status') {
      handlers.onStatus?.(parsed as Extract<MicroBatchStreamEvent, { event: 'status' }>['data'])
    } else if (eventName === 'scenario_started') {
      handlers.onScenarioStarted?.(parsed as Extract<MicroBatchStreamEvent, { event: 'scenario_started' }>['data'])
    } else if (eventName === 'scenario_result') {
      handlers.onScenarioResult?.(parsed as Extract<MicroBatchStreamEvent, { event: 'scenario_result' }>['data'])
    } else if (eventName === 'scenario_error') {
      handlers.onScenarioError?.(parsed as Extract<MicroBatchStreamEvent, { event: 'scenario_error' }>['data'])
    } else if (eventName === 'batch_result') {
      result = parsed as { batch_id: string; leaderboard: MicroLeaderboard }
    } else if (eventName === 'error') {
      const error = parsed as { message?: string }
      throw new Error(error.message || 'Micro batch stream failed.')
    }
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const blocks = buffer.split(/\r?\n\r?\n/)
    buffer = blocks.pop() ?? ''
    for (const block of blocks) {
      dispatch(block)
    }
  }
  buffer += decoder.decode()
  if (buffer.trim()) {
    dispatch(buffer)
  }
  if (!result) {
    throw new Error('Micro batch stream ended without a result.')
  }
  return result
}

export const fetchMicroRun = async (runId: string, apiBase = getApiBaseUrl()): Promise<MicroRunDetail> => {
  return expectOk<MicroRunDetail>(await fetch(`${apiBase}/micro/runs/${runId}`))
}

export const runMicroBatch = async (
  payload: {
    suite_id?: string
    openrouter_model_ids?: string[]
    prompt_condition?: string
    reasoning?: {
      effort?: string
    } | null
    scenario_ids?: string[] | null
  },
  apiBase = getApiBaseUrl()
): Promise<{ batch_id: string; leaderboard: MicroLeaderboard }> => {
  return expectOk<{ batch_id: string; leaderboard: MicroLeaderboard }>(
    await fetch(`${apiBase}/micro/batches`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  )
}

export const fetchMicroBatch = async (
  batchId: string,
  apiBase = getApiBaseUrl()
): Promise<MicroBatchDetail> => {
  return expectOk<MicroBatchDetail>(await fetch(`${apiBase}/micro/batches/${batchId}`))
}

export const fetchMicroBatchLeaderboard = async (
  batchId: string,
  apiBase = getApiBaseUrl()
): Promise<MicroLeaderboard> => {
  return expectOk<MicroLeaderboard>(await fetch(`${apiBase}/micro/batches/${batchId}/leaderboard`))
}

export const legalActionArgKeys = (action: LegalAction): string[] => {
  const schema = action.args_schema as { properties?: Record<string, unknown> }
  const properties = schema.properties
  if (!properties || typeof properties !== 'object') {
    return []
  }
  return Object.keys(properties)
}
