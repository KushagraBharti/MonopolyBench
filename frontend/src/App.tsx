import { BatchDashboardPage } from '@/pages/BatchDashboardPage'
import { LiveBenchPage } from '@/pages/LiveBenchPage'
import { MicroDashboardPage } from '@/pages/MicroDashboardPage'
import { MicroSuitePage } from '@/pages/MicroSuitePage'
import { ModelDetailPage } from '@/pages/ModelDetailPage'
import { ResearchArtifactsPage } from '@/pages/ResearchArtifactsPage'
import { ReplayReviewPage } from '@/pages/ReplayReviewPage'
import { RunsPage } from '@/pages/RunsPage'
import { GamesPage, LoginPage, GamePage, TestsPage } from '@/pages/CloudPages'
import { CampaignsRoute } from '@/pages/cloud/CampaignPages'
import { CreateCampaignPage } from '@/pages/cloud/CreateCampaignPage'
import { NewGamePage } from '@/pages/cloud/NewGamePage'
import { DashboardPage } from '@/pages/cloud/DashboardPage'
import { ExportsPage } from '@/pages/cloud/ExportsPage'

function App() {
  if (import.meta.env.VITE_MB_MODE === 'cloud') {
    const path = window.location.pathname.replace(/(.)\/+$/, '$1')
    if (path === '/login') return <LoginPage />
    if (path === '/' || path === '/dashboard') {
      // Old bookmarks filtered games on the root page; keep them working under Games.
      const legacy = new URLSearchParams(window.location.search)
      if (path === '/' && (legacy.has('status') || legacy.has('archived'))) {
        window.location.replace(`/games${window.location.search}`)
        return null
      }
      return <DashboardPage />
    }
    if (path === '/games') return <GamesPage />
    if (path === '/games/new') return <NewGamePage />
    if (path.startsWith('/games/')) return <GamePage />
    if (path === '/tests') return <TestsPage />
    if (path === '/tests/new') return <NewGamePage mode="smoke" />
    if (path === '/exports') return <ExportsPage />
    if (path === '/campaigns/new') return <CreateCampaignPage />
    if (path === '/campaigns' || path.startsWith('/campaigns/')) return <CampaignsRoute />
  }
  if (window.location.pathname.startsWith('/runs/') && (
    window.location.pathname.endsWith('/replay') || window.location.pathname.endsWith('/review')
  )) {
    return <ReplayReviewPage />
  }
  if (window.location.pathname === '/runs' || window.location.pathname.startsWith('/runs/')) {
    return <RunsPage />
  }
  if (window.location.pathname.startsWith('/models/')) {
    return <ModelDetailPage />
  }
  if (window.location.pathname === '/batches' || window.location.pathname.startsWith('/batches/')) {
    return <BatchDashboardPage />
  }
  if (window.location.pathname === '/research' || window.location.pathname.startsWith('/research/')) {
    return <ResearchArtifactsPage />
  }
  if (window.location.pathname.startsWith('/micro/detail')) {
    return <MicroSuitePage />
  }
  if (window.location.pathname === '/micro' || window.location.pathname === '/micro/') {
    return <MicroDashboardPage />
  }
  return <LiveBenchPage />
}

export default App
