import { useEffect, useRef, useState, useSyncExternalStore } from 'react';
import type { Event, StateSnapshot } from '@/net/contracts';
import { BoardScene } from './scene';
import { PresentationCursor } from './presentation';
import './board3d.css';

const subscribeMotion = (change: () => void) => {
  const query = window.matchMedia('(prefers-reduced-motion: reduce)');
  query.addEventListener('change', change); return () => query.removeEventListener('change', change);
};
const reducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

export interface Board3DProps {
  snapshot: StateSnapshot | null;
  events: readonly Event[];
  resetKey: string | number;
  animate: boolean;
  onFailure: () => void;
  highlightIndex?: number | null;
}

export default function Board3D({ snapshot, events, resetKey, animate, onFailure, highlightIndex }: Board3DProps) {
  const host = useRef<HTMLDivElement>(null);
  const scene = useRef<BoardScene | null>(null);
  const cursor = useRef(new PresentationCursor());
  const latest = useRef({ snapshot, events, resetKey, animate });
  const [ready, setReady] = useState(false);
  const [selected, setSelected] = useState<number | null>(null);
  const [motion, setMotion] = useState(true);
  const reduced = useSyncExternalStore(subscribeMotion, reducedMotion, () => true);
  const allowMotion = animate && motion && !reduced;

  useEffect(() => { latest.current = { snapshot, events, resetKey, animate: allowMotion }; }, [snapshot, events, resetKey, allowMotion]);
  useEffect(() => {
    if (!host.current) return;
    let active = true;
    let board: BoardScene;
    try { board = new BoardScene(host.current, setSelected, onFailure); }
    catch { onFailure(); return; }
    scene.current = board;
    cursor.current = new PresentationCursor();
    board.load().then(() => {
      if (!active) return;
      const data = latest.current;
      board.update(cursor.current.accept(data.snapshot, data.events, data.resetKey, data.animate));
      setReady(true);
    }).catch(() => { if (active) onFailure(); });
    return () => { active = false; board.dispose(); scene.current = null; };
  }, [onFailure]);
  useEffect(() => {
    if (!ready) return;
    scene.current?.update(cursor.current.accept(snapshot, events, resetKey, allowMotion));
  }, [snapshot, events, resetKey, allowMotion, ready]);
  useEffect(() => { if (ready) scene.current?.focus(selected ?? highlightIndex ?? null); }, [selected, highlightIndex, ready]);

  const space = snapshot?.board.find(s => s.index === selected);
  const owner = snapshot?.players.find(p => p.player_id === space?.owner_id);
  return <div className="board3d" data-board-root="true" data-view="3d">
    <div className="board3d-canvas" ref={host} data-scene-ready={ready} />
    {!ready && <div className="board3d-loading" role="status"><span className="board3d-spinner" /><strong>Building the city…</strong><span>Loading the board and its pieces</span></div>}
    <div className="board3d-tools" aria-label="3D camera controls">
      <button type="button" onClick={() => scene.current?.resetCamera()} disabled={!ready}>Reset view</button>
      <button type="button" onClick={() => scene.current?.resetCamera(true)} disabled={!ready}>Overhead</button>
      <button type="button" onClick={() => setMotion(v => !v)} aria-pressed={motion && !reduced} disabled={reduced} title={reduced ? 'Reduced motion follows your system preference' : undefined}>Motion {motion && !reduced ? 'on' : 'off'}</button>
    </div>
    <div className="board3d-inspect">
      <label htmlFor="board3d-property">Inspect a space</label>
      <select id="board3d-property" value={selected ?? ''} onChange={e => setSelected(e.target.value === '' ? null : Number(e.target.value))}>
        <option value="">Select on the board or here</option>
        {snapshot?.board.map(s => <option key={s.index} value={s.index}>{s.index.toString().padStart(2, '0')} · {s.name}</option>)}
      </select>
      {space && <div className="board3d-deed" role="status">
        <div className="board3d-deed-title"><strong>{space.name}</strong><button type="button" aria-label="Close property details" onClick={() => setSelected(null)}>×</button></div>
        <dl><div><dt>Owner</dt><dd>{owner?.name ?? 'Unowned'}</dd></div>
          {space.price !== null && <div><dt>Price</dt><dd>${space.price}</dd></div>}
          {space.kind === 'PROPERTY' && <div><dt>Development</dt><dd>{space.hotel ? 'Hotel' : `${space.houses} house${space.houses === 1 ? '' : 's'}`}</dd></div>}
          {space.mortgaged && <div><dt>Status</dt><dd>Mortgaged</dd></div>}
        </dl>
      </div>}
    </div>
    <p className="board3d-hint">Drag to orbit · Scroll to zoom · Select a space</p>
  </div>;
}
