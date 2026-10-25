import { useState } from 'react'
import type { CloudExport } from '@/net/jobs'
import { Shell } from './CloudShell'
import { exportDownload, exportGroup, exportKindLabel, exportName, exportSource, fileSize, newestFirst, usePoll, when, type ExportGroup } from './cloudUi'

const FILTERS: { key: ExportGroup | null; label: string; param: string | null }[] = [
  { key: null, label: 'All', param: null },
  { key: 'single', label: 'Games', param: 'games' },
  { key: 'campaign', label: 'Campaigns', param: 'campaigns' },
  { key: 'smoke', label: 'Tests', param: 'tests' },
]

/** Every prepared package. Downloads use the signed-in session; nothing new is generated here. */
export function ExportsPage() {
  const { data, error } = usePoll<CloudExport[]>('/exports')
  const [search, setSearch] = useState('')
  const param = new URLSearchParams(window.location.search).get('type')
  const filter = FILTERS.find(f => f.param === param) ?? FILTERS[0]
  const needle = search.trim().toLowerCase()
  const items = newestFirst(data ?? [])
    .filter(item => !filter.key || exportGroup(item) === filter.key)
    .filter(item => !needle || [exportName(item), item.run_id, item.campaign_id, item.scope_id, item.export_id].some(v => v?.toLowerCase().includes(needle)))
  return <Shell section="exports">
    <div className="cb-page">
      <header className="cb-page-head">
        <div><h1>Exports</h1><p>Download packages with every move, prompt, response and replay file. A game’s package is made when it finishes. Campaign snapshots are prepared from the campaign page and hold the finished games available at that moment.</p></div>
      </header>
      <div className="cb-toolbar">
        <nav className="cb-segmented" aria-label="Filter exports">
          {FILTERS.map(f => <a key={f.label} href={f.param ? `/exports?type=${f.param}` : '/exports'} aria-current={f === filter ? 'page' : undefined}>{f.label}</a>)}
        </nav>
        <label className="cb-search"><span className="cb-sr">Search exports</span><input className="cb-input" type="search" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search by name, run or campaign" /></label>
      </div>
      {error ? <p className="cb-error" role="alert">Couldn’t load exports: {error}</p> : null}
      {!data && !error ? <p className="cb-meta" role="status">Loading…</p> : null}
      {data && items.length === 0 ? <div className="cb-empty">
        <h2>{needle ? `No exports match “${search.trim()}”` : data.length ? `No ${filter.label.toLowerCase()} exports yet` : 'No exports yet'}</h2>
        {!needle ? <p>Finished games are packaged automatically. For a campaign, open it and choose Prepare snapshot.</p> : null}
      </div> : null}
      {items.length ? <div className="cb-export-list"><ul className="cb-rows" aria-label={`${items.length} ${items.length === 1 ? 'export' : 'exports'}`}>
        {items.map(item => {
          const source = exportSource(item)
          const name = exportName(item)
          return <li key={item.export_id}>
            <span className="cb-row-main">
              <strong>{name}</strong>
              <span className="cb-meta">{[exportKindLabel(item), fileSize(item.bytes), when(item.created_at), item.scope === 'campaign' ? `Revision ${item.revision}` : item.run_id ? `Run ${item.run_id}` : null].filter(Boolean).join(' · ')}</span>
              {item.scope === 'campaign' ? <span className="cb-meta">Snapshot: includes finished games and the campaign manifest. Games still playing or not started aren’t included in full.</span> : null}
            </span>
            {source ? <a className="cb-btn cb-btn-ghost" href={source.href}>{source.label}</a> : null}
            <a className="cb-btn cb-btn-secondary" href={exportDownload(item)} download aria-label={`Download ${name}`}>Download</a>
          </li>
        })}
      </ul></div> : null}
    </div>
  </Shell>
}
