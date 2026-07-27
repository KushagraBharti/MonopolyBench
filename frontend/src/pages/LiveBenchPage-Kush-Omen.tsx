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

export const LiveBenchPage = () => {
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

  const isConnected = connection.status === 'connected';
  const runBadgeLabel =
    runState === 'RUNNING' ? 'RUNNING' : runState === 'PAUSED' ? 'PAUSED' : runState === 'COMPLETE' ? 'COMPLETE' : 'IDLE';

  return (
    <div className="relative flex min-h-screen w-full flex-col overflow-y-auto bg-neo-bg font-sans text-black lg:h-screen lg:flex-row lg:overflow-hidden">
      <aside className="z-30 flex w-full flex-col border-b-2 border-black bg-white shadow-[4px_0_16px_rgba(0,0,0,0.06)] lg:h-full lg:w-[22rem] lg:border-b-0 lg:border-r-2 2xl:w-[24rem]">
        <header className="px-3 py-2.5 border-b-2 border-black bg-neo-bg/60 shrink-0">
          <div className="flex flex-col gap-2 2xl:flex-row 2xl:items-center 2xl:justify-between">
            <div className="flex min-w-0 flex-wrap items-center gap-2">
              <h1 className="text-base font-black uppercase tracking-normal leading-none">
                Monopoly<span className="text-neo-pink ml-0.5">Bench</span>
              </h1>
              <a
                href="/micro/detail"
                className="inline-flex min-h-8 items-center px-2.5 py-1 text-[9px] font-black uppercase border-[1.5px] border-black rounded-[2px] bg-white shadow-neo-sm hover:-translate-y-px hover:shadow-neo transition-all duration-100"
              >
                Micro Suite
              </a>
              <a
                href="/batches"
                className="inline-flex min-h-8 items-center px-2.5 py-1 text-[9px] font-black uppercase border-[1.5px] border-black rounded-[2px] bg-white shadow-neo-sm hover:-translate-y-px hover:shadow-neo transition-all duration-100"
              >
                Batches
              </a>
              {runStatus.runId ? (
                <a
                  href={`/runs/${encodeURIComponent(runStatus.runId)}/replay`}
                  className="inline-flex min-h-8 items-center px-2.5 py-1 text-[9px] font-black uppercase border-[1.5px] border-black rounded-[2px] bg-white shadow-neo-sm hover:-translate-y-px hover:shadow-neo transition-all duration-100"
                >
                  Replay
                </a>
              ) : null}
            </div>
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
          <div className="shrink-0 p-2 border-b border-black/10 bg-white z-10">
            <GameControls />
          </div>

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

      <main className="relative flex min-h-[32rem] min-w-0 flex-1 items-center justify-start overflow-x-auto overflow-y-hidden bg-neo-bg p-3 brutal-scroll lg:h-full lg:justify-center lg:overflow-hidden lg:p-4">
        <div className="absolute inset-0 pointer-events-none"
          style={{
            backgroundImage: 'url(/background.png)',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        />

        <Board spaces={snapshot?.board || []} className="relative z-10 aspect-square w-full min-w-[34rem] max-w-[min(100%,calc(100vh-2rem))] lg:min-w-0" />
        <BoardEffectsLayer />
      </main>

      <aside className="z-20 flex w-full flex-col border-t-2 border-black bg-white shadow-[-4px_0_16px_rgba(0,0,0,0.06)] lg:h-full lg:w-[21rem] lg:border-l-2 lg:border-t-0 2xl:w-[23rem]">
        <div className="px-3 py-2.5 border-b-2 border-black flex justify-between items-center bg-neo-bg/60">
          <div className="flex items-center gap-1">
            {(['dev', 'feed'] as const).map((tab) => (
              <button
                key={tab}
                type="button"
                onClick={() => setRightTab(tab)}
                className={cn(
                  "min-h-8 px-3 py-1 text-[10px] font-bold uppercase border-[1.5px] border-black rounded-[2px] transition-all duration-100 select-none",
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
