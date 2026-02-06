import { useEffect, useMemo, useState } from 'react';
import { useGameStore } from '@/state/store';
import { NeoBadge } from '@/components/ui/NeoPrimitive';
import { cn } from '@/components/ui/cn';
import { LlmIoPanel } from '@/components/panels/LlmIoPanel';

type Tab = 'snapshot' | 'last' | 'stream' | 'raw' | 'llm_io';

const JsonPane = ({ title, data }: { title: string; data: unknown }) => (
  <div className="flex flex-col gap-1 h-full min-h-0">
    <div className="flex items-center justify-between border-b border-black/15 bg-neo-bg px-2.5 py-1.5">
      <span className="text-[10px] uppercase font-black tracking-wider text-gray-700">{title}</span>
      <button
        onClick={() => navigator.clipboard.writeText(JSON.stringify(data, null, 2))}
        className="text-[9px] font-mono text-gray-400 hover:text-neo-blue uppercase transition-colors"
      >
        Copy
      </button>
    </div>
    <div className="flex-1 overflow-auto bg-white p-2.5 font-mono text-[10px] brutal-scroll leading-relaxed">
      <pre className="text-gray-700">{JSON.stringify(data, null, 2)}</pre>
    </div>
  </div>
);

const ToggleSwitch = ({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) => (
  <button
    onClick={onClick}
    className={cn(
      "relative px-3 py-1 min-w-[70px] text-[10px] font-bold uppercase transition-all duration-100 border-[1.5px] rounded-[2px] select-none",
      active
        ? "bg-black text-white border-black shadow-none translate-y-[1px]"
        : "bg-white text-gray-700 border-black/40 hover:border-black/70 shadow-[2px_2px_0_0_rgba(0,0,0,0.15)] hover:shadow-[2px_2px_0_0_rgba(0,0,0,0.25)]"
    )}
  >
    {label}
  </button>
);

export const Inspector = () => {
  const [showThoughts, setShowThoughts] = useState(false);

  const snapshot = useGameStore((state) => state.snapshot);
  const previousSnapshot = useGameStore((state) => state.previousSnapshot);
  const events = useGameStore((state) => state.events);
  const connection = useGameStore((state) => state.connection);
  const runStatus = useGameStore((state) => state.runStatus);
  const inspectorOpen = useGameStore((state) => state.inspectorOpen);
  const inspectorTab = useGameStore((state) => state.inspectorTab);
  const inspectorFocus = useGameStore((state) => state.inspectorFocus);
  const setInspectorOpen = useGameStore((state) => state.setInspectorOpen);
  const setInspectorTab = useGameStore((state) => state.setInspectorTab);
  const setInspectorFocus = useGameStore((state) => state.setInspectorFocus);
  const setLlmIoSelectedDecisionId = useGameStore((state) => state.setLlmIoSelectedDecisionId);

  const lastEvent = events.length > 0 ? events[0] : null;
  const streamEvents = useMemo(() => {
    const filtered = showThoughts ? events : events.filter((e) => e.type !== 'LLM_PRIVATE_THOUGHT');
    return filtered.slice(0, 100);
  }, [events, showThoughts]);

  useEffect(() => {
    if (inspectorFocus) {
      setInspectorOpen(true);
      if (inspectorFocus.decisionId) {
        setInspectorTab('llm_io');
        setLlmIoSelectedDecisionId(inspectorFocus.decisionId);
      } else {
        setInspectorTab('stream');
      }
    }
  }, [inspectorFocus, setInspectorOpen, setInspectorTab, setLlmIoSelectedDecisionId]);

  const focusLabel = useMemo(() => {
    if (!inspectorFocus) return null;
    if (inspectorFocus.decisionId) return `Decision ${inspectorFocus.decisionId}`;
    if (inspectorFocus.eventId) return `Event ${inspectorFocus.eventId}`;
    if (inspectorFocus.eventIndex !== undefined) return `Event #${inspectorFocus.eventIndex}`;
    return null;
  }, [inspectorFocus]);

  const runId = runStatus.runId ?? 'none';

  const getDecisionId = (event: typeof events[number]) => {
    const payload = event.payload as Record<string, unknown> | null | undefined;
    const decisionId = payload?.decision_id;
    return typeof decisionId === 'string' ? decisionId : null;
  };

  const getThoughtText = (event: typeof events[number]) => {
    const payload = event.payload as Record<string, unknown> | null | undefined;
    const thought = payload?.thought;
    return typeof thought === 'string' ? thought : '';
  };

  const matchesFocus = (event: typeof events[number]) => {
    if (!inspectorFocus) return false;
    if (inspectorFocus.eventId && event.event_id === inspectorFocus.eventId) return true;
    if (inspectorFocus.decisionId) {
      const decisionId = getDecisionId(event);
      return decisionId === inspectorFocus.decisionId;
    }
    return false;
  };

  if (!inspectorOpen) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={() => setInspectorOpen(true)}
          className="w-10 h-10 bg-black/90 border-[1.5px] border-white/20 text-white shadow-[3px_3px_0_0_rgba(0,0,0,0.4)] rounded-[3px] hover:rotate-90 transition-transform duration-300 flex items-center justify-center"
          title="Open Inspector"
        >
          <span className="font-mono text-lg">⚙</span>
        </button>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-end sm:items-center justify-center bg-black/40 backdrop-blur-[3px] p-2 md:p-4 animate-fade-in-up">
      <div className="w-full max-w-[98vw] md:max-w-[92vw] h-[92vh] md:h-[94vh] flex flex-col bg-neo-bg border-2 border-black/90 shadow-[10px_10px_0px_0px_rgba(0,0,0,0.85)] rounded-[3px] relative overflow-hidden">

        {/* Header Bar */}
        <div className="h-11 bg-black text-white flex justify-between items-center px-4 select-none shrink-0">
          <div className="flex items-center gap-3">
            <h2 className="text-[14px] font-black uppercase tracking-tight">System Inspector</h2>
            <div className="hidden md:block h-5 w-px bg-white/20" />
            <div className="hidden md:flex font-mono text-[9px] text-gray-500 gap-3">
              <span>RUN: {snapshot?.run_id?.slice(0, 8) ?? 'N/A'}</span>
              <span>TURN: {snapshot?.turn_index ?? 0}</span>
              <span>SCHEMA: {snapshot?.schema_version ?? '1.0'}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {focusLabel && (
              <NeoBadge variant="info" className="text-[9px] py-0 px-2">
                {focusLabel}
              </NeoBadge>
            )}
            {runStatus.players && runStatus.players.length > 0 && runStatus.players.length !== 4 && (
              <NeoBadge variant="warning" className="text-[9px] py-0 px-2">
                PLAYERS {runStatus.players.length}/4
              </NeoBadge>
            )}
            <button
              onClick={() => {
                setInspectorOpen(false);
                setInspectorFocus(null);
              }}
              className="w-7 h-7 flex items-center justify-center bg-neo-red/90 text-white text-[11px] font-bold hover:bg-red-400 transition-colors rounded-[2px]"
            >
              X
            </button>
          </div>
        </div>

        {/* Toolbar */}
        <div className="bg-white border-b border-black/15 px-3 py-2 flex flex-wrap gap-3 items-center shrink-0">
          <div className="flex flex-wrap items-center gap-1.5 mr-auto pb-1 md:pb-0">
            {(['snapshot', 'last', 'stream', 'raw', 'llm_io'] as Tab[]).map((tab) => (
              <ToggleSwitch
                key={tab}
                label={tab === 'llm_io' ? 'LLM I/O' : tab}
                active={inspectorTab === tab}
                onClick={() => setInspectorTab(tab)}
              />
            ))}
          </div>

          {inspectorTab === 'stream' && (
            <label className="flex items-center gap-1.5 cursor-pointer font-bold text-[10px] uppercase bg-neo-bg px-2 py-1 border border-black/20 rounded-[2px] active:translate-y-[1px] select-none">
              <input
                type="checkbox"
                checked={showThoughts}
                onChange={(e) => setShowThoughts(e.target.checked)}
                className="accent-black w-3.5 h-3.5"
              />
              Show Thoughts
            </label>
          )}
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-hidden p-3 bg-neo-bg relative">
          <div className="h-full bg-white border border-black/15 rounded-[2px] overflow-hidden flex flex-col relative z-10">
            {inspectorTab === 'snapshot' && (
              <div className="flex-1 grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-black/10 overflow-hidden">
                <JsonPane title="Live State" data={snapshot ?? {}} />
                <JsonPane title="Previous State" data={previousSnapshot ?? {}} />
              </div>
            )}

            {inspectorTab === 'last' && (
              <div className="flex-1 overflow-hidden">
                <JsonPane title="Latest Event Payload" data={lastEvent ?? {}} />
              </div>
            )}

            {inspectorTab === 'stream' && (
              <div className="flex-1 flex flex-col min-h-0 bg-white">
                <div className="bg-black/90 text-white px-2.5 py-1 text-[9px] uppercase font-bold flex justify-between rounded-t-[2px]">
                  <span>Event Log (Last 100)</span>
                  <span className="text-gray-400 tabular-nums">{streamEvents.length} items</span>
                </div>
                <div className="flex-1 overflow-y-auto brutal-scroll p-0">
                  {streamEvents.length === 0 && (
                    <div className="p-8 text-center text-gray-400 font-mono text-[10px]">No events to display.</div>
                  )}
                  {streamEvents.map((event, idx) => {
                    const isThought = event.type === 'LLM_PRIVATE_THOUGHT';
                    const isFocused = matchesFocus(event);
                    return (
                      <div
                        key={`${event.event_id}-${idx}`}
                        className={cn(
                          "flex items-baseline gap-2 px-2.5 py-1.5 border-b border-gray-100/80 font-mono text-[10px] hover:bg-blue-50/50 transition-colors",
                          isThought && "bg-gray-50/60 text-gray-500 italic",
                          isFocused && "bg-neo-yellow/30"
                        )}
                      >
                        <span className="w-8 shrink-0 text-gray-400 tabular-nums">#{event.turn_index}</span>
                        <span className={cn("font-bold w-40 shrink-0 truncate", isThought ? "text-gray-400" : "text-neo-blue")}>
                          {event.type}
                        </span>
                        <span className="truncate flex-1 text-gray-500">
                          {isThought
                            ? getThoughtText(event)
                            : JSON.stringify(event.payload).slice(0, 100)}
                        </span>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {inspectorTab === 'raw' && (
              <div className="flex-1 grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-black/10 overflow-hidden">
                <JsonPane title="Websocket Connection" data={connection} />
                <JsonPane title="Runner Status" data={runStatus} />
              </div>
            )}

            {inspectorTab === 'llm_io' && (
              <div className="flex-1 min-h-0">
                <LlmIoPanel key={`llm-io-${runId}`} />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
