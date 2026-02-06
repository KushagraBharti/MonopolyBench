import type { Space } from '@/net/contracts';
import { getPlayerColor, getPlayerInitials } from '@/domain/monopoly/colors';
import { NeoCard } from '@/components/ui/NeoPrimitive';
import { cn } from '@/components/ui/cn';
import { PropertyChip } from '@/components/panels/PropertyChip';

const formatMoney = (value: number): string => {
  return value.toLocaleString('en-US');
};

type PlayerCardProps = {
  playerId: string;
  name: string;
  modelId: string | null;
  cash: number;
  propertyCount: number;
  netWorth: number;
  inJail: boolean;
  bankrupt: boolean;
  isActive: boolean;
  properties: Space[];
  deedHighlight: number | null;
  onToggleHighlight: (index: number) => void;
  latestThought: string | null;
};

export const PlayerCard = ({
  playerId,
  name,
  modelId,
  cash,
  propertyCount,
  netWorth,
  inJail,
  bankrupt,
  isActive,
  properties,
  deedHighlight,
  onToggleHighlight,
  latestThought,
}: PlayerCardProps) => {
  const badgeColor = getPlayerColor(playerId);

  return (
    <NeoCard
      data-player-card-id={playerId}
      className={cn(
        'p-2.5 flex flex-col gap-1.5 h-full transition-colors duration-200',
        isActive
          ? 'bg-neo-yellow/15 border-neo-yellow/60 shadow-[2px_2px_0_0_rgba(255,217,0,0.3)]'
          : bankrupt
            ? 'bg-gray-50 opacity-60'
            : 'bg-white'
      )}
    >
      {/* Header: Name + Status */}
      <div className="flex items-center justify-between gap-1.5">
        <div className="flex items-center gap-1.5 min-w-0">
          <div
            className="w-3 h-3 rounded-[2px] border-[1.5px] border-black shrink-0"
            style={{ backgroundColor: badgeColor }}
            title={`Player ${playerId}`}
          />
          <div className="min-w-0">
            <div className={cn('text-[11px] font-black uppercase truncate leading-tight', bankrupt && 'line-through')}>
              {name || getPlayerInitials(playerId)}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-1 shrink-0">
          {isActive && (
            <span className="text-[8px] font-bold uppercase text-neo-blue bg-neo-blue/10 px-1 py-px rounded-[2px]">Active</span>
          )}
          {inJail && (
            <span className="text-[8px] font-bold uppercase text-neo-orange bg-neo-orange/10 px-1 py-px rounded-[2px]">Jail</span>
          )}
          {bankrupt && (
            <span className="text-[8px] font-bold uppercase text-neo-red bg-neo-red/10 px-1 py-px rounded-[2px]">Out</span>
          )}
        </div>
      </div>

      {/* Model ID */}
      <div className="text-[9px] text-gray-400 font-mono truncate leading-none -mt-0.5">
        {modelId ?? 'model unknown'}
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-3 gap-1 bg-neo-bg/60 rounded-[2px] px-1.5 py-1">
        <div className="flex flex-col">
          <span className="text-[8px] uppercase tracking-wide text-gray-400 leading-none">Cash</span>
          <span className="font-mono text-[11px] font-bold text-black tabular-nums">${formatMoney(cash)}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-[8px] uppercase tracking-wide text-gray-400 leading-none">Props</span>
          <span className="font-mono text-[11px] font-bold text-black tabular-nums">{propertyCount}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-[8px] uppercase tracking-wide text-gray-400 leading-none">Net</span>
          <span
            className="font-mono text-[11px] font-bold text-black tabular-nums"
            title="Net worth = cash + sum(price) - sum(price/2 for mortgaged)"
          >
            ${formatMoney(netWorth)}
          </span>
        </div>
      </div>

      {/* Properties */}
      <div className="flex flex-col gap-0.5">
        <span className="text-[8px] uppercase tracking-wide text-gray-400">Properties</span>
        <div className="flex flex-wrap gap-0.5">
          {properties.length > 0 ? (
            properties.map((space) => (
              <PropertyChip
                key={space.index}
                space={space}
                isSelected={deedHighlight === space.index}
                onSelect={() => onToggleHighlight(space.index)}
              />
            ))
          ) : (
            <span className="text-[9px] text-gray-400 italic">None</span>
          )}
        </div>
      </div>

      {/* Latest Thought */}
      <div className="flex flex-col gap-0.5 border-t border-black/5 pt-1.5 mt-auto">
        <span className="text-[8px] uppercase tracking-wide text-gray-400">Thought</span>
        <div className="text-[10px] text-gray-600 min-h-[14px] whitespace-pre-wrap leading-snug line-clamp-3">
          {latestThought ?? <span className="text-gray-300 italic">...</span>}
        </div>
      </div>
    </NeoCard>
  );
};
