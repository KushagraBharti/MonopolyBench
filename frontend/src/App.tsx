import { useEffect, useMemo, useRef, useState } from 'react';
import { getApiBaseUrl, getWsUrl, WsClient } from '@/net/ws';
import { useGameStore } from '@/state/store';
import { Board } from '@/components/board/Board';
import { BoardEffectsLayer } from '@/components/board/BoardEffectsLayer';
import { PlayerStackPanel } from '@/components/panels/PlayerStackPanel';
import { EventFeed } from '@/components/feed/EventFeed';
import { ChatFeed } from '@/components/feed/ChatFeed';
import { GameControls } from '@/components/panels/GameControls';
import { Inspector } from '@/components/panels/Inspector';
import { AuctionPanel } from '@/components/panels/AuctionPanel';
import { TradeInspectorPanel } from '@/components/panels/TradeInspectorPanel';
import { NeoBadge } from '@/components/ui/NeoPrimitive';
import { cn } from '@/components/ui/cn';
import { GO_INDEX, JAIL_INDEX } from '@/domain/monopoly/constants';
import type { Event } from '@/net/contracts';

function App() {
  const setStatus = useGameStore((state) => state.setStatus);
  const setSnapshot = useGameStore((state) => state.setSnapshot);
  const pushEvent = useGameStore((state) => state.pushEvent);
  const setRunStatus = useGameStore((state) => state.setRunStatus);
  const setEventHighlight = useGameStore((state) => state.setEventHighlight);
  const snapshot = useGameStore((state) => state.snapshot);
  const connection = useGameStore((state) => state.connection);
  const runStatus = useGameStore((state) => state.runStatus);
  const logResetId = useGameStore((state) => state.logResetId);
  const latestEvent = useGameStore((state) => state.events[0]);
  const apiBase = useMemo(() => getApiBaseUrl(), []);
  const highlightTimerRef = useRef<number | null>(null);
  const [rightTab, setRightTab] = useState<'dev' | 'feed'>('dev');

  const runState = useMemo(() => {
    if (runStatus.running && runStatus.paused) return 'PAUSED';
    if (runStatus.running) return 'RUNNING';
    if (runStatus.runId) return 'COMPLETE';
    return 'IDLE';
  }, [runStatus.running, runStatus.paused, runStatus.runId]);

  const showAuction = Boolean(snapshot?.auction);
  const showTrade = Boolean(snapshot?.trade);

  useEffect(() => {
    const client = new WsClient(getWsUrl(), {
      onHello: (payload) => setRunStatus({ runId: payload.run_id }),
      onSnapshot: (payload) => setSnapshot(payload),
      onEvent: (payload) => pushEvent(payload),
      onError: (payload) => setStatus('disconnected', payload.message),
      onStatusChange: (status, error) => setStatus(status, error),
    });
    client.connect();
    return () => client.close();
  }, [pushEvent, setRunStatus, setSnapshot, setStatus]);

  useEffect(() => {
    let active = true;
    const fetchStatus = async () => {
      try {
        const res = await fetch(`${apiBase}/run/status`);
        if (!res.ok) return;
        const data = (await res.json()) as {
          running: boolean;
          paused?: boolean;
          run_id: string | null;
          turn_index: number | null;
          connected_clients: number;
          players?: {
            player_id: string;
            name: string;
            model_display_name: string;
            openrouter_model_id: string;
            reasoning?: {
              effort?: string;
            };
          }[];
        };
        if (!active) return;
        setRunStatus({
          running: data.running,
          paused: data.paused ?? false,
          runId: data.run_id,
          turnIndex: data.turn_index ?? null,
          connectedClients: data.connected_clients,
          players: data.players ?? [],
        });
      } catch {
        if (!active) return;
      }
    };
    fetchStatus();
    const interval = window.setInterval(fetchStatus, 2500);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, [apiBase, setRunStatus]);

  useEffect(() => {
    if (!latestEvent) return;
    const highlightIndices = getHighlightIndices(latestEvent);
    if (!highlightIndices.length) return;
    setEventHighlight(highlightIndices);
    if (highlightTimerRef.current) {
      window.clearTimeout(highlightTimerRef.current);
    }
    highlightTimerRef.current = window.setTimeout(() => {
      setEventHighlight(null);
    }, 1400);
    return () => {
      if (highlightTimerRef.current) {
        window.clearTimeout(highlightTimerRef.current);
      }
    };
  }, [latestEvent, setEventHighlight]);

  // Status Derivation
  const isConnected = connection.status === 'connected';
  const runBadgeLabel =
    runState === 'RUNNING' ? 'RUNNING' : runState === 'PAUSED' ? 'PAUSED' : runState === 'COMPLETE' ? 'COMPLETE' : 'IDLE';

  return (
    <div className="h-screen w-screen bg-neo-bg text-black font-sans overflow-hidden flex relative">

      {/* Sidebar: Left Panel (Players & Controls & Ownership) */}
      <aside className="w-137.5 h-full border-r-2 border-black bg-white flex flex-col z-30 shadow-[4px_0_16px_rgba(0,0,0,0.06)]">
        <header className="px-3 py-2.5 border-b-2 border-black bg-neo-bg/60 shrink-0">
          <div className="flex items-center justify-between">
            <h1 className="text-base font-black uppercase tracking-tighter leading-none">
              Monopoly<span className="text-neo-pink ml-0.5">Bench</span>
            </h1>
            <div className="flex items-center gap-1.5">
              <span className={cn(
                "w-2 h-2 rounded-full transition-colors duration-300",
                isConnected ? "bg-neo-green" : "bg-neo-pink animate-pulse"
              )} />
              <NeoBadge
                variant={
                  runState === 'RUNNING' ? 'info' :
                    runState === 'PAUSED' ? 'warning' :
                      runState === 'COMPLETE' ? 'success' :
                        'neutral'
                }
                className="text-[8px] py-0 px-1.5"
              >
                {runBadgeLabel}
              </NeoBadge>
            </div>
          </div>
        </header>

        <div className="flex-1 flex flex-col min-h-0 bg-neo-bg/30">
          {/* Controls - Fixed */}
          <div className="shrink-0 p-2 border-b border-black/10 bg-white z-10">
            <GameControls />
          </div>

          {/* Scrolling Area for Players/Auction/Trade */}
          <div className="flex-1 overflow-y-auto p-2 min-h-0 relative brutal-scroll">
            <div className="mb-2">
              <PlayerStackPanel />
            </div>
            {(showAuction || showTrade) && (
              <div className="flex flex-col gap-2 mt-2">
                <AuctionPanel visible={showAuction} />
                <TradeInspectorPanel visible={showTrade} />
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Area: Board (Centered & Scaled) */}
      <main className="flex-1 h-full relative flex items-center justify-center bg-neo-bg p-4 overflow-hidden">
        {/* Background Image */}
        <div className="absolute inset-0 pointer-events-none"
          style={{
            backgroundImage: 'url(/background.png)',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        />

        <Board spaces={snapshot?.board || []} className="h-full max-h-[95vh] w-auto aspect-square relative z-10" />
        <BoardEffectsLayer />
      </main>

      {/* Right Sidebar: Feed */}
      <aside className="w-96 h-full border-l-2 border-black bg-white flex flex-col z-20 shadow-[-4px_0_16px_rgba(0,0,0,0.06)]">
        <div className="px-3 py-2.5 border-b-2 border-black flex justify-between items-center bg-neo-bg/60">
          <div className="flex items-center gap-1">
            {(['dev', 'feed'] as const).map((tab) => (
              <button
                key={tab}
                type="button"
                onClick={() => setRightTab(tab)}
                className={cn(
                  "px-3 py-1 text-[10px] font-bold uppercase border-[1.5px] border-black rounded-[2px] transition-all duration-100 select-none",
                  rightTab === tab
                    ? "bg-black text-white shadow-none"
                    : "bg-white text-black shadow-neo-sm hover:-translate-y-px hover:shadow-neo"
                )}
              >
                {tab === 'dev' ? 'Events' : 'Feed'}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[9px] font-bold uppercase text-gray-400 tracking-wide">Turn</span>
            <span className="text-lg font-mono font-black leading-none tabular-nums">{snapshot?.turn_index ?? 0}</span>
          </div>
        </div>
        <div className="flex-1 min-h-0 relative">
          {rightTab === 'dev' ? <EventFeed /> : <ChatFeed key={`chat-${logResetId}`} />}
        </div>
      </aside>

      <Inspector />
    </div>
  );
}

export default App;

const getHighlightIndices = (event: Event): number[] => {
  switch (event.type) {
    case 'PLAYER_MOVED': {
      const indices = [event.payload.to];
      if (event.payload.passed_go) {
        indices.push(GO_INDEX);
      }
      return indices;
    }
    case 'PROPERTY_PURCHASED':
      return [event.payload.space_index];
    case 'PROPERTY_TRANSFERRED':
      return [event.payload.space_index];
    case 'RENT_PAID':
      return [event.payload.space_index];
    case 'SENT_TO_JAIL':
      return [JAIL_INDEX];
    default:
      return [];
  }
};
