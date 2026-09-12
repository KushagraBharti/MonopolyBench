import { Component, lazy, Suspense, useCallback, useState } from 'react';
import type { ReactNode } from 'react';
import type { Event, StateSnapshot } from '@/net/contracts';
import { Board } from '@/components/board/Board';
import { cn } from '@/components/ui/cn';
import './board3d.css';

const Board3D = lazy(() => import('./Board3D'));
const NO_EVENTS: readonly Event[] = [];
class BoardLoadBoundary extends Component<{ children: ReactNode; onFailure: () => void }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch() { this.props.onFailure(); }
  render() { return this.state.failed ? null : this.props.children; }
}
type Props = {
  snapshot: StateSnapshot | null;
  events?: readonly Event[];
  resetKey?: string | number;
  animate?: boolean;
  highlightIndex?: number | null;
  className?: string;
  flatEffects?: ReactNode;
};

export function BoardViewport({ snapshot, events = NO_EVENTS, resetKey = 'live', animate = true, highlightIndex, className, flatEffects }: Props) {
  const [mode, setMode] = useState<'3d' | 'flat'>(() => {
    try { return window.localStorage.getItem('monopolybench.board-view.v1') === 'flat' ? 'flat' : '3d'; } catch { return '3d'; }
  });
  const [failed, setFailed] = useState(false);
  const handleFailure = useCallback(() => { setFailed(true); setMode('flat'); }, []);
  const choose = (next: '3d' | 'flat') => {
    setMode(next); setFailed(false);
    try { window.localStorage.setItem('monopolybench.board-view.v1', next); } catch { /* Private browsing still supports the current selection. */ }
  };
  return <section className={cn('board-viewport', className)} aria-label="Game board">
    <div className="board-view-toggle" aria-label="Board view">
      <button type="button" aria-pressed={mode === '3d'} onClick={() => choose('3d')}>3D city</button>
      <button type="button" aria-pressed={mode === 'flat'} onClick={() => choose('flat')}>Classic</button>
    </div>
    {mode === '3d' ? <BoardLoadBoundary onFailure={handleFailure}><Suspense fallback={<div className="board3d-loading" role="status">Loading 3D board…</div>}>
      <Board3D snapshot={snapshot} events={events} resetKey={resetKey} animate={animate} highlightIndex={highlightIndex} onFailure={handleFailure} />
    </Suspense></BoardLoadBoundary> : <>
      {failed && <p className="board3d-fallback" role="status">3D couldn’t load. The classic board is ready; you can retry 3D above.</p>}
      <div className={cn('board-flat-stage', failed && 'board-flat-stage-fallback')}>
        <Board spaces={snapshot?.board ?? []} players={snapshot?.players ?? []} activePlayerId={snapshot?.active_player_id ?? null} highlightState={{ eventHighlight: highlightIndex == null ? null : [highlightIndex] }} className="board-flat" />
      </div>
      {flatEffects}
    </>}
  </section>;
}
