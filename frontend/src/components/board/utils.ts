/** Corner squares are wider than edge squares, as on a printed board. */
export const CORNER_RATIO = 1.6;
const TRACK_TOTAL = 9 + 2 * CORNER_RATIO;
export const BOARD_TRACKS = `${CORNER_RATIO}fr repeat(9, minmax(0, 1fr)) ${CORNER_RATIO}fr`;

export type BoardSide = 'bottom' | 'left' | 'top' | 'right' | 'corner';

export const getGridPosition = (index: number) => {
    if (index >= 0 && index <= 10) {
        // Bottom: 0 is at 11/11. 10 is at 11/1.
        return { row: 11, col: 11 - index };
    } else if (index >= 11 && index <= 19) {
        // Left: 11 is at 10/1. 19 is at 2/1.
        return { row: 11 - (index - 10), col: 1 };
    } else if (index >= 20 && index <= 30) {
        // Top: 20 is at 1/1. 30 is at 1/11.
        return { row: 1, col: 1 + (index - 20) };
    } else {
        // Right: 31 is at 2/11. 39 is at 10/11.
        return { row: 1 + (index - 30), col: 11 };
    }
};

export const getBoardSide = (index: number): BoardSide => {
    if (index % 10 === 0) return 'corner';
    if (index < 10) return 'bottom';
    if (index < 20) return 'left';
    if (index < 30) return 'top';
    return 'right';
};

/** Center of a 1-based grid track as a percentage of the board edge. */
const trackCenter = (track: number) => {
    if (track === 1) return (CORNER_RATIO / 2 / TRACK_TOTAL) * 100;
    if (track === 11) return ((TRACK_TOTAL - CORNER_RATIO / 2) / TRACK_TOTAL) * 100;
    return ((CORNER_RATIO + (track - 2) + 0.5) / TRACK_TOTAL) * 100;
};

/** Corner square edge as a percentage of the board edge. */
export const CORNER_PERCENT = (CORNER_RATIO / TRACK_TOTAL) * 100;

// Start at bottom right, clockwise
export const getCSSPosition = (index: number) => {
    const { row, col } = getGridPosition(index);
    return { x: trackCenter(col), y: trackCenter(row) };
};

// Square-relative 2x2 slots, in board container units. A token is 3.6cqw wide, so a
// 1.9cqw offset keeps four tokens inside the narrowest edge square (about 8.2cqw).
const SLOT_GRID: Array<[number, number]> = [[-1, -1], [1, -1], [-1, 1], [1, 1]];
const SLOT_STEP = 1.9;

// Jail corner, in fractions of the corner square from its top-left. Visitors use the
// outer L-shaped strip; jailed players use the cell in the inner corner.
// Leave room for the scaled visitor disc, active ring and shadow at the outer edge.
const VISITOR_SLOTS: Array<[number, number]> = [[0.225, 0.775], [0.5, 0.775], [0.225, 0.5], [0.775, 0.775], [0.225, 0.225]];
const JAIL_CELL: [number, number] = [0.65, 0.35];

const cornerPoint = ([fx, fy]: [number, number]) => ({ x: CORNER_PERCENT * fx, y: 100 - CORNER_PERCENT + CORNER_PERCENT * fy });

/**
 * Token anchor for a player. Jail (index 10) has two zones: the cell in the inner
 * corner for players the snapshot marks in_jail, and the outer strip for visitors.
 */
export const getTokenAnchor = (index: number, inJail: boolean) => {
    if (index !== 10) return getCSSPosition(index);
    return inJail ? cornerPoint(JAIL_CELL) : cornerPoint(VISITOR_SLOTS[0]);
};

/** Offset of the n-th of `count` tokens sharing a zone, in board container units (cqw). */
export const getSlotOffset = (count: number, index: number): [number, number] => {
    if (count <= 1) return [0, 0];
    if (count === 2) return [index === 0 ? -SLOT_STEP : SLOT_STEP, 0];
    const [gx, gy] = SLOT_GRID[index % SLOT_GRID.length];
    const ring = Math.floor(index / SLOT_GRID.length);
    return [gx * SLOT_STEP + ring * 0.8, gy * SLOT_STEP + ring * 0.8];
};

/** Where the n-th token in a zone sits: percentage anchor plus a cqw offset. */
export const getTokenPlacement = (position: number, inJail: boolean, count: number, index: number) => {
    if (position === 10 && !inJail) return { ...cornerPoint(VISITOR_SLOTS[index % VISITOR_SLOTS.length]), dx: 0, dy: 0 };
    const [dx, dy] = getSlotOffset(count, index);
    return { ...getTokenAnchor(position, inJail), dx, dy };
};

/** Tokens that share a zone are spread together. Jail and visiting are separate zones. */
export const getTokenZone = (position: number, inJail: boolean) => (position === 10 && inJail ? 'jail' : `square:${position}`);
