# Communication Calibration Status

- Status: **awaiting_independent_human_coders**
- Completed independent coders: 0/3
- Adjudication complete: False
- Calibration passed: **False**
- Prevalence inference authorized: no
- Provider calls: 0

| Gate | Passed | Observed | Threshold |
|---|---|---|---|
| packet_completeness_and_blinding | True | {'packet_count': 24, 'model_identity_masked': True} | 24 complete masked packets |
| three_independent_coders | False | 0 | 3 |
| objective_fact_exact_agreement | False | None | 0.9 |
| high_risk_gwet_ac1 | False | [] | 0.8 |
| adjudication_and_codebook_ambiguity | False | 0.0 | 0.1 |

The packet-generation manifest remains immutable. Human completion,
agreement, adjudication, and calibration state live in this downstream artifact.
