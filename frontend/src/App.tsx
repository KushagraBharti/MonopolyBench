import { BatchDashboardPage } from '@/pages/BatchDashboardPage'
import { LiveBenchPage } from '@/pages/LiveBenchPage'
import { MicroDashboardPage } from '@/pages/MicroDashboardPage'
import { MicroSuitePage } from '@/pages/MicroSuitePage'
import { ModelDetailPage } from '@/pages/ModelDetailPage'
import { ResearchArtifactsPage } from '@/pages/ResearchArtifactsPage'
import { ReplayReviewPage } from '@/pages/ReplayReviewPage'
import { RunsPage } from '@/pages/RunsPage'
import { GamesPage, LoginPage, GamePage } from '@/pages/CloudPages'
import { CampaignsRoute } from '@/pages/cloud/CampaignPages'
import { CreateCampaignPage } from '@/pages/cloud/CreateCampaignPage'

function App() {
  if (import.meta.env.VITE_MB_MODE === 'cloud') {
    if (window.location.pathname === '/login') return <LoginPage />
    if (window.location.pathname.startsWith('/games/')) return <GamePage />
    if (window.location.pathname === '/campaigns/new') return <CreateCampaignPage />
    if (window.location.pathname === '/campaigns' || window.location.pathname.startsWith('/campaigns/')) return <CampaignsRoute />
    if (window.location.pathname === '/') return <GamesPage />
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
