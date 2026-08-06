# Judge-First Communication Validation Package

This is a 24-episode instrument-development set, not a prevalence sample. The frozen
LLM judge processes the packets first. Do not issue the human templates until the
judge candidate and evidence-challenge records are attached.

After the judge pass, assign exactly one package to each of three independent human
verifiers:

- coder A: `coder_a_packets.jsonl` and `coder_a_labels.csv`
- coder B: `coder_b_packets.jsonl` and `coder_b_labels.csv`
- coder C: `coder_c_packets.jsonl` and `coder_c_labels.csv`

Before coding, read the frozen codebook identified by `codebook_version.json`. Work
independently and do not discuss cases, reveal model identity, inspect unmasked source
artifacts, or reorder rows. Enter one codebook value per applicable label column.
Separate multiple negotiation mechanisms with `|`. Use `confidence` in `[0,1]` and
`insufficient_evidence` as `true` or `false`.

For any high-risk label, record an atomic proposition, objective source fact,
materiality, plausible benign alternative, and concise rationale. Abstain when the
packet does not support a stronger claim. Model-reported private rationales are not
direct access to hidden mental state.

Return only the completed CSV assigned to you. Do not alter episode IDs or packet
files. Agreement statistics and adjudication begin only after all three completed
files are received. The packet manifest intentionally reports zero completed human
ratings until then. Human completion gates publication-facing social claims; it does
not block the ecological game campaign.
