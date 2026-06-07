import { useRef, useState } from 'react';
import { getApiBaseUrl } from '@/net/ws';
import { useGameStore } from '@/state/store';
import { cn } from '@/components/ui/cn';

export const GameControls = () => {
  const [loadingAction, setLoadingAction] = useState<null | 'start' | 'stop' | 'pause' | 'resume'>(null);
  const [pendingStart, setPendingStart] = useState(false);
  const [pendingResume, setPendingResume] = useState(false);
  const [maxTurns, setMaxTurns] = useState(50);
  const pendingStartRef = useRef(false);
  const pendingResumeRef = useRef(false);
  const runStatus = useGameStore((state) => state.runStatus);
  const setRunStatus = useGameStore((state) => state.setRunStatus);
  const resetLogs = useGameStore((state) => state.resetLogs);
  const apiBase = getApiBaseUrl();

  const handleStart = async () => {
    if (loadingAction || pendingStartRef.current || pendingResumeRef.current || runStatus.running) return;
    pendingStartRef.current = true;
    setPendingStart(true);
    setLoadingAction('start');
    try {
      await fetch(`${apiBase}/run/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seed: Date.now() % 100000, max_turns: maxTurns }),
      });
    } catch (e) {
      console.error(e);
      alert('Failed to start run');
    } finally {
      setLoadingAction(null);
      pendingStartRef.current = false;
      setPendingStart(false);
    }
  };

  const handleStop = async () => {
    if (loadingAction || pendingStartRef.current || pendingResumeRef.current) return;
    setLoadingAction('stop');
    resetLogs();
    setRunStatus({ running: false, paused: false });
    try {
      await fetch(`${apiBase}/run/stop`, { method: 'POST' });
    } catch (e) {
      console.error(e);
      alert('Failed to stop run');
    } finally {
      setLoadingAction(null);
    }
  };

  const handlePause = async () => {
    if (loadingAction || pendingStartRef.current || pendingResumeRef.current || !runStatus.running || runStatus.paused) return;
    setLoadingAction('pause');
    try {
      await fetch(`${apiBase}/run/pause`, { method: 'POST' });
      setRunStatus({ paused: true });
    } catch (e) {
      console.error(e);
      alert('Failed to pause run');
    } finally {
      setLoadingAction(null);
    }
  };

  const handleResume = async () => {
    if (loadingAction || pendingStartRef.current || pendingResumeRef.current || !runStatus.running || !runStatus.paused) return;
    pendingResumeRef.current = true;
    setPendingResume(true);
    setLoadingAction('resume');
    try {
      await fetch(`${apiBase}/run/resume`, { method: 'POST' });
      setRunStatus({ paused: false });
    } catch (e) {
      console.error(e);
      alert('Failed to resume run');
    } finally {
      setLoadingAction(null);
      pendingResumeRef.current = false;
      setPendingResume(false);
    }
  };

  const isRunning = runStatus.running;
  const isPaused = runStatus.paused;
  const isLoading = loadingAction !== null || pendingStart || pendingResume;

  return (
    <div className="flex flex-col gap-1.5">
      <label className="flex items-center justify-between gap-2 text-[9px] font-black uppercase tracking-[0.16em] text-gray-500">
        <span>Max Turns</span>
        <input
          type="number"
          min={1}
          step={1}
          value={maxTurns}
          disabled={isLoading || isRunning}
          onChange={(event) => {
            const value = Number.parseInt(event.target.value, 10);
            setMaxTurns(Number.isFinite(value) ? Math.max(1, value) : 50);
          }}
          className="h-7 w-16 rounded-[2px] border-[1.5px] border-black bg-white px-2 text-right text-[11px] font-black text-black shadow-neo-sm outline-none disabled:bg-gray-100 disabled:text-gray-400"
        />
      </label>
      <div className="flex items-center gap-1.5">
        <button
          onClick={handleStart}
          disabled={isLoading || isRunning}
          className={cn(
            "brutal-btn flex-1 text-[10px] px-2 py-1.5 rounded-[2px]",
            isRunning
              ? "bg-gray-100 text-gray-400 border-gray-300 shadow-none cursor-default"
              : "bg-neo-black text-white hover:bg-neutral-800"
          )}
        >
          {isRunning ? 'LIVE' : 'START'}
        </button>

        <button
          onClick={isPaused ? handleResume : handlePause}
          disabled={isLoading || !isRunning}
          className={cn(
            'brutal-btn flex-1 text-[10px] px-2 py-1.5 rounded-[2px] disabled:opacity-40 disabled:cursor-not-allowed',
            isPaused ? 'bg-neo-green text-black hover:bg-green-300' : 'bg-neo-yellow text-black hover:bg-yellow-300'
          )}
        >
          {isPaused ? 'RESUME' : 'PAUSE'}
        </button>

        <button
          onClick={handleStop}
          disabled={isLoading || !isRunning}
          className="brutal-btn text-[10px] px-2 py-1.5 rounded-[2px] bg-white hover:bg-red-50 disabled:opacity-40 disabled:cursor-not-allowed text-neo-red border-neo-red/60 hover:border-neo-red"
        >
          STOP
        </button>
      </div>
    </div>
  );
};
