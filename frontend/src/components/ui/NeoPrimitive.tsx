import { type ButtonHTMLAttributes, type HTMLAttributes, forwardRef } from 'react';
import { cn } from '@/components/ui/cn';

interface NeoProps extends HTMLAttributes<HTMLDivElement> {
    variant?: 'default' | 'flat' | 'bordered';
}

export const NeoCard = forwardRef<HTMLDivElement, NeoProps>(
    ({ className, variant = 'default', children, ...props }, ref) => {
        return (
            <div
                ref={ref}
                className={cn(
                    "bg-white border-2 border-black rounded-[3px]",
                    variant === 'default' && "shadow-neo",
                    variant === 'flat' && "shadow-none",
                    className
                )}
                {...props}
            >
                {children}
            </div>
        );
    }
);
NeoCard.displayName = "NeoCard";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
}

export const NeoButton = forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = 'primary', size = 'md', ...props }, ref) => {
        const variants = {
            primary: "bg-neo-green hover:bg-green-400 text-black",
            secondary: "bg-neo-yellow hover:bg-yellow-300 text-black",
            danger: "bg-neo-pink hover:bg-pink-400 text-white",
            ghost: "bg-transparent shadow-none border-2 border-black/20 hover:border-black hover:shadow-neo-sm hover:translate-x-0 hover:translate-y-0"
        };

        const sizes = {
            sm: "min-h-9 px-3 py-1 text-sm",
            md: "min-h-10 px-6 py-2 text-base",
            lg: "min-h-12 px-8 py-4 text-xl",
        };

        return (
            <button
                ref={ref}
                className={cn(
                    variants[variant],
                    sizes[size],
                    "font-bold uppercase tracking-normal transition-all duration-100 active:translate-y-0.5 active:shadow-none border-2 border-black shadow-neo rounded-[3px] select-none disabled:cursor-not-allowed disabled:opacity-45 disabled:hover:bg-inherit",
                    variant === 'ghost' && "shadow-none active:translate-y-0",
                    className
                )}
                {...props}
            />
        );
    }
);
NeoButton.displayName = "NeoButton";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
    variant?: 'neutral' | 'success' | 'warning' | 'error' | 'info';
}

export const NeoBadge = ({ className, variant = 'neutral', ...props }: BadgeProps) => {
    const variants = {
        neutral: "bg-gray-100 text-gray-700 border-gray-300",
        success: "bg-neo-green/90 text-black border-black",
        warning: "bg-neo-yellow/90 text-black border-black",
        error: "bg-neo-pink/90 text-white border-black",
        info: "bg-neo-cyan/90 text-black border-black",
    };

    return (
        <span
            className={cn(
                "inline-flex items-center px-2 py-0.5 border-[1.5px] text-[10px] font-bold uppercase tracking-wide rounded-[2px]",
                variants[variant],
                className
            )}
            {...props}
        />
    );
}
