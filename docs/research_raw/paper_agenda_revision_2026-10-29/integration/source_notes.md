# Additional methodological sources and decisions

Inspected primary sources on 29 October 2026:

- AgentBoard, NeurIPS 2024 Datasets and Benchmarks paper, https://proceedings.nips.cc/paper_files/paper/2024/file/877b40688e330a0e2a3fc24084208dfa-Paper-Datasets_and_Benchmarks_Track.pdf. The abstract and introduction motivate incremental progress measurement rather than final success alone. The current manuscript already cites the correct paper. Our plan-follow-through study must define its own endpoints; AgentBoard's progress metric is not automatically a Monopoly utility metric.
- Agarwal et al., Deep Reinforcement Learning at the Edge of the Statistical Precipice, NeurIPS 2021, https://proceedings.neurips.cc/paper_files/paper/2021/file/f514cec81cb148559cf475e7426eed5e-Paper.pdf. The abstract and introduction explain uncertainty from few independent runs and distinguish aggregate performance from point-estimate comparisons. This supports explicit dependence and uncertainty reporting, not treating the five seed blocks as an adequate iid sample or importing an estimator without its assumptions.

The screenshot paper lists remain leads, not an externally verified reference list. No novelty claim is based on those lists.

## Sampling correction

The original common sample contains three deterministic SHA-selected public-unflagged decisions per player-game. The earlier 200 ordinary / 40 notable labels describe a review outcome, not sampling strata. The new temporal study reads all 240 selected applied/public fields and preserves the original selection metadata. Its codebook is new and exploratory, and the original preselection itself depends on the earlier public extraction. It is not a random sample of every decision or every claim.

## Authorization and preservation

The user authorized paper improvement and team work after the read-only guidance assessment. No paid OpenRouter budget has yet been supplied. Existing saved-game analyses and separate CPU-only diagnostic pilot games are authorized within this work; provider-query and prompt-intervention arms remain unrun. The old manuscript is preserved in ../baseline. The original outline, prior literature review, canonical game artifacts, engine and model-facing production prompts remain unchanged.
