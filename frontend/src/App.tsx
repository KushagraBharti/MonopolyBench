import { BatchDashboardPage } from '@/pages/BatchDashboardPage'
import { LiveBenchPage } from '@/pages/LiveBenchPage'
import { MicroDashboardPage } from '@/pages/MicroDashboardPage'
import { MicroSuitePage } from '@/pages/MicroSuitePage'
import { ModelDetailPage } from '@/pages/ModelDetailPage'
import { ReplayReviewPage } from '@/pages/ReplayReviewPage'
import { RunsPage } from '@/pages/RunsPage'

function App() {
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
  if (window.location.pathname.startsWith('/micro/detail')) {
    return <MicroSuitePage />
  }
  if (window.location.pathname === '/micro' || window.location.pathname === '/micro/') {
    return <MicroDashboardPage />
  }
  return <LiveBenchPage />
}

export default App
