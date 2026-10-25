const LABS = {
  openai: { name: 'OpenAI', file: 'openai.svg' },
  anthropic: { name: 'Anthropic', file: 'anthropic.svg' },
  gemini: { name: 'Google Gemini', file: 'gemini.svg' },
  xai: { name: 'xAI', file: 'xai.svg' },
} as const

/** Identity comes from the model, never the seat or player color. */
export function labBrand(model: string) {
  const id = model.trim().toLowerCase()
  if (id.startsWith('openai/') || /^(gpt-|o[134](?:-|$))/.test(id)) return LABS.openai
  if (id.startsWith('anthropic/') || id.startsWith('claude')) return LABS.anthropic
  if (id.startsWith('google/') || id.startsWith('gemini')) return LABS.gemini
  if (id.startsWith('x-ai/') || id.startsWith('xai/') || id.startsWith('grok')) return LABS.xai
  return null
}

export function labLogoSrc(model: string): string | null {
  const brand = labBrand(model)
  return brand ? `${import.meta.env?.BASE_URL ?? '/'}labs/${brand.file}` : null
}
