import { NeoCard } from '@/components/ui/NeoPrimitive';
import { getSpaceName, SPACE_INDEX_BY_KEY } from '@/domain/monopoly/constants';
import { useGameStore } from '@/state/store';

type TradeInspectorPanelProps = {
  visible: boolean;
};

export const TradeInspectorPanel = ({ visible }: TradeInspectorPanelProps) => {
  const snapshot = useGameStore((state) => state.snapshot);
  const trade = snapshot?.trade ?? null;

  if (!visible || !trade) return null;

  const playerMap = new Map(
    (snapshot?.players ?? []).map((player) => [player.player_id, player.name])
  );

  const formatPlayer = (playerId: string | null | undefined) =>
    playerId ? playerMap.get(playerId) ?? playerId : 'Unknown';

  const formatSpaceKey = (spaceKey: string) => {
    const spaceIndex = SPACE_INDEX_BY_KEY[spaceKey];
    return spaceIndex !== undefined ? getSpaceName(spaceIndex) : spaceKey;
  };

  const formatBundle = (bundle: {
    cash: number;
    properties: string[];
    get_out_of_jail_cards: number;
  }) => {
    const parts: string[] = [];
    if (bundle.cash > 0) parts.push(`$${bundle.cash}`);
    if (bundle.properties.length) {
      parts.push(bundle.properties.map(formatSpaceKey).join(', '));
    }
    if (bundle.get_out_of_jail_cards > 0) {
      const label = bundle.get_out_of_jail_cards === 1 ? 'jail card' : 'jail cards';
      parts.push(`${bundle.get_out_of_jail_cards} ${label}`);
    }
    return parts.length ? parts.join(' + ') : 'none';
  };

  return (
    <NeoCard className="p-2.5 bg-white">
      <div className="flex items-center justify-between mb-1">
        <span className="text-[10px] font-black uppercase tracking-wide">Trade</span>
        <span className="text-[8px] font-bold uppercase text-neo-blue bg-neo-blue/10 px-1.5 py-px rounded-[2px]">Active</span>
      </div>
      <div className="text-[9px] font-mono text-gray-400 leading-none">
        {formatPlayer(trade.initiator_player_id)}
        {' <-> '}
        {formatPlayer(trade.counterparty_player_id)}
      </div>
      <div className="mt-2 text-[10px] space-y-1.5">
        <div className="bg-neo-bg/60 rounded-[2px] px-2 py-1.5">
          <div className="flex justify-between mb-1">
            <span className="text-[8px] uppercase text-gray-400">Exchange</span>
            <span className="font-mono font-bold tabular-nums">
              {trade.exchange_index}/{trade.max_exchanges}
            </span>
          </div>
          <div>
            <span className="text-[8px] uppercase text-gray-400">Current Offer</span>
            <div className="font-mono text-[10px] mt-0.5 space-y-0.5">
              <div className="text-neo-green">Offer: {formatBundle(trade.current_offer.offer)}</div>
              <div className="text-neo-pink">Request: {formatBundle(trade.current_offer.request)}</div>
            </div>
          </div>
        </div>
        {trade.history_last_2.length > 0 && (
          <div className="pt-1 border-t border-black/5">
            <span className="text-[8px] uppercase text-gray-400">Recent Exchanges</span>
            <div className="font-mono text-[10px] mt-1 space-y-1.5">
              {trade.history_last_2.map((entry, index) => (
                <div key={`trade-history-${index}`} className="bg-neo-bg/40 rounded-[2px] px-1.5 py-1">
                  <div className="text-[9px] font-bold">{formatPlayer(entry.from_player_id)}</div>
                  <div className="text-gray-500">
                    Offer: {formatBundle(entry.offer)}
                  </div>
                  <div className="text-gray-500">
                    Request: {formatBundle(entry.request)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </NeoCard>
  );
};
