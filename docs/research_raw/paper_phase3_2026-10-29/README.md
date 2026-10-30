# Phase 3: evidence, literature, exhibits and outline

## Shared package

Steps **11–14** are assembled: claim-dependent experiment decisions, a primary-source literature comparison, generated figures/tables and a new venue-neutral paper outline. The full manuscript and release validation are later stages. No new paid games, canonical artifact edits, prompt changes or engine changes were made here.

Start with:

- [LaTeX drafting package](latex/README.md): editable outline, figures and native tables; [outline PDF](latex/paper_outline.pdf) and [exhibit PDF](latex/figures_and_tables.pdf). The original Markdown below is retained as the source snapshot; the literature review remains in Markdown.
- [Detailed paper outline](paper_outline.md): argument, evidence, figures, citations and competing explanations for every section.
- [Experiment decisions](experiment_decisions.md): retained claims, optional existing-log analyses and studies needed only for stronger claims.
- [Literature review](literature_review.md), [34-entry selected bibliography](references.bib) and [version/provenance registry](reference_registry.json).
- [Figures and tables](figures_and_tables.md), [visual gallery](figure_gallery.html) and [full captions](astra/exhibit_captions.md).
- [Integration decisions and preserved dissent](integration_log.md) and [package verification](verification.json).

The paper's central evidence combines economic trajectories and social conduct. Capability and alignment remain the research motivation; a capability-growth/alignment curve, intrinsic model ranking, causal persuasion and successful RL training are not findings of this cohort. The strongest method contribution is a demonstrated exact-prefix legal-alternative protocol, not a claim to have invented replay or economic-agent evaluation.

## Reproduction of this stage

From the repository root, using the existing Python environment:

```sh
PYTHONDONTWRITEBYTECODE=1 python/.venv/bin/python docs/research_raw/paper_phase3_2026-10-29/astra/build_reference_library.py
PYTHONDONTWRITEBYTECODE=1 python/.venv/bin/python docs/research_raw/paper_phase3_2026-10-29/astra/check_deployment_residuals.py
PYTHONDONTWRITEBYTECODE=1 python/.venv/bin/python docs/research_raw/paper_phase3_2026-10-29/astra/build_exhibits.py
PYTHONDONTWRITEBYTECODE=1 python/.venv/bin/python docs/research_raw/paper_phase3_2026-10-29/astra/verify_package.py
```

These commands regenerate downstream outputs and check their source links. They rely on retained phase-1/phase-2 audits and saved games; this is not yet the clean external release test planned for step 17. Plot file hashes identify this export, not a promise of byte-identical PDF metadata across rebuilds. Semantic and causal validity are not established by file/hash checks alone.

Each coauthor worked across the full scope. Independent proposals and debate remain in [Sol's handoff](sol/handoff.md), [Opus's handoff](opus/handoff.md), [Fable's handoff](fable/handoff.md), and [Astra's handoff](astra/handoff.md). Their archived proposals can contain wording subsequently superseded by the shared integration log. The final assembly was checked by Astra; it is not described as another blind four-way review.

## Original stage contract

The user authorized steps 11–14 on 2026-10-29. Astra, Sol, Opus and Fable are equal, overlapping coauthors. Each examines the entire question, experimental sufficiency, related work, figures/tables and detailed paper structure. This is not a division into one researcher per topic. Preserve independent initial positions, then challenge one another with evidence and co-write the final package.

## Deliverables

1. A claim-to-experiment decision matrix. Distinguish existing support, existing-log analysis, optional strengthening and experiments necessary only for stronger claims. Do not run new paid experiments or change benchmark behavior.
2. A verified primary-source literature map and bibliography. Include the user's named papers, direct Monopoly/economic competitors, long-horizon evaluation, safety and social conduct, and evaluation validity. Record version, checked URL, relevant section and bounded comparison. An absent feature must be described as unreported in the inspected source unless independently established. Search snippets alone do not substantiate methods claims.
3. Regenerable, inspected figures and tables with source IDs/hashes, units, caption limits and semantic checks. Publication assets should be standalone files. Keep outcome profiles, longitudinal economics and social cases substantial; interface findings explain affected results rather than replace the paper's subject.
4. A new detailed, venue-neutral outline. Each section needs its argument, evidence, exhibits, citations, alternative explanations and transitions. Include the capability/alignment ambition and realistic sandbox motivation, while distinguishing implemented affordances from measured alignment and unimplemented training.

Do not start the complete manuscript or venue tailoring in this stage. Preserve canonical games, prompts, engine and prior research records. Write each coauthor's work under their own named folder; root assembles versioned shared artifacts only after evidence reconciliation. No commits or pushes.

## Existing evidence

Start with ../paper_phase2_2026-10-28/core_review/astra/review_handoff.md, methods_and_findings.md, claims.md and reconciliation.md. Read all three peers' final syntheses as well. Initial judgments, corrections and source IDs remain in each core_review directory. Phase-1 setup/replay evidence is in ../paper_phase1_2026-10-28/.

Important final corrections: 103 spending game/player/color units; $103,450 outlay; $93,000 whole-game developed paid rent, $92,550 after first own spend; 58 winner spending groups, 34 containing inherited deeds, thirty first complete via estate. Three of sixty eliminations admit current-debt payment, with differing mechanisms; 56 fail even a full upper bound; one hotel lock. All61 Opus defaulted purchase multisets execute after reordering. Recovery can change quantities. Grok has139 received-name conflicts, fifteen equal parsed argument objects, only five literally identical JSON substrings. Trade-history manifestations reach2054/6989 initial prompts, not proven reliance. Five seed blocks, four rotations each; same raw dice do not mean identical opportunities.

Public deception is permitted by the game instructions. The current cohort does not establish a capability-growth/alignment trend, intrinsic provider ranking, causal persuasion, optimal policy, deliberate kingmaking or counterfactual winners. Recorded explanations are not privileged hidden intent. No false claim of independent human annotation or preregistration.

## Literature coverage

The user's named starting set: Vending-Bench, AgentMonopoly, SOTOPIA, Concordia, The Agent Company, AgentBench, WebArena, OSWorld, tau-bench, AgentDojo, MLE-bench and METR time horizons. Also examine Vending-Bench2 and Arena, FinBoardBench, NegotiationArena, MACHIAVELLI, AgentBoard, HAL, Cattle Trade, DECE and relevant promise/commitment studies. Add or prune according to actual explanatory value, not a citation quota. Distinguish papers, workshop papers, author eval pages and software documentation.

Astra's initial primary-source check found Vending-Bench Arena explicitly includes competitive co-located businesses, collaboration and trading. The proposal must therefore not claim multiplayer economics as absent from Vending-Bench generally. AgentMonopoly already records public/private explanations and actions. FinBoardBench provides an acquisition-to-conversion account and liquidity/ROI summaries; the earlier broad “longitudinal acquisition and finance” wording is narrowed after Fable's source challenge. Seek precise additional measurement and instrument contributions, not blanket superiority.

## Peer process

Each researcher first saves an initial full-scope position, then exchanges concrete objections with all other running coauthors. Use direct messages while their tasks run and durable debate notes. New reviews of a finished coauthor require a new delegated task, not a message that silently restarts it. No repeated polling or empty status updates. Send substantive early findings to Astra so parallel writing can proceed.

Your work should contain enough concrete text, citations and exhibit specifications to improve the paper directly. Do not stop at a plan or a generic reading list. Distinguish verified source claims from proposed interpretations. Preserve unresolved dissent when evidence does not settle it.
