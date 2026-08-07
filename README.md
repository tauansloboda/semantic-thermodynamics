UPDATE (August 2026): Added the full formalization paper covering Phase Space Collapse, Structural Friction, and the Entropic Proportionality Law.

# Semantic Thermodynamics: LLM Entropy Minimization

This repository contains the foundational whitepaper, execution scripts, and raw empirical data for the **Semantic Thermodynamics** framework.

## The Premise
Large Language Models operate as Bayesian inference engines. In environments with high semantic entropy, they expend excess compute mapping infinite phase spaces. By applying "Narrative Gravity"—a precise formula of persona, teleological vectors, and destructive pruning—we can force the model into a deterministic geodesic, drastically reducing cost and latency.

## Empirical Results (Experiment Zero)
By restructuring a standard data-extraction prompt using the **Formula v2.0**, we observed:
- **79.29% reduction** in completion tokens.
- **60.73% reduction** in system latency (from 3.4s to 1.3s).

## Repository Contents
- `Semantic_Thermodynamics_Whitepaper.pdf`: The complete theoretical framework and the Law of Entropic Proportionality ($\Lambda$).
- `experimento_zero.py`: The async Python script used to benchmark the token and latency collapse.
- `experimento_um.py`: The script mapping the "Structural Friction" and the optimal semantic gradient.
- `*.csv`: Raw telemetry data from the OpenAI API runs.

## How to Test the Physics
1. Clone this repo.
2. `pip install openai`
3. Export your API key: `export OPENAI_API_KEY="sk-..."`
4. Run `python experimento_zero.py` and watch the latency drop.

*Author: Tauan Vinicius Guahyba Sloboda*
