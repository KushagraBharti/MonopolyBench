import type { CloudJob } from '@/net/jobs'
import { ACTION_LABELS } from './cloudUi'
import { useJobAction } from './useJobAction'

/** One button per action the server allows for this job. No client-side guesses. */
export function JobControls({ job, onChanged }: { job: CloudJob; onChanged?: (job: CloudJob) => void }) {
  const { act, error, busy } = useJobAction(job, onChanged)
  return <>
    {job.allowed_actions.map(action => <button key={action} className={`cb-btn ${action === 'cancel' ? 'cb-btn-danger' : 'cb-btn-ghost'}`} disabled={Boolean(busy)} onClick={() => void act(action)}>{busy === action ? 'Working…' : ACTION_LABELS[action] ?? action}</button>)}
    {error ? <p className="cb-error" role="alert">{error}</p> : null}
  </>
}
