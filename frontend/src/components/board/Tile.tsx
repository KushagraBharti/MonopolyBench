import { memo, type ReactNode } from 'react';
import type { Space } from '@/net/contracts';
import { cn } from '@/components/ui/cn';
import { getGroupColor, getPlayerColor } from '@/domain/monopoly/colors';
import { getBoardSide } from '@/components/board/utils';
import './board.css';

interface TileProps {
  space: Space;
  className?: string;
  highlightSource?: 'deed' | 'event' | 'decision' | null;
  /** Display name for the owner, used in the accessible label. */
  ownerName?: string | null;
}

const icon = (paths: ReactNode, filled = false) => (
  <svg viewBox="0 0 24 24" className="mb-tile-icon" aria-hidden="true" fill={filled ? 'currentColor' : 'none'} stroke={filled ? 'none' : 'currentColor'} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    {paths}
  </svg>
);

const TrainIcon = () => icon(<><rect x="5" y="3" width="14" height="13" rx="2" /><path d="M5 10h14M9 20l-2 2M15 20l2 2" /><circle cx="9" cy="13" r=".8" fill="currentColor" /><circle cx="15" cy="13" r=".8" fill="currentColor" /></>);
const BulbIcon = () => icon(<><path d="M9 18h6M10 21h4" /><path d="M12 3a6 6 0 00-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0012 3z" /></>);
const WaterIcon = () => icon(<path d="M12 3s6 6.5 6 11a6 6 0 01-12 0c0-4.5 6-11 6-11z" />);
const ChestIcon = () => icon(<><rect x="3" y="8" width="18" height="12" rx="1.5" /><path d="M3 12h18M5 8V6a2 2 0 012-2h10a2 2 0 012 2v2" /><rect x="10.5" y="11" width="3" height="3" fill="currentColor" /></>);
const ChanceIcon = () => (
  <span className="mb-tile-glyph" aria-hidden="true">?</span>
);
const TaxIcon = () => icon(<><path d="M12 3v18" /><path d="M17 7.5C17 5.6 14.8 4.5 12 4.5S7 5.6 7 7.6c0 4.5 10 2.6 10 7.4 0 2-2.2 3.5-5 3.5s-5-1.4-5-3.4" /></>);

const formatPrice = (price: number) => `$${price}`;

const ownerLabel = (space: Space, ownerName?: string | null) => {
  const parts = [space.name];
  if (space.price !== null && !space.owner_id) parts.push(`unowned, price ${formatPrice(space.price)}`);
  if (space.owner_id) parts.push(`owned by ${ownerName ?? space.owner_id}`);
  if (space.hotel) parts.push('hotel');
  else if (space.houses > 0) parts.push(`${space.houses} house${space.houses === 1 ? '' : 's'}`);
  if (space.mortgaged) parts.push('mortgaged');
  return parts.join(', ');
};

const Corner = ({ space }: { space: Space }) => {
  if (space.index === 0) {
    return (
      <div className="mb-corner mb-corner-go">
        <span className="mb-corner-small">Collect $200 salary as you pass</span>
        <span className="mb-corner-big">GO</span>
        <svg viewBox="0 0 48 16" className="mb-go-arrow" aria-hidden="true"><path d="M46 8H6M14 1L4 8l10 7" fill="none" stroke="currentColor" strokeWidth="3" strokeLinejoin="round" /></svg>
      </div>
    );
  }
  if (space.index === 10) {
    return (
      <div className="mb-corner mb-corner-jail">
        <div className="mb-jail-cell"><span>In jail</span></div>
        <span className="mb-jail-just">Just</span>
        <span className="mb-jail-visiting">Visiting</span>
      </div>
    );
  }
  if (space.index === 20) {
    return (
      <div className="mb-corner mb-corner-parking">
        <span className="mb-corner-small">Free</span>
        <svg viewBox="0 0 24 24" className="mb-corner-icon" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"><path d="M4 15l2-6h12l2 6v3H4z" /><circle cx="8" cy="18" r="1.6" fill="currentColor" /><circle cx="16" cy="18" r="1.6" fill="currentColor" /></svg>
        <span className="mb-corner-small">Parking</span>
      </div>
    );
  }
  return (
    <div className="mb-corner mb-corner-gotojail">
      <span className="mb-corner-small">Go to</span>
      <svg viewBox="0 0 24 24" className="mb-corner-icon" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2"><rect x="4" y="3" width="16" height="18" rx="1.5" /><path d="M8 3v18M12 3v18M16 3v18" /></svg>
      <span className="mb-corner-small">Jail</span>
    </div>
  );
};

/**
 * One board square. Renders only what the snapshot says: owner, houses, the hotel flag
 * and the mortgage flag. Color bands face the board center, like a printed board.
 */
export const Tile = memo(({ space, className, highlightSource = null, ownerName }: TileProps) => {
  const { name, kind, price, group, owner_id, houses, hotel, mortgaged } = space;
  const side = getBoardSide(space.index);
  const groupColor = getGroupColor(group);
  const isStreet = kind === 'PROPERTY' && groupColor !== 'transparent';

  if (side === 'corner') {
    return (
      <div className={cn('mb-tile', className)} data-side="corner" data-highlight={highlightSource ?? undefined} title={name} role="img" aria-label={name}>
        <Corner space={space} />
      </div>
    );
  }

  const upper = name.toUpperCase();
  const glyph = kind === 'RAILROAD' ? <TrainIcon />
    : kind === 'UTILITY' ? (upper.includes('WATER') ? <WaterIcon /> : <BulbIcon />)
    : kind === 'COMMUNITY_CHEST' ? <ChestIcon />
    : kind === 'CHANCE' ? <ChanceIcon />
    : kind === 'TAX' ? <TaxIcon />
    : null;

  return (
    <div
      className={cn('mb-tile', className)}
      data-side={side}
      data-kind={kind}
      data-highlight={highlightSource ?? undefined}
      data-mortgaged={mortgaged || undefined}
      data-owned={Boolean(owner_id) || undefined}
      title={ownerLabel(space, ownerName)}
      role="img"
      aria-label={ownerLabel(space, ownerName)}
    >
      {isStreet ? (
        <div className="mb-tile-band" style={{ backgroundColor: groupColor }}>
          {hotel ? (
            <span className="mb-hotel" aria-hidden="true" />
          ) : (
            Array.from({ length: houses }).map((_, i) => <span key={i} className="mb-house" aria-hidden="true" />)
          )}
        </div>
      ) : null}
      <div className="mb-tile-body">
        <span className="mb-tile-name">{name}</span>
        {glyph}
        {price !== null && !owner_id ? <span className="mb-tile-price">{formatPrice(price)}</span> : null}
      </div>
      {owner_id ? <div className="mb-tile-owner" style={{ backgroundColor: getPlayerColor(owner_id) }} aria-hidden="true" /> : null}
      {mortgaged ? <div className="mb-tile-mortgage" aria-hidden="true"><span>Mortgaged</span></div> : null}
    </div>
  );
});

Tile.displayName = 'Tile';
