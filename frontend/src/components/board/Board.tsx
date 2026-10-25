import { useMemo } from 'react';
import type { ReactNode } from 'react';
import type { Player, Space } from '@/net/contracts';
import { Tile } from '@/components/board/Tile';
import { cn } from '@/components/ui/cn';
import { TokenLayer } from '@/components/board/TokenLayer';
import { BOARD_TRACKS, getGridPosition } from '@/components/board/utils';
import { useGameStore, type StoreState } from '@/state/store';

type BoardHighlightState = {
    deedHighlight?: number | null;
    eventHighlight?: number[] | null;
    decisionHighlight?: number[] | null;
};

interface BoardProps {
    spaces: Space[];
    className?: string;
    showTokens?: boolean;
    players?: Player[];
    activePlayerId?: string | null;
    highlightState?: BoardHighlightState;
    centerContent?: ReactNode;
    /** Model id per player_id from the run configuration; tokens show that model's lab logo. */
    playerModels?: Record<string, string>;
    /** Accessible name for the board region. */
    label?: string;
    /** Display name per player_id for token and owner labels. Defaults to the snapshot name. */
    playerLabels?: Record<string, string>;
    /** Engine phase of the shown snapshot. GAME_OVER suppresses the active-turn token. */
    phase?: string | null;
}

export const Board = ({
    spaces,
    className,
    showTokens = true,
    players,
    activePlayerId,
    highlightState,
    centerContent,
    playerModels,
    label,
    playerLabels,
    phase,
}: BoardProps) => {
    const { deedHighlight, eventHighlight, decisionHighlight } = useGameStore(
        (state: StoreState) => state.ui
    );
    const snapshot = useGameStore((state: StoreState) => state.snapshot);

    // A board given explicit players renders only its own data: it never borrows the
    // global live snapshot's highlights or turn holder. null means "none", undefined
    // means "not specified".
    const explicit = players !== undefined;
    const pick = <T,>(key: keyof BoardHighlightState, global: T): T | null => {
        if (highlightState && highlightState[key] !== undefined) return highlightState[key] as T | null;
        return explicit ? null : global;
    };
    const resolvedDeedHighlight = pick('deedHighlight', deedHighlight);
    const resolvedEventHighlight = pick('eventHighlight', eventHighlight);
    const resolvedDecisionHighlight = pick('decisionHighlight', decisionHighlight);
    const globalPlayers = snapshot?.players;
    const resolvedPlayers = useMemo(() => players ?? globalPlayers ?? [], [players, globalPlayers]);
    const resolvedPhase = phase !== undefined ? phase : explicit ? null : snapshot?.phase ?? null;
    const requestedActive = activePlayerId !== undefined ? activePlayerId : explicit ? null : snapshot?.active_player_id ?? null;
    const resolvedActivePlayerId = resolvedPhase === 'GAME_OVER' ? null : requestedActive;

    const ownerNames = useMemo(
        () => new Map(resolvedPlayers.map((player) => [player.player_id, playerLabels?.[player.player_id] ?? player.name])),
        [resolvedPlayers, playerLabels]
    );

    const highlightSets = useMemo(() => {
        return {
            event: new Set(resolvedEventHighlight ?? []),
            decision: new Set(resolvedDecisionHighlight ?? []),
        };
    }, [resolvedDecisionHighlight, resolvedEventHighlight]);

    // Ensure we have 40 spaces
    const safeSpaces = useMemo(() => {
        if (spaces.length === 40) return spaces;
        return Array.from({ length: 40 }).map((_, i) => ({
            index: i,
            kind: 'PROPERTY',
            name: `Space ${i}`,
            group: null,
            price: null,
            owner_id: null,
            mortgaged: false,
            houses: 0,
            hotel: false,
        } as Space));
    }, [spaces]);

    return (
        <div className={cn('relative p-3', className)} data-board-root="true" role={label ? 'region' : undefined} aria-label={label}>
            {/* Board Physical Base */}
            <div className="relative w-full h-full bg-[#e4f1e1] border-2 border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,0.85)] overflow-hidden">
                {/* The Grid */}
                <div
                    className="absolute inset-0 grid gap-px bg-black"
                    style={{ gridTemplateColumns: BOARD_TRACKS, gridTemplateRows: BOARD_TRACKS }}
                >
                    {safeSpaces.map((space) => {
                        const { row, col } = getGridPosition(space.index);
                        return (
                            <div
                                key={space.index}
                                style={{
                                    gridRow: row,
                                    gridColumn: col,
                                }}
                                className="relative min-w-0 min-h-0"
                            >
                                <Tile
                                    space={space}
                                    ownerName={space.owner_id ? ownerNames.get(space.owner_id) ?? null : null}
                                    highlightSource={
                                        resolvedDeedHighlight === space.index
                                            ? 'deed'
                                            : highlightSets.decision.has(space.index)
                                                ? 'decision'
                                                : highlightSets.event.has(space.index)
                                                    ? 'event'
                                                    : null
                                    }
                                />
                            </div>
                        );
                    })}

                    {/* Center Board Area */}
                    <div className="row-start-2 row-end-11 col-start-2 col-end-11 bg-[#cfe5d0] flex items-center justify-center flex-col relative overflow-hidden min-w-0 min-h-0">
                        {centerContent ?? (
                            <div className="z-10 flex h-full w-full max-w-full items-center justify-center">
                                <img
                                    src="/../logo2.png"
                                    alt="Monopoly Bench"
                                    className="h-auto max-h-[60%] w-auto max-w-[70%] object-contain"
                                />
                            </div>
                        )}
                    </div>
                </div>

                {/* Token Overlay */}
                {showTokens ? <TokenLayer players={resolvedPlayers} activePlayerId={resolvedActivePlayerId} playerModels={playerModels} playerLabels={Object.fromEntries(ownerNames)} /> : null}
            </div>
        </div>
    );
};
