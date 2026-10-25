import { useEffect, useId, useRef, useState, type FormEvent } from 'react'
import { cloudRequest, type CloudJob, type GamePreparation, type GamePrepareRequest } from '@/net/jobs'
import { BudgetField, BudgetNote, SeatTokens, Shell, Token } from './CloudShell'
import { EFFORTS, capitalize, errorText, modelInfo, parseBudget, ROSTER, settingsLine, type Effort } from './cloudUi'

type Mode = 'single' | 'smoke'
const MAX_SINGLE_TURNS = 10000

interface Form { seats: string[]; effort: Effort; fullGame: boolean; turns: number; budget: string; count: number }
interface Prepared { request: GamePrepareRequest; preparation: GamePreparation; idempotencyKey: string }

const ENDPOINTS: Record<Mode, { prepare: string; start: string }> = {
  single: { prepare: '/games/prepare', start: '/games' },
  smoke: { prepare: '/smoke/prepare', start: '/smoke' },
}

function formProblem(mode: Mode, form: Form) {
  const turns = form.turns
  if (mode === 'smoke') {
    if (!Number.isInteger(turns) || turns < 5 || turns > 10) return 'Choose a turn limit from 5 to 10.'
    if (!Number.isInteger(form.count) || form.count < 1 || form.count > 20) return 'Choose from 1 to 20 test games.'
  } else if (!form.fullGame && (!Number.isInteger(turns) || turns < 1 || turns > MAX_SINGLE_TURNS)) {
    return `Choose a turn limit from 1 to ${MAX_SINGLE_TURNS}, or play the full game.`
  }
  return parseBudget(form.budget).problem
}

function toRequest(mode: Mode, form: Form): GamePrepareRequest {
  return {
    models: form.seats,
    effort: form.effort,
    max_turns: mode === 'smoke' ? form.turns : form.fullGame ? null : form.turns,
    cost_budget: parseBudget(form.budget).value,
    ...(mode === 'smoke' ? { count: form.count } : {}),
  }
}

/**
 * Two-step setup for games outside a campaign: choose settings, review the prepared games, then start explicitly.
 * Single games play to the end by default; model tests are short and capped at 10 turns.
 */
export function GameSetup({ mode, onStarted, onCancel }: { mode: Mode; onStarted: (jobs: CloudJob[]) => void; onCancel: () => void }) {
  const [form, setForm] = useState<Form>({ seats: ROSTER, effort: 'medium', fullGame: true, turns: mode === 'smoke' ? 5 : 200, budget: '', count: 1 })
  const [step, setStep] = useState<'setup' | 'review'>('setup')
  const [prepared, setPrepared] = useState<Prepared | null>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState<'' | 'review' | 'start'>('')
  const lock = useRef(false)
  const ids = useId()
  const problem = formProblem(mode, form)
  const noun = mode === 'smoke' ? (form.count === 1 ? 'test game' : 'test games') : 'game'

  function update(next: Partial<Form>) { setForm({ ...form, ...next }); setError('') }

  async function review(e: FormEvent) {
    e.preventDefault()
    if (lock.current) return
    if (problem) { setError(problem); return }
    const request = toRequest(mode, form)
    // Reuse the stored preparation when nothing changed, so its seeds and idempotency key stay the same.
    if (prepared && JSON.stringify(prepared.request) === JSON.stringify(request)) { setError(''); setStep('review'); return }
    lock.current = true; setBusy('review'); setError('')
    try {
      const preparation = await cloudRequest<GamePreparation>(ENDPOINTS[mode].prepare, request)
      setPrepared({ request, preparation, idempotencyKey: crypto.randomUUID() })
      setStep('review')
    } catch (err) { setError(errorText(err)) }
    finally { lock.current = false; setBusy('') }
  }

  async function start() {
    if (!prepared || lock.current) return
    lock.current = true; setBusy('start'); setError('')
    try {
      const jobs = await cloudRequest<CloudJob[]>(ENDPOINTS[mode].start, { preparation_id: prepared.preparation.preparation_id, idempotency_key: prepared.idempotencyKey })
      onStarted(Array.isArray(jobs) ? jobs : [])
    } catch (err) {
      setError(errorText(err))
      lock.current = false; setBusy('')
    }
  }

  const configs = prepared?.preparation.configs ?? []

  if (step === 'review' && prepared) return <div className="cb-review">
    <h2 className="cb-step-title">Review and start</h2>
    <p>Nothing has started yet. {mode === 'single' ? 'This game starts' : `These ${configs.length} ${noun} start`} only when you press Start.</p>
    {configs.map((config, i) => <article className="cb-test-row" key={config.run_id}>
      <strong>{mode === 'single' ? 'Your game' : `Test game ${i + 1}`}</strong>
      <SeatTokens models={config.players.map(p => p.openrouter_model_id)} labelled />
      <small>{settingsLine(config)}</small>
      <small className="cb-meta">Seed <code>{config.seed}</code> · Run <code>{config.run_id}</code></small>
    </article>)}
    <section className="cb-section">
      <h3>Billing</h3>
      <p>{mode === 'single' ? 'The game is' : 'Test games are'} paid from your existing provider funding: your OpenRouter balance, or your own provider accounts for any keys connected to OpenRouter. This app makes no purchases. Cost depends on the models, how long the game runs and how much they reason.</p>
      {prepared.request.cost_budget != null ? <p>{mode === 'single' ? 'The game pauses' : 'Each test game pauses'} once its recorded spend reaches ${prepared.request.cost_budget.toFixed(2)}. This is not a hard cap.</p> : <p>No spend pause is set.</p>}
      <BudgetNote />
    </section>
    <p className="cb-hint">{mode === 'single' ? 'A single game is not a balanced research campaign: seats don’t rotate and it isn’t paired with other boards. Its moves, prompts and replay files are still saved like any other game.' : 'Test games are excluded from research. Their files are still saved.'}</p>
    {error ? <p className="cb-error" role="alert">{error}</p> : null}
    <div className="cb-actions">
      <button className="cb-btn cb-btn-primary" disabled={Boolean(busy)} onClick={() => void start()}>{busy === 'start' ? 'Starting…' : mode === 'single' ? 'Start game' : `Start ${configs.length} ${noun}`}</button>
      <button className="cb-btn cb-btn-ghost" disabled={Boolean(busy)} onClick={() => { setError(''); setStep('setup') }}>Back to settings</button>
    </div>
  </div>

  return <form className="cb-form" onSubmit={review} noValidate>
    <fieldset className="cb-field">
      <legend>Players</legend>
      <p className="cb-hint">Seat 1 moves first. You can pick the same model more than once.</p>
      <div className="cb-seat-picks">
        {form.seats.map((model, i) => <label className="cb-seat-pick" key={i}>
          <span>Seat {i + 1}</span>
          <span className="cb-seat-select"><Token model={model} /><select className="cb-input" value={model} onChange={e => update({ seats: form.seats.map((m, n) => n === i ? e.target.value : m) })}>{ROSTER.map(m => <option key={m} value={m}>{modelInfo(m).name}</option>)}</select></span>
        </label>)}
      </div>
    </fieldset>

    <fieldset className="cb-field">
      <legend>Reasoning effort</legend>
      <p className="cb-hint">Used by every seat. Research campaigns use medium.</p>
      <div className="cb-choices">
        {EFFORTS.map(effort => <label key={effort} className="cb-choice"><input type="radio" name={`${ids}-effort`} checked={form.effort === effort} onChange={() => update({ effort })} /><span>{capitalize(effort)}</span></label>)}
      </div>
    </fieldset>

    {mode === 'single' ? <fieldset className="cb-field">
      <legend>Turn limit</legend>
      <p className="cb-hint">A full game plays until one player is left.</p>
      <div className="cb-choices">
        <label className="cb-choice"><input type="radio" name={`${ids}-turns`} checked={form.fullGame} onChange={() => update({ fullGame: true })} /><span>Full game</span></label>
        <label className="cb-choice"><input type="radio" name={`${ids}-turns`} checked={!form.fullGame} onChange={() => update({ fullGame: false })} /><span>Stop after a number of turns</span></label>
      </div>
      {!form.fullGame ? <div className="cb-inline-field">
        <label htmlFor={`${ids}-turn-count`}>Turns</label>
        <input id={`${ids}-turn-count`} className="cb-input cb-input-short" type="number" inputMode="numeric" min={1} max={MAX_SINGLE_TURNS} value={Number.isFinite(form.turns) ? form.turns : ''} onChange={e => update({ turns: e.target.valueAsNumber })} />
        <span className="cb-hint">1 to {MAX_SINGLE_TURNS.toLocaleString()}.</span>
      </div> : null}
    </fieldset> : <div className="cb-field-row">
      <label className="cb-field">Turn limit<input className="cb-input cb-input-short" type="number" inputMode="numeric" min={5} max={10} value={Number.isFinite(form.turns) ? form.turns : ''} onChange={e => update({ turns: e.target.valueAsNumber })} /><small className="cb-hint">5 to 10</small></label>
      <label className="cb-field">Games<input className="cb-input cb-input-short" type="number" inputMode="numeric" min={1} max={20} value={Number.isFinite(form.count) ? form.count : ''} onChange={e => update({ count: e.target.valueAsNumber })} /><small className="cb-hint">1 to 20</small></label>
    </div>}

    <BudgetField value={form.budget} onChange={budget => update({ budget })} scope={mode === 'smoke' ? 'each game' : 'game'} />

    {error ? <p className="cb-error" role="alert">{error}</p> : null}
    <div className="cb-actions">
      <button className="cb-btn cb-btn-primary" disabled={Boolean(busy)}>{busy === 'review' ? 'Preparing review…' : mode === 'single' ? 'Review game' : 'Review test games'}</button>
      <button type="button" className="cb-btn cb-btn-ghost" disabled={Boolean(busy)} onClick={onCancel}>Cancel</button>
    </div>
    <p className="cb-hint">Reviewing draws the board. Nothing is played or charged until you start.</p>
  </form>
}

export function NewGamePage({ mode = 'single' }: { mode?: Mode }) {
  if (mode === 'smoke') return <Shell section="tests">
    <div className="cb-page cb-wizard">
      <a className="cb-back" href="/tests">Tests</a>
      <h1>New model test</h1>
      <p className="cb-lede">Short games of 5 to 10 turns, to check that every model responds. Tests are excluded from research and are separate from campaigns.</p>
      <GameSetup mode="smoke" onCancel={() => window.location.assign('/tests')} onStarted={jobs => window.location.assign(jobs.length === 1 ? `/games/${jobs[0].job_id}` : '/tests')} />
    </div>
  </Shell>
  return <Shell section="games">
    <div className="cb-page cb-wizard">
      <a className="cb-back" href="/games">Games</a>
      <h1>New game</h1>
      <p className="cb-lede">Pick any four models and settings, review, then start. For a balanced study where every model plays every seat, <a href="/campaigns/new">create a campaign</a> instead.</p>
      <GameSetup mode="single" onCancel={() => window.location.assign('/games')} onStarted={jobs => window.location.assign(jobs[0] ? `/games/${jobs[0].job_id}` : '/games')} />
    </div>
  </Shell>
}

/** Short capped games that check models respond. Separate from research campaigns. */
export function TestModelsDialog({ close, onLaunched }: { close: () => void; onLaunched: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null)
  useEffect(() => { dialog.current?.showModal() }, [])
  return <dialog ref={dialog} onCancel={close} aria-labelledby="test-title" className="cloud-modal">
    <button className="cb-btn cb-btn-ghost cloud-close" onClick={close} aria-label="Close">×</button>
    <h2 id="test-title">Test models</h2>
    <p className="cb-hint">Short games of 5 to 10 turns, to check that models respond. They are excluded from research and are separate from campaigns.</p>
    <GameSetup mode="smoke" onCancel={close} onStarted={() => { onLaunched(); close() }} />
  </dialog>
}
