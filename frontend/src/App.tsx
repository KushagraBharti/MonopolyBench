import { LiveBenchPage } from '@/pages/LiveBenchPage'
import { MicroDashboardPage } from '@/pages/MicroDashboardPage'
import { MicroSuitePage } from '@/pages/MicroSuitePage'

function App() {
  if (window.location.pathname.startsWith('/micro/detail')) {
    return <MicroSuitePage />
  }
  if (window.location.pathname === '/micro' || window.location.pathname === '/micro/') {
    return <MicroDashboardPage />
  }
  return <LiveBenchPage />
}

export default App
