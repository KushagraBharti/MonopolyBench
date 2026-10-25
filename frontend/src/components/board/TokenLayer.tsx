import type { CSSProperties } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { useGameStore } from '@/state/store';
import { getTokenPlacement, getTokenZone } from '@/components/board/utils';
import { getPlayerColor, getPlayerTokenSrc } from '@/domain/monopoly/colors';
import { getSpaceName } from '@/domain/monopoly/constants';
import { LabLogo } from '@/components/LabLogo';
import type { Player } from '@/net/contracts';

type TokenLayerProps = {
    players?: Player[];
    /** null means no turn holder. undefined falls back to the global live snapshot. */
    activePlayerId?: string | null;
    /** Model id per player_id from the run configuration. Players without one keep the classic pawn. */
    playerModels?: Record<string, string>;
    /** Display name per player_id for the accessible label. */
    playerLabels?: Record<string, string>;
};

const describe = (player: Player, label: string, isActive: boolean) => {
    const parts = [label];
    if (player.bankrupt) parts.push('bankrupt');
    else if (player.in_jail) parts.push(`in jail, ${player.jail_turns} turn${player.jail_turns === 1 ? '' : 's'} served`);
    else parts.push(`on ${getSpaceName(player.position)}`);
    if (isActive) parts.push('current turn');
    return parts.join(', ');
};

export const TokenLayer = ({ players: playersProp, activePlayerId, playerModels, playerLabels }: TokenLayerProps) => {
    const snapshot = useGameStore((state) => state.snapshot);
    const reduceMotion = useReducedMotion();
    const players = playersProp ?? snapshot?.players ?? [];
    const activeId = activePlayerId !== undefined ? activePlayerId : snapshot?.phase === 'GAME_OVER' ? null : snapshot?.active_player_id ?? null;

    const zoneKey = (player: Player) => getTokenZone(player.position, player.in_jail);
    const zoneCounts = new Map<string, number>();
    players.forEach((p) => zoneCounts.set(zoneKey(p), (zoneCounts.get(zoneKey(p)) ?? 0) + 1));
    const zoneIndexes = new Map<string, number>();

    return (
        <div className="absolute inset-0 pointer-events-none z-30 overflow-visible" role="list" aria-label="Player tokens">
            {players.map((player) => {
                const key = zoneKey(player);
                const isActive = activeId === player.player_id && !player.bankrupt;
                const model = playerModels?.[player.player_id];
                const count = zoneCounts.get(key) ?? 1;
                const indexInZone = zoneIndexes.get(key) ?? 0;
                zoneIndexes.set(key, indexInZone + 1);
                const { x, y, dx, dy } = getTokenPlacement(player.position, player.in_jail, count, indexInZone);
                const label = describe(player, playerLabels?.[player.player_id] ?? player.name ?? player.player_id, isActive);

                return (
                    <motion.div
                        key={player.player_id}
                        role="listitem"
                        aria-label={label}
                        initial={false}
                        animate={{
                            left: `calc(${x}% + ${dx}cqw)`,
                            top: `calc(${y}% + ${dy}cqw)`,
                            scale: isActive ? 1.1 : 1.0,
                            zIndex: isActive ? 100 : 50 + indexInZone,
                        }}
                        transition={reduceMotion ? { duration: 0 } : { type: 'spring', stiffness: 140, damping: 20, mass: 0.8 }}
                        className="absolute w-0 h-0 flex items-center justify-center"
                    >
                        {model ? (
                            <div
                                className="mb-token shrink-0"
                                style={{ '--mb-seat': getPlayerColor(player.player_id) } as CSSProperties}
                                data-active={isActive || undefined}
                                data-jailed={player.in_jail || undefined}
                                data-visiting={player.position === 10 && !player.in_jail || undefined}
                                data-bankrupt={player.bankrupt || undefined}
                            >
                                <LabLogo model={model} decorative />
                            </div>
                        ) : (
                            <div
                                className="mb-pawn shrink-0"
                                data-visiting={player.position === 10 && !player.in_jail || undefined}
                                data-active={isActive || undefined}
                                data-bankrupt={player.bankrupt || undefined}
                            >
                                <img
                                    src={getPlayerTokenSrc(player.player_id)}
                                    alt=""
                                    className="block w-full h-full object-contain select-none pointer-events-none"
                                    draggable={false}
                                />
                            </div>
                        )}
                    </motion.div>
                );
            })}
        </div>
    );
};
