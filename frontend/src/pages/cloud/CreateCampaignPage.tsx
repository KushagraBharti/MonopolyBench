import { useId, useRef, useState, type FormEvent, type ReactNode } from 'react'
import { cloudRequest, type CampaignPreparation, type CloudCampaign } from '@/net/jobs'
import { BudgetField, BudgetNote, CheckConnections, Facts, Notice, SeatTokens, Shell, Token } from './CloudShell'
import { boardNumbers, errorText, modelInfo, money, needsConnectionCheck, parseBudget, ROSTER } from './cloudUi'

const GAME_PRESETS = [4, 8, 12, 24, 40, 80]
const MAX_GAMES = 80

interface Setup { name: string; games: number; concurrency: number; budget: string }
interface Prepared { request: Setup; preparation: CampaignPreparation; idempotencyKey: string }

function sameSetup(a: Setup, b: Setup) {
  return a.name.trim() === b.name.trim() && a.games === b.games && a.concurrency === b.concurrency && parseBudget(a.budget).value === parseBudget(b.budget).value
}

function gamesProblem(games: number) {
  if (!Number.isInteger(games) || games < 4) return 'Choose at least 4 games.'
  if (games > MAX_GAMES) return `Choose at most ${MAX_GAMES} games.`
  if (games % 4 !== 0) return 'Choose a multiple of 4, so every model plays every seat on each board.'
  return ''
}

export function CreateCampaignPage() {
  const [step, setStep] = useState<'setup' | 'review'>('setup')
  const [setup, setSetup] = useState<Setup>({ name: '', games: 4, concurrency: 4, budget: '' })
  const [prepared, setPrepared] = useState<Prepared | null>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState<'' | 'review' | 'save'>('')
  const requestId = useRef(0)
  const saving = useRef(false)
  const heading = useRef<HTMLHeadingElement>(null)

  const problem = !setup.name.trim() ? 'Give the campaign a name.' : gamesProblem(setup.games) || parseBudget(setup.budget).problem

  function goTo(next: 'setup' | 'review') {
    setStep(next)
    requestAnimationFrame(() => heading.current?.focus())
  }

  async function review(e: FormEvent) {
    e.preventDefault()
    if (problem || busy) { setError(problem); return }
    setError('')
    // Reuse the stored seed draw when nothing changed; a new draw is only made for a new setup.
    if (prepared && sameSetup(prepared.request, setup)) { goTo('review'); return }
    const id = ++requestId.current
    const request = { ...setup, name: setup.name.trim() }
    setBusy('review')
    try {
      const preparation = await cloudRequest<CampaignPreparation>('/campaigns/prepare', { name: request.name, seed_blocks: request.games / 4, concurrency: request.concurrency, cost_budget: parseBudget(request.budget).value })
      if (id !== requestId.current) return
      setPrepared({ request, preparation, idempotencyKey: crypto.randomUUID() })
      goTo('review')
    } catch (err) {
      if (id === requestId.current) setError(errorText(err))
    } finally {
      if (id === requestId.current) setBusy('')
    }
  }

  async function save() {
    if (!prepared || saving.current) return
    saving.current = true; setBusy('save'); setError('')
    try {
      const campaign = await cloudRequest<CloudCampaign>('/campaigns/create', { preparation_id: prepared.preparation.preparation_id, idempotency_key: prepared.idempotencyKey })
      window.location.assign(`/campaigns/${encodeURIComponent(campaign.campaign_id)}?saved=1`)
    } catch (err) {
      setError(errorText(err))
      saving.current = false; setBusy('')
    }
  }

  return <Shell>
    <div className="cb-page cb-wizard">
      <a className="cb-back" href="/campaigns">Campaigns</a>
      <h1 ref={heading} tabIndex={-1}>{step === 'setup' ? 'Create a campaign' : 'Review your campaign'}</h1>
      <ol className="cb-steps" aria-label="Steps">
        <li aria-current={step === 'setup' ? 'step' : undefined} data-done={step === 'review' || undefined}><span>1</span>Set up</li>
        <li aria-current={step === 'review' ? 'step' : undefined}><span>2</span>Review and save</li>
        <li><span>3</span>Start games</li>
      </ol>
      {step === 'setup'
        ? <SetupStep setup={setup} onChange={next => { setSetup(next); setError('') }} onSubmit={review} busy={busy === 'review'} error={error} />
        : prepared ? <ReviewStep prepared={prepared} busy={busy === 'save'} error={error} onBack={() => { setError(''); goTo('setup') }} onSave={() => void save()} onChecked={() => setError('')} /> : null}
    </div>
  </Shell>
}

function SetupStep({ setup, onChange, onSubmit, busy, error }: { setup: Setup; onChange: (s: Setup) => void; onSubmit: (e: FormEvent) => void; busy: boolean; error: string }) {
  const ids = useId()
  const custom = !GAME_PRESETS.includes(setup.games)
  const gameIssue = gamesProblem(setup.games)
  return <div className="cb-wizard-grid">
    <form className="cb-form" onSubmit={onSubmit} noValidate>
      <div className="cb-field">
        <label htmlFor={`${ids}-name`}>Campaign name</label>
        <input id={`${ids}-name`} className="cb-input" value={setup.name} maxLength={80} required autoComplete="off" placeholder="For example: November frontier study" onChange={e => onChange({ ...setup, name: e.target.value })} />
      </div>

      <fieldset className="cb-field" aria-describedby={`${ids}-games-hint`}>
        <legend>Number of games</legend>
        <p className="cb-hint" id={`${ids}-games-hint`}>Games come in sets of 4. Each set shares one board and rotates the seats.</p>
        <div className="cb-choices">
          {GAME_PRESETS.map(n => <label key={n} className="cb-choice"><input type="radio" name="games" checked={setup.games === n} onChange={() => onChange({ ...setup, games: n })} /><span>{n}</span></label>)}
          <label className="cb-choice"><input type="radio" name="games" checked={custom} onChange={() => onChange({ ...setup, games: custom ? setup.games : 16 })} /><span>Other</span></label>
        </div>
        {custom ? <div className="cb-inline-field">
          <label htmlFor={`${ids}-games`}>Games</label>
          <input id={`${ids}-games`} className="cb-input cb-input-short" type="number" inputMode="numeric" min={4} max={MAX_GAMES} step={4} value={Number.isFinite(setup.games) ? setup.games : ''} aria-invalid={Boolean(gameIssue) || undefined} aria-describedby={`${ids}-games-error`} onChange={e => onChange({ ...setup, games: e.target.valueAsNumber })} />
          <span className="cb-hint" id={`${ids}-games-error`}>{gameIssue || `Up to ${MAX_GAMES}, in steps of 4.`}</span>
        </div> : null}
      </fieldset>

      <fieldset className="cb-field" aria-describedby={`${ids}-conc-hint`}>
        <legend>Games at the same time</legend>
        <p className="cb-hint" id={`${ids}-conc-hint`}>More at once finishes sooner. 4 is recommended.</p>
        <div className="cb-choices">
          {[1, 2, 3, 4, 5, 6, 7, 8].map(n => <label key={n} className="cb-choice"><input type="radio" name="concurrency" checked={setup.concurrency === n} onChange={() => onChange({ ...setup, concurrency: n })} /><span>{n}</span></label>)}
        </div>
      </fieldset>

      <fieldset className="cb-field">
        <legend>Players</legend>
        <p className="cb-hint">The same four study models play every game. This line-up is fixed for the study.</p>
        <ul className="cb-roster">
          {ROSTER.map(model => <li key={model}><Token model={model} /><span><strong>{modelInfo(model).name}</strong><small>{modelInfo(model).lab}</small></span></li>)}
        </ul>
      </fieldset>

      <section className="cb-field" aria-labelledby={`${ids}-preset`}>
        <h2 className="cb-field-title" id={`${ids}-preset`}>Study settings</h2>
        <Facts rows={[['Reasoning effort', 'Medium'], ['Turn limit', 'None, every game plays to the end']]} />
        <p className="cb-hint">These are fixed so every campaign game is comparable. To choose different models, effort or a turn limit, <a href="/games/new">run one game</a> or test models from the Games page.</p>
      </section>

      <BudgetField value={setup.budget} onChange={budget => onChange({ ...setup, budget })} scope="campaign" />

      {error ? <p className="cb-error" role="alert">{error}</p> : null}
      <div className="cb-actions">
        <button className="cb-btn cb-btn-primary" disabled={busy}>{busy ? 'Preparing review…' : 'Review campaign'}</button>
        <a className="cb-btn cb-btn-ghost" href="/campaigns">Cancel</a>
      </div>
      <p className="cb-hint">Reviewing draws the boards for this campaign. Nothing is played or charged.</p>
    </form>
    <Deed name={setup.name.trim() || 'Untitled campaign'} rows={deedRows(Number.isFinite(setup.games) ? setup.games : 0, setup.concurrency, parseBudget(setup.budget).value)} />
  </div>
}

function deedRows(games: number, concurrency: number, budget: number | null): [string, ReactNode][] {
  const boards = games > 0 && games % 4 === 0 ? games / 4 : null
  return [
    ['Games', games || '—'],
    ['Boards', boards ?? '—'],
    ['Plays per board', 4],
    ['At the same time', concurrency],
    ['Reasoning effort', 'Medium'],
    ['Turn limit', 'None'],
    ['Spend pause', budget == null ? 'None' : `${money(budget)} across campaign`],
  ]
}

/** Campaign summary styled as a title deed card. */
function Deed({ name, rows, footer }: { name: string; rows: [string, ReactNode][]; footer?: ReactNode }) {
  return <aside className="cb-deed" aria-label="Campaign summary">
    <header><small>Campaign</small><strong>{name}</strong></header>
    <dl>{rows.map(([term, value]) => <div key={term}><dt>{term}</dt><dd>{value}</dd></div>)}</dl>
    <footer>{footer ?? 'Every model sits in every seat once per board.'}</footer>
  </aside>
}

function ReviewStep({ prepared, busy, error, onBack, onSave, onChecked }: { prepared: Prepared; busy: boolean; error: string; onBack: () => void; onSave: () => void; onChecked: () => void }) {
  const { preparation } = prepared
  const cells = preparation.cells
  const boards = boardNumbers(cells)
  const firstSeed = [...boards.entries()].find(([, n]) => n === 1)?.[0]
  const firstBoard = cells.filter(c => c.seed === firstSeed).sort((a, b) => a.cell_index - b.cell_index)
  const name = (typeof preparation.config.study_label === 'string' && preparation.config.study_label) || prepared.request.name
  const concurrency = typeof preparation.config.concurrency === 'number' ? preparation.config.concurrency : prepared.request.concurrency
  const budget = typeof preparation.config.cost_budget === 'number' ? preparation.config.cost_budget : parseBudget(prepared.request.budget).value
  const [connectionsPassed, setConnectionsPassed] = useState(false)
  const preflightError = Boolean(error) && needsConnectionCheck(error)
  // The review's readiness was computed at preparation time; a passing check run here clears only its connection blocker.
  // The server re-checks everything on save.
  const blockers = preparation.readiness.reasons.filter(r => !(connectionsPassed && needsConnectionCheck(r)))
  function checked() { setConnectionsPassed(true); onChecked() }
  return <div className="cb-wizard-grid">
    <div className="cb-review">
      <section className="cb-section">
        <h2>How seats rotate</h2>
        <p>Every board is played four times from the same starting seed, and the seats rotate each time, so each model moves first once and sits in every seat once. Different decisions change what happens next, so the four games can play out differently and their dice and card draws aren’t guaranteed to match.</p>
        <div className="cb-table-wrap"><table className="cb-rotation">
          <caption>Board 1{boards.size > 1 ? `. Boards 2 to ${boards.size} rotate the same way.` : ''}</caption>
          <thead><tr><th scope="col">Game</th>{[1, 2, 3, 4].map(s => <th scope="col" key={s}>Seat {s}</th>)}</tr></thead>
          <tbody>{firstBoard.map((cell, i) => <tr key={cell.cell_index}><th scope="row">{i + 1}</th>{cell.models_by_seat.map((m, s) => <td key={s}><Token model={m} seat={s + 1} /><span>{modelInfo(m).name}</span></td>)}</tr>)}</tbody>
        </table></div>
      </section>

      <section className="cb-section">
        <h2>Billing</h2>
        <p>Games are paid from your existing provider funding: your OpenRouter balance, and your own provider accounts for any keys you’ve connected to OpenRouter. This app makes no purchases. There is no turn limit, so each game plays until it ends.</p>
        <p>{budget == null ? 'No spend pause is set, so games keep playing whatever they cost.' : `Games pause before new requests once the campaign’s combined recorded spend reaches ${money(budget)}. This is not a hard cap.`} You can pause, resume or cancel the whole campaign or any single game from the campaign page.</p>
        <BudgetNote />
      </section>

      <section className="cb-section">
        <h2>Before you save</h2>
        <p>Saving freezes this campaign to the current app version, so the same checks that allow games to start must pass now.</p>
        {blockers.length === 0
          ? <p className="cb-ok">{connectionsPassed ? 'Model connections passed. Other checks passed when this review was prepared.' : 'All checks passed when this review was prepared.'}</p>
          : <ul className="cb-reasons">{blockers.map(r => <li key={r}>{r}</li>)}</ul>}
        {blockers.some(needsConnectionCheck) && !preflightError ? <CheckConnections onDone={passed => passed && checked()} /> : null}
      </section>

      <details className="cb-disclosure">
        <summary>Research details</summary>
        <Facts rows={[
          ['Preparation', <code>{preparation.preparation_id}</code>],
          ['Board seeds', <code>{[...boards.keys()].join(', ')}</code>],
          ['Code version', <code>{preparation.git_sha}</code>],
          ['Image', <code>{preparation.image_digest}</code>],
          ['Seat rule', <code>{String(preparation.config.seat_permutation ?? 'cyclic_4')}</code>],
          ['Model roster', <code>{String(preparation.config.model_roster ?? '')}</code>],
        ]} />
        <div className="cb-table-wrap"><table className="cb-table cb-table-compact">
          <caption>Planned games in launch order</caption>
          <thead><tr><th scope="col">Order</th><th scope="col">Board</th><th scope="col">Seats</th><th scope="col">Run ID</th></tr></thead>
          <tbody>{[...cells].sort((a, b) => a.execution_rank - b.execution_rank).map(cell => <tr key={cell.cell_index}><td>{cell.execution_rank + 1}</td><td>{boards.get(cell.seed)}</td><td><SeatTokens models={cell.models_by_seat} /></td><td><code>{cell.run_id}</code></td></tr>)}</tbody>
        </table></div>
      </details>

      {error ? <div role="alert">
        {preflightError
          ? <Notice tone="bad" title="Model connections need a fresh check">
              <p>{error}</p>
              <p>Saving needs a passing connection check on the current code from the last 6 hours. Run the check, then save again. Your boards stay the same.</p>
              <CheckConnections onDone={passed => passed && checked()} />
            </Notice>
          : <p className="cb-error">{error}</p>}
      </div> : null}

      <div className="cb-actions">
        <button className="cb-btn cb-btn-primary" disabled={busy} onClick={onSave}>{busy ? 'Saving campaign…' : 'Save campaign'}</button>
        <button className="cb-btn cb-btn-ghost" disabled={busy} onClick={onBack}>Back to setup</button>
      </div>
      <p className="cb-hint">Saving doesn’t start any games. You’ll start them from the campaign page.</p>
    </div>
    <Deed name={name} rows={deedRows(cells.length, concurrency, budget)} footer={`${boards.size} ${boards.size === 1 ? 'board' : 'boards'} drawn. Not started.`} />
  </div>
}
