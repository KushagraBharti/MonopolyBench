import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { labBrand, labLogoSrc } from '../src/domain/labBrand.ts'

test('logos follow actual rotated model identities and preserve Anthropic fallback branding', () => {
  const models = ['x-ai/grok-4.7', 'anthropic/claude-opus-5.5', 'openai/gpt-6.1-sol', 'google/gemini-4-argon', 'anthropic/claude-opus-4.8']
  assert.deepEqual(models.map(m => labBrand(m)?.name), ['xAI', 'Anthropic', 'OpenAI', 'Google Gemini', 'Anthropic'])
  for (const model of models) {
    const src = labLogoSrc(model)
    const svg = readFileSync(new URL('../public' + src, import.meta.url), 'utf8')
    assert.match(svg, /<svg\b/)
    assert.doesNotMatch(svg, /<script\b|https?:\/\/[^" ]+\.(?:png|jpg)/)
  }
})

test('duplicate models keep the same brand, unsupported models do not masquerade as a lab', () => {
  assert.equal(labLogoSrc('openai/gpt-6.1-sol'), labLogoSrc('GPT-6.1-SOL'))
  assert.equal(labBrand('vendor/unknown'), null)
  assert.equal(labLogoSrc('vendor/unknown'), null)
})
