# Q4 six-seed campaign

Twenty-four uncapped games, six independent seed blocks and four cyclic seat
rotations per block. The campaign runs at most four workers concurrently, with
provider-native medium effort and execution policy v3.

The owner chose no campaign dollar cap. OpenAI uses BYOK first with the existing
OpenRouter-credit fallback. No purchase or automatic top-up is authorized.
Anthropic BYOK remains preferred; Gemini and Grok use OpenRouter credits.
One technical rerun per failed cell is permitted, retaining the original.

`seed_draw.json` preserves the initial seed and its five subsequent draws from
the recorded entropy. `run_matrix.json` fixes every cell and randomized execution
rank. `analysis_contract.json` defines descriptive outcomes, correct reliability
denominators, the versioned communication codebook, review and claim boundaries.
The runtime campaign JSON embeds these records and their hashes so the live
freeze and campaign export remain self-contained.

The participant label is "Opus 5.5 (with fallbacks)". Every attempt retains its
actual model, response condition, private-note availability and returned reasoning.
Six seed blocks are not twenty-four independent replications or a power guarantee.

Publishing or freezing does not start games. The live campaign must remain
`frozen` until a separately authorized Run action. No source deployment may occur
during its execution. The live freeze records the final deployed SHA, source
fingerprint, current passing preflight and registry/configuration hashes.
