import { NeoCard } from '@/components/ui/NeoPrimitive';
import { useGameStore } from '@/state/store';
import { getSpaceName, SPACE_INDEX_BY_KEY } from '@/domain/monopoly/constants';

type AuctionPanelProps = {
  visible: boolean;
};

export const AuctionPanel = ({ visible }: AuctionPanelProps) => {
  const snapshot = useGameStore((state) => state.snapshot);
  const auction = snapshot?.auction ?? null;

  if (!visible || !auction) return null;

  const playerMap = new Map(
    (snapshot?.players ?? []).map((player) => [player.player_id, player.name])
  );
  const spaceIndex = SPACE_INDEX_BY_KEY[auction.property_space_key] ?? null;
  const spaceLabel =
    spaceIndex !== null ? `${getSpaceName(spaceIndex)}` : auction.property_space_key;
  const currentLeader = auction.current_leader_player_id
    ? playerMap.get(auction.current_leader_player_id) ?? auction.current_leader_player_id
    : null;
  const currentBidder = auction.current_bidder_player_id
    ? playerMap.get(auction.current_bidder_player_id) ?? auction.current_bidder_player_id
    : null;
  const minNextBid = auction.current_high_bid + 1;
  const activeBidders = auction.active_bidders_player_ids.map(
    (playerId) => playerMap.get(playerId) ?? playerId
  );

  return (
    <NeoCard className="p-2.5 bg-white">
      <div className="flex items-center justify-between mb-1">
        <span className="text-[10px] font-black uppercase tracking-wide">Auction</span>
        <span className="text-[8px] font-bold uppercase text-neo-orange bg-neo-orange/10 px-1.5 py-px rounded-[2px]">Live</span>
      </div>
      <div className="text-[9px] font-mono text-gray-400 leading-none">
        {spaceLabel}
      </div>
      <div className="mt-2 text-[10px] space-y-1 bg-neo-bg/60 rounded-[2px] px-2 py-1.5">
        <div className="flex justify-between">
          <span className="text-[8px] uppercase text-gray-400">High Bid</span>
          <span className="font-mono font-bold tabular-nums">${auction.current_high_bid}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-[8px] uppercase text-gray-400">Min Next</span>
          <span className="font-mono font-bold tabular-nums">${minNextBid}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-[8px] uppercase text-gray-400">Leader</span>
          <span className="font-mono text-[10px]">{currentLeader ?? 'None'}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-[8px] uppercase text-gray-400">Bidder</span>
          <span className="font-mono text-[10px]">{currentBidder ?? 'Unknown'}</span>
        </div>
      </div>
      <div className="mt-1.5 pt-1.5 border-t border-black/5">
        <span className="text-[8px] uppercase text-gray-400">Active Bidders</span>
        <div className="font-mono text-[10px] mt-0.5">{activeBidders.join(', ') || 'None'}</div>
      </div>
    </NeoCard>
  );
};
