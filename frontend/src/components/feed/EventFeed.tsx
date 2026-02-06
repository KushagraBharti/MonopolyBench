import { useEffect, useMemo, useRef, useState } from 'react';
import type { Event } from '@/net/contracts';
import { useGameStore } from '@/state/store';
import { NeoBadge } from '@/components/ui/NeoPrimitive';
import { cn } from '@/components/ui/cn';
import { getPlayerColor } from '@/domain/monopoly/colors';
import {
  formatEventCard,
  formatMoney,
  formatSpaceLabel,
  type EventBadge,
  type EventCardPart,
  type EventSeverity,
} from '@/domain/monopoly/formatters';

const severityBorders: Record<EventSeverity, string> = {
  neutral: 'border-black/20',
  info: 'border-neo-blue/60',
  success: 'border-neo-green/60',
  warning: 'border-neo-yellow/70',
  danger: 'border-neo-pink/60',
};

const severityAccents: Record<EventSeverity, string> = {
  neutral: 'bg-gray-100',
  info: 'bg-neo-blue/10',
  success: 'bg-neo-green/8',
  warning: 'bg-neo-yellow/10',
  danger: 'bg-neo-pink/8',
};

const KNOWN_EVENT_TYPES = new Set<string>([
  'GAME_STARTED',
  'TURN_STARTED',
  'DICE_ROLLED',
  'PLAYER_MOVED',
  'CASH_CHANGED',
  'PROPERTY_PURCHASED',
  'RENT_PAID',
  'SENT_TO_JAIL',
  'TURN_ENDED',
  'GAME_ENDED',
  'LLM_DECISION_REQUESTED',
  'LLM_DECISION_RESPONSE',
  'LLM_PUBLIC_MESSAGE',
  'LLM_PRIVATE_THOUGHT',
]);

const PlayerName = ({ id }: { id: string }) => (
  <span
    className="font-mono font-bold px-1.5 py-px border border-black/60 text-[9px] items-center inline-flex rounded-[2px]"
    style={{ backgroundColor: getPlayerColor(id), color: 'white' }}
  >
    {id}
  </span>
);

const MoneyAmount = ({ amount, showSign }: { amount: number; showSign?: boolean }) => {
  const isNegative = amount < 0;
  return (
    <span className={cn('font-mono font-bold text-[11px]', isNegative ? 'text-neo-red' : 'text-neo-green')}>
      {formatMoney(amount, showSign)}
    </span>
  );
};

const SpaceLabel = ({ index }: { index: number }) => (
  <span className="font-mono text-[9px] border border-black/40 px-1 py-px bg-neo-bg rounded-[2px]">
    {formatSpaceLabel(index)}
  </span>
);

const Badge = ({ badge }: { badge: EventBadge }) => {
  const variant = badge.tone === 'success'
    ? 'success'
    : badge.tone === 'warning'
      ? 'warning'
      : badge.tone === 'danger'
        ? 'error'
        : badge.tone === 'info'
          ? 'info'
          : 'neutral';
  return (
    <NeoBadge variant={variant} className="text-[9px]">
      {badge.text}
    </NeoBadge>
  );
};

const renderPart = (part: EventCardPart, index: number) => {
  switch (part.kind) {
    case 'text':
      return <span key={`part-${index}`} className="font-medium">{part.value}</span>;
    case 'player':
      return <PlayerName key={`part-${index}`} id={part.playerId} />;
    case 'money':
      return (
        <MoneyAmount key={`part-${index}`} amount={part.amount} showSign={part.showSign} />
      );
    case 'space':
      return <SpaceLabel key={`part-${index}`} index={part.spaceIndex} />;
    default:
      return null;
  }
};

const ChevronIcon = ({ expanded }: { expanded: boolean }) => (
  <svg
    className={cn("w-4 h-4 transition-transform duration-200", expanded && "rotate-180")}
    viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"
  >
    <path d="M6 9l6 6 6-6" />
  </svg>
);

const EventItem = ({ event }: { event: Event }) => {
  const [expanded, setExpanded] = useState(false);
  const card = useMemo(() => formatEventCard(event), [event]);

  // "Unknown" events should look distinct but clean
  const isUnknown = !KNOWN_EVENT_TYPES.has(event.type);

  return (
    <div
      onClick={() => setExpanded(!expanded)}
      className={cn(
        'group relative cursor-pointer select-none outline-none',
        'animate-snap-in',
        card.isMinor && !expanded ? 'opacity-60 hover:opacity-100' : 'opacity-100'
      )}
    >
      <div className={cn(
        'bg-white border-[1.5px] p-2 rounded-[3px] transition-all duration-150',
        'hover:shadow-neo-sm',
        severityBorders[card.severity]
      )}>
        <div className="flex items-start gap-2">
          {/* Left: Icon */}
          <div className="flex-shrink-0 pt-px">
            <span className={cn(
              "flex items-center justify-center w-5 h-5 border-[1.5px] border-black/40 rounded-[2px] font-mono text-[10px] leading-none",
              isUnknown ? "bg-gray-100 text-gray-400" : severityAccents[card.severity]
            )}>
              {card.icon}
            </span>
          </div>

          {/* Center: Content */}
          <div className="flex-1 min-w-0 flex flex-col gap-0.5">
            <div className="flex items-baseline gap-1.5">
              <span className="font-bold text-[10px] uppercase tracking-wide leading-none text-gray-800">
                {card.title}
              </span>
              <span className="font-mono text-[8px] text-gray-300 tabular-nums">#{card.turnIndex}</span>
            </div>

            <div className="text-[11px] leading-snug flex flex-wrap gap-x-1 gap-y-0.5 items-center">
              {card.parts.map(renderPart)}
            </div>
          </div>

          {/* Right: Chevron */}
          <div className="flex-shrink-0 text-gray-300 group-hover:text-gray-600 transition-colors self-start pt-0.5">
            <ChevronIcon expanded={expanded} />
          </div>
        </div>

        {/* Badges Footer */}
        {card.badges.length > 0 && (
          <div className="mt-1.5 pt-1.5 border-t border-dashed border-gray-100 flex flex-wrap gap-1">
            {card.badges.map((badge, idx) => (
              <Badge key={`${badge.text}-${idx}`} badge={badge} />
            ))}
          </div>
        )}

        {/* Expanded Details */}
        {expanded && (
          <div className="mt-2 text-[10px] font-mono">
            <div className="bg-neo-bg/80 border border-black/15 rounded-[2px] p-2 overflow-x-auto">
              <pre className="text-gray-600 whitespace-pre-wrap break-all leading-relaxed">
                {JSON.stringify(card.details, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export const EventFeed = () => {
  const events = useGameStore((state) => state.events);
  const containerRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);

  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = 0;
    }
  }, [events, autoScroll]);

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop } = e.currentTarget;
    setAutoScroll(scrollTop < 20);
  };

  return (
    <div className="flex flex-col h-full bg-white font-sans">
      {/* Resume Banner */}
      {!autoScroll && (
        <div className="absolute top-2 left-1/2 -translate-x-1/2 z-30">
          <button
            type="button"
            onClick={() => setAutoScroll(true)}
            className="brutal-btn bg-neo-yellow text-[9px] py-1 px-3 shadow-neo-sm rounded-[2px]"
          >
            RESUME LIVE
          </button>
        </div>
      )}

      <div
        ref={containerRef}
        className="flex-1 overflow-y-auto px-2 py-2 brutal-scroll space-y-1.5 pb-8"
        onScroll={handleScroll}
      >
        {events.length === 0 && (
          <div className="flex flex-col items-center justify-center pt-20 text-gray-300">
            <span className="text-3xl mb-2 opacity-40">~</span>
            <span className="text-[10px] font-bold uppercase tracking-wide">Waiting for events</span>
          </div>
        )}

        {events.map((event, index) => (
          <EventItem key={`${event.event_id}-${index}`} event={event} />
        ))}
      </div>
    </div>
  );
};
