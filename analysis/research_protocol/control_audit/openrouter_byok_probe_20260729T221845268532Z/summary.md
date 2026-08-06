# OpenRouter BYOK Cost Probe

- Successful calls: 12/16
- BYOK calls: 4
- Non-BYOK calls: 8
- Total tokens: 4349
- Reported usage cost: $0.01767390
- OpenRouter available-credit delta: $0.00000000

| Actor | Calls | BYOK | Prompt | Completion | Reasoning | Total | Cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| claude_opus_48_medium | 4 | 0 | 0 | 0 | 0 | 0 | $0.00000000 |
| gemini_31_pro_preview_medium | 4 | 0 | 59 | 948 | 904 | 1007 | $0.01149400 |
| grok_43_medium | 4 | 0 | 822 | 2276 | 2222 | 3098 | $0.00617990 |
| openai_gpt_55_medium | 4 | 4 | 78 | 166 | 100 | 244 | $0.00000000 |

The credit delta is an account-level before/after observation and may include
unrelated concurrent activity. Per-call `usage.is_byok` is the routing evidence.
