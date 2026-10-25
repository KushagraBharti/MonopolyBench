export type { CloudJob, CloudCampaign, CloudLive, CloudConfig, CampaignCell, CampaignPreparation, CampaignReadiness, CampaignPlannedCell, GamePrepareRequest, GamePreparation, CloudExport, CloudStatus, CloudDashboard } from '@contracts/cloud'

export const CLOUD_API = (import.meta.env.VITE_API_BASE || '/api').replace(/\/$/, '')
export async function cloudRequest<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(CLOUD_API + path, {
    credentials: 'include',
    ...(body === undefined ? {} : { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }),
  })
  if (response.status === 401 && window.location.pathname !== '/login') window.location.assign('/login')
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(typeof error.detail === 'string' ? error.detail : JSON.stringify(error.detail))
  }
  return response.json() as Promise<T>
}
