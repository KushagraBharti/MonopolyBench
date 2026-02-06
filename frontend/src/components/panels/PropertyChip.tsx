import type { Space } from '@/net/contracts';
import { getGroupColor } from '@/domain/monopoly/colors';
import { cn } from '@/components/ui/cn';

const formatChipLabel = (name: string): string => {
  const cleaned = name
    .replace(/\b(Avenue|Street|Place|Railroad|Company|Gardens|Park|Line|Works)\b/gi, '')
    .replace(/\s+/g, ' ')
    .trim();
  const base = cleaned.length > 0 ? cleaned : name;
  const words = base.split(' ');
  const short = words.slice(0, 2).join(' ');
  return short.length > 10 ? short.slice(0, 10) : short;
};

const buildTitle = (space: Space): string => {
  const parts = [space.name];
  if (space.group) {
    parts.push(`Group: ${space.group}`);
  }
  if (space.mortgaged) {
    parts.push('Mortgaged');
  }
  if (space.hotel) {
    parts.push('Hotel');
  } else if (space.houses > 0) {
    parts.push(`Houses: ${space.houses}`);
  }
  return parts.join(' - ');
};

type PropertyChipProps = {
  space: Space;
  isSelected: boolean;
  onSelect: () => void;
};

export const PropertyChip = ({ space, isSelected, onSelect }: PropertyChipProps) => {
  const groupColor = getGroupColor(space.group);
  const label = formatChipLabel(space.name);

  return (
    <button
      type="button"
      onClick={onSelect}
      title={buildTitle(space)}
      className={cn(
        'flex items-center gap-1 px-1.5 py-0.5 rounded-[2px] border-[1.5px] text-[8px] font-bold uppercase tracking-wide transition-all duration-100',
        'bg-white text-gray-800 border-black/60 hover:border-black hover:-translate-y-px cursor-pointer select-none',
        space.mortgaged && 'opacity-50',
        isSelected && 'ring-[1.5px] ring-neo-pink border-neo-pink'
      )}
    >
      <span
        className="w-2 h-2 rounded-[1px] border-[1.5px] border-black/50 shrink-0"
        style={{ backgroundColor: groupColor }}
      />
      <span className="truncate max-w-[80px]">{label}</span>
      {space.mortgaged && <span className="text-[7px] font-black text-neo-red">M</span>}
    </button>
  );
};
