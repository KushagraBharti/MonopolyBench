import { useRef, useState } from 'react'
import { cloudRequest, type CloudJob } from '@/net/jobs'
import { errorText } from './cloudUi'

/** Posts a server-listed job action. Cancel always asks first; one action at a time. */
export function useJobAction(job: CloudJob, onChanged?: (job: CloudJob) => void) {
  const [error, setError] = useState('')
  const [busy, setBusy] = useState('')
  const lock = useRef(false)
  async function act(action: string) {
    if (lock.current) return
    if (action === 'cancel' && !window.confirm('Cancel this game? It stops for good and can’t be resumed.')) return
    lock.current = true; setBusy(action); setError('')
    try { onChanged?.(await cloudRequest<CloudJob>(`/jobs/${job.job_id}/${action}`, {})) }
    catch (e) { setError(errorText(e)) }
    finally { lock.current = false; setBusy('') }
  }
  return { act, error, busy }
}
