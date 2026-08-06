# Campaign control evidence

`openrouter_preflight.json` is the current E1 authorization artifact. It was captured
after commit `64534655` and includes one forced tool call through each exact route.

The dated `openrouter_byok_probe_20260729*` artifacts are historical diagnostics.
They record the account state observed on July 29, when both OpenAI and Anthropic BYOK
were available. They must not be used as evidence of current billing configuration.

The current policy is:

- OpenAI: BYOK required and fail-closed;
- Anthropic: OpenRouter credits;
- Google AI Studio: OpenRouter credits;
- xAI: OpenRouter credits.

The preflight remains unauthorized whenever any route or tool call fails, OpenAI BYOK
is not confirmed, the roster hash changes, the snapshot becomes stale, or available
OpenRouter credits are below the registered E1 threshold.
