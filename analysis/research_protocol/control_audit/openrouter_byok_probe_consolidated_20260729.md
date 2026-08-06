# Consolidated OpenRouter BYOK Probe

- Canonical requirement passed: **True**
- Calls: 16
- Total tokens: 4666
- Reported cost: **$0.01767390**
- BYOK calls: 8
- Non-BYOK calls: 8

| Model | Calls | BYOK | Prompt | Completion | Reasoning | Total | Cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| anthropic/claude-opus-4.8 | 4 | 4 | 115 | 202 | 85 | 317 | $0.00000000 |
| google/gemini-3.1-pro-preview | 4 | 0 | 59 | 948 | 904 | 1007 | $0.01149400 |
| x-ai/grok-4.3 | 4 | 0 | 822 | 2276 | 2222 | 3098 | $0.00617990 |
| openai/gpt-5.5 | 4 | 4 | 78 | 166 | 100 | 244 | $0.00000000 |

## All attempts

- Attempts: 21
- Successful: 17
- Failed: 4
- Tokens: 4725
- Reported cost: $0.01767390

Four failed attempts were Anthropic requests with the roster's explicit
`provider.only=["anthropic"]` filter. Unfiltered diagnostic requests returned
provider `Anthropic`, `is_byok=true`, and zero reported cost.
