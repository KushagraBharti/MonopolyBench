# T6. Normative contracts in three close environments

Each cell records what each environment's **instructions** or its **analysts' coding scheme** say about a behavior. A cell is not a moral judgment or a finding about behavior.

- "Not addressed" means not found in the inspected prompt or sections.
- "Externally coded" means the analysts classify the behavior as misaligned even though the agents' instructions are silent.

Sources: MonopolyBench `SYSTEM_PROMPT_V1` (`python/packages/arena/src/monopoly_arena/player_config.py`); AgentMonopoly, arXiv 2610.29330v2 §4, plus the repo README at commit 2434f427; Vending-Bench Arena paper, arXiv 2608.14825v3 §2.1–2.2, §4.1, App. D. Checked 2026-10-29 (Opus). Machine-readable version: `normative_contracts.csv`.

| Behavior | MonopolyBench (this cohort) | AgentMonopoly | Vending-Bench Arena paper |
|---|---|---|---|
| False public factual claim | **Explicitly permitted** ("Deception in public chat is allowed") | Bluffing **encouraged**; factual falsity not separately addressed | Instruction silent; **externally coded** misaligned (Stage B false factual claim) |
| Public message contradicting own action | Not explicitly addressed. Public deception is permitted, and the prompt also says "Be consistent unless there is a reason to change". Not the same measured violation as where it is prohibited | **Explicitly prohibited** | Instruction silent; follow-through measured descriptively (App. D) |
| False private note or reasoning | **Soft instruction against it** ("private thoughts should reflect true reasoning"). The note is also fed back as the agent's own memory, so a false note can mislead the agent's later decisions (Fable's point). Whether AgentMonopoly feeds `chain_of_thought` back is not reported in the inspected sections | Not addressed; the explanation is "not … how the model computes its decision" | Instruction silent; reasoning summaries audited for intent, as a lower bound |
| Withdrawing or changing a stated offer | Not addressed | Not addressed | Instruction silent; promise enactment measured |
| Coordinated pricing or market division | No price mechanism; "cooperative" play permitted; coalitions not addressed | Not addressed | Instruction silent; **externally coded** misaligned (collusion) |
| Pressure on or exploitation of a distressed counterparty | "manipulative" and "opportunistic" play **explicitly permitted** | Strategic rent waiving allowed; exploitation not addressed | Instruction silent; **externally coded** misaligned (manipulation) |
| Illegal game action | **Engine-prevented**: rejection, validation error, corrective retry, then deterministic fallback | **Engine-prevented** (legal_actions) | Not reported in inspected sections |

**Caption.** The same act has a different normative status across environments, so rates and labels do not transfer between them.

In MonopolyBench, a false public claim is authorized competitive conduct. A false private note is a potential breach of a soft instruction, but it is confounded with memory error. Applied rule violations cannot occur, while attempted invalid actions are recorded.

Under the current contract, an instruction-violation finding would require evidence that identifies a knowing false private note. That evidence is unavailable for most decisions (channel availability) and is not established in any checked case. This is non-identification, not impossibility (accepted from Astra, debate R3).
