import { labBrand, labLogoSrc } from '@/domain/labBrand'

/** Local, dependency-free brand mark. The surrounding UI supplies seat identity. */
export function LabLogo({ model, className, decorative = false }: { model: string; className?: string; decorative?: boolean }) {
  const src = labLogoSrc(model)
  if (src) return <img src={src} alt={decorative ? '' : `${labBrand(model)?.name} logo`} aria-hidden={decorative || undefined} className={className} draggable={false} />
  return <svg viewBox="0 0 24 24" role={decorative ? undefined : 'img'} aria-label={decorative ? undefined : 'Model'} aria-hidden={decorative || undefined} className={className}><rect x="3" y="3" width="18" height="18" rx="4" fill="none" stroke="currentColor" strokeWidth="2" /><circle cx="8" cy="10" r="1.5" /><circle cx="16" cy="10" r="1.5" /><path d="M8 16h8" fill="none" stroke="currentColor" strokeWidth="2" /></svg>
}
