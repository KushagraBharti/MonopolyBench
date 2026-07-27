import { useMemo } from 'react';
import type { ReactNode } from 'react';
import type { Player, Space } from '@/net/contracts';
import { Tile } from '@/components/board/Tile';
import { cn } from '@/components/ui/cn';
import { TokenLayer } from '@/components/board/TokenLayer';
import { getGridPosition } from '@/components/board/utils';
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
}

export const Board = ({
    spaces,
    className,
    showTokens = true,
    players,
    activePlayerId,
    highlightState,
    centerContent,
}: BoardProps) => {
    const { deedHighlight, eventHighlight, decisionHighlight } = useGameStore(
        (state: StoreState) => state.ui
    );
    const snapshot = useGameStore((state: StoreState) => state.snapshot);

    const resolvedDeedHighlight = highlightState?.deedHighlight ?? deedHighlight;
    const resolvedEventHighlight = highlightState?.eventHighlight ?? eventHighlight;
    const resolvedDecisionHighlight = highlightState?.decisionHighlight ?? decisionHighlight;
    const resolvedPlayers = players ?? snapshot?.players ?? [];
    const resolvedActivePlayerId = activePlayerId ?? snapshot?.active_player_id ?? null;

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
        <div className={cn('relative p-3', className)} data-board-root="true">
            {/* Board Physical Base */}
            <div className="relative w-full h-full bg-[linear-gradient(145deg,#f9f6f0,#f0eadd)] border-[6px] border-black shadow-[10px_10px_0px_0px_rgba(0,0,0,0.85)] rounded-[2px] overflow-hidden">
                <div className="absolute inset-[6px] border border-black/15 pointer-events-none rounded-[1px]" />

                {/* The Grid */}
                <div className="absolute inset-0 grid grid-cols-11 grid-rows-11 gap-px bg-[#1a1a1a] p-[2px]">
                    {safeSpaces.map((space) => {
                        const { row, col } = getGridPosition(space.index);
                        return (
                            <div
                                key={space.index}
                                style={{
                                    gridRow: row,
                                    gridColumn: col,
                                }}
                                className="relative bg-white"
                            >
                                <Tile
                                    space={space}
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
                    <div className="row-start-2 row-end-11 col-start-2 col-end-11 bg-[#f8f5ee] flex items-center justify-center flex-col relative overflow-hidden">

                        {/* Subtle Center Texture */}
                        <div className="absolute inset-0 opacity-[0.04] bg-[radial-gradient(circle_at_center,#000_0.8px,transparent_0.8px)] bg-size-[14px_14px]" />

                        {/* Branding */}
                        {centerContent ?? (
                            <div className="z-10 flex h-full w-full max-w-full items-center justify-center">
                                <img
                                    src="/../logo2.png"
                                    alt="Monopoly Bench"
                                    className="h-auto max-h-[72%] w-auto max-w-[82%] object-contain drop-shadow-[3px_3px_0_rgba(0,0,0,0.08)]"
                                />
                            </div>
                        )}
                    </div>
                </div>

                {/* Token Overlay */}
                {showTokens ? <TokenLayer players={resolvedPlayers} activePlayerId={resolvedActivePlayerId} /> : null}
            </div>
        </div>
    );
};
