import { motion, AnimatePresence } from 'framer-motion';
import { useCallback, useEffect, useRef } from 'react';
import type { Space } from '@/net/contracts';
import { getGroupColor } from '@/domain/monopoly/colors';

interface PropertyToastProps {
    isVisible: boolean;
    space: Space;
    method: 'BOUGHT' | 'WON' | 'TRADED';
    price?: number | null;
    start: { x: number; y: number };
    target?: { x: number; y: number } | null;
    onComplete?: () => void;
}

export const PropertyToast = ({
    isVisible,
    space,
    method,
    price,
    start,
    target,
    onComplete,
}: PropertyToastProps) => {
    const groupColor = getGroupColor(space.group);
    const targetPos = target ?? { x: start.x + 140, y: start.y - 80 };
    const completedRef = useRef(false);

    const triggerComplete = useCallback(() => {
        if (completedRef.current) return;
        completedRef.current = true;
        onComplete?.();
    }, [onComplete]);

    useEffect(() => {
        if (!isVisible) return;
        completedRef.current = false;
        const timer = window.setTimeout(triggerComplete, 1200);
        return () => window.clearTimeout(timer);
    }, [isVisible, triggerComplete]);

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    className="fixed left-0 top-0 z-[70] pointer-events-none"
                    initial={{ opacity: 0, x: start.x, y: start.y, scale: 0.7 }}
                    animate={{ opacity: 1, x: targetPos.x, y: targetPos.y, scale: 0.95 }}
                    exit={{ opacity: 0, scale: 0.6 }}
                    transition={{ type: 'spring', stiffness: 180, damping: 20 }}
                    onAnimationComplete={triggerComplete}
                >
                    <div className="bg-white border-[1.5px] border-black/80 shadow-[4px_4px_0_0_rgba(0,0,0,0.8)] p-2 w-52 rounded-[3px]">
                        <div
                            className="w-full h-6 mb-2 border border-black/40 rounded-[2px] flex items-center justify-center font-black uppercase text-[9px] tracking-normal text-white"
                            style={{ backgroundColor: groupColor }}
                        >
                            {space.kind === 'PROPERTY' ? 'Title Deed' : space.name}
                        </div>

                        <div className="text-center">
                            <h3 className="text-[12px] font-black uppercase leading-tight mb-1.5 px-1">
                                {space.name}
                            </h3>

                            <div className="border-t border-black/10 pt-1.5 mt-1 flex items-center justify-center gap-2">
                                <span className="text-[8px] font-bold bg-black/90 text-white px-1.5 py-0.5 rounded-[2px] uppercase">
                                    {method}
                                </span>
                                {typeof price === 'number' ? (
                                    <span className="font-mono text-[11px] text-gray-600">${price}</span>
                                ) : null}
                            </div>
                        </div>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};
