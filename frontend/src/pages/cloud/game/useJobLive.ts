import { useEffect, useRef, useState } from 'react'
import { CLOUD_API, type CloudJob, type CloudLive } from '@/net/jobs'
import { useCloudStore, type CloudView } from '@/state/cloud'
import { useGameStore } from '@/state/store'

export type LiveConnection = 'connecting' | 'live' | 'reconnecting' | 'closed'

/** Same cap as the cloud view cache, so panels show everything the stream kept. */
export const MAX_PANEL_EVENTS = 500
const RETRY_BASE_MS = 1000
const RETRY_MAX_MS = 30000

export type JobLive = {
  connection: LiveConnection
  /** Set when the stream refuses this job for good (closed with 4404). */
  error: string
  /** True when older events were dropped from the cache; full history is in Decisions and artifacts. */
  historyLimited: boolean
  /**
   * False while the board shows a polled snapshot newer than the streamed events, so
   * event-derived context (pending decision, dice) would describe an older position.
   */
  eventsSynchronized: boolean
}

/**
 * Streams one job into the shared game store. The cloud view (per job, ordered, guarded
 * against stale commits and older generations) is canonical; the game store that the
 * panels read is always a projection of the accepted view, so every panel renders the
 * same snapshot. Revisits and StrictMode remounts hydrate from the cached view because
 * the server's replay of already-seen commits is rejected as a duplicate.
 */
export function useJobLive(id: string, job: CloudJob | null): JobLive {
  const [connection, setConnection] = useState<LiveConnection>('connecting')
  const [error, setError] = useState('')
  const [historyLimited, setHistoryLimited] = useState(false)
  const [polledAhead, setPolledAhead] = useState(false)
  // Commit of a polled job snapshot shown while the stream had nothing newer.
  const polledCommit = useRef<number | null>(null)
  // A different job starts from a clean live state (reset during render, not in an effect).
  const [liveId, setLiveId] = useState(id)
  if (liveId !== id) {
    setLiveId(id)
    setConnection('connecting')
    setError('')
    setHistoryLimited(false)
    setPolledAhead(false)
  }

  useEffect(() => {
    let active = true
    let socket: WebSocket | null = null
    let timer: ReturnType<typeof setTimeout> | undefined
    let failures = 0
    polledCommit.current = null

    const game = useGameStore.getState()
    game.resetLogs()
    // resetLogs marks the previous run stopped; a revisited run must not be suppressed.
    useGameStore.setState({ stoppedRunId: null })

    const project = (view: CloudView) => {
      if (view.snapshot && (polledCommit.current === null || view.commit >= polledCommit.current)) {
        polledCommit.current = null
        setPolledAhead(false)
        useGameStore.getState().setSnapshot(view.snapshot)
      }
      // Event seq starts at 0; a later first event means older history was trimmed.
      setHistoryLimited(view.events.length > 0 && view.events[0].seq > 0)
      useGameStore.setState({ events: view.events.slice(-MAX_PANEL_EVENTS).reverse() })
    }

    const cached = useCloudStore.getState().views[id]
    if (cached) project(cached)

    const connect = () => {
      if (!active) return
      const view = useCloudStore.getState().views[id]
      const url = new URL(`${CLOUD_API}/jobs/${id}/ws`, window.location.href)
      url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
      url.searchParams.set('after', String(view?.commit ?? 0))
      url.searchParams.set('generation', String(view?.generation ?? -1))
      const current = new WebSocket(url)
      socket = current
      let openedAt = 0
      current.onopen = () => { if (active && socket === current) { openedAt = Date.now(); setConnection('live') } }
      current.onmessage = message => {
        if (!active || socket !== current) return
        let envelope: CloudLive
        try { envelope = JSON.parse(message.data) } catch { return }
        if (envelope.type === 'HELLO' || envelope.job_id !== id) return
        if (!useCloudStore.getState().receive(envelope)) return
        const accepted = useCloudStore.getState().views[id]
        if (accepted) project(accepted)
      }
      current.onclose = event => {
        if (!active || socket !== current) return
        if (event.code === 4401) { window.location.assign('/login'); return }
        if (event.code === 4404) {
          // The server does not know this job: stop retrying and drop anything cached under its id.
          useCloudStore.setState(state => {
            if (!(id in state.views)) return state
            const views = { ...state.views }
            delete views[id]
            return { views }
          })
          useGameStore.getState().resetLogs()
          useGameStore.setState({ stoppedRunId: null })
          setConnection('closed')
          setError('Live updates unavailable: the server could not find this game.')
          return
        }
        // 1013 (try again later) and drops back off exponentially, capped. A connection
        // that stayed up a while counts as healthy and restarts the backoff.
        if (openedAt && Date.now() - openedAt > 10000) failures = 0
        setConnection('reconnecting')
        const delay = Math.min(RETRY_MAX_MS, RETRY_BASE_MS * 2 ** failures)
        failures += 1
        timer = setTimeout(connect, delay)
      }
    }
    connect()
    return () => {
      active = false
      clearTimeout(timer)
      if (socket) { socket.onmessage = null; socket.onclose = null; socket.onopen = null; socket.close() }
    }
  }, [id])

  // The polled job carries a snapshot too. Use it only when the stream has nothing newer.
  useEffect(() => {
    if (connection === 'closed') return
    if (!job || job.job_id !== id || !job.snapshot || job.snapshot.run_id !== job.run_id) return
    const view = useCloudStore.getState().views[id]
    const store = useGameStore.getState()
    const shown = store.snapshot?.run_id === job.run_id ? store.snapshot : null
    if (job.snapshot_kind === 'initial_preview') {
      if (!shown && !view?.snapshot) store.setSnapshot(job.snapshot)
      return
    }
    if (!view?.snapshot || job.commit_seq > view.commit) {
      if (polledCommit.current !== null && job.commit_seq <= polledCommit.current) return
      polledCommit.current = job.commit_seq
      setPolledAhead(true)
      store.setSnapshot(job.snapshot)
    }
  }, [job, id, connection])

  return { connection, error, historyLimited, eventsSynchronized: !polledAhead }
}
