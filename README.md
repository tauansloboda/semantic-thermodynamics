# Semantic Thermodynamics

### Narrative structure as an infrastructure variable for Large Language Models

This repository contains the papers, source code, raw telemetry, and reproducibility artifacts for **Semantic Thermodynamics**, an experimental framework for studying how semantic constraint affects inference cost, latency, output entropy, and reliability in Large Language Models.

The central engineering premise is simple:

> **Prompt structure is not merely an interface concern. It changes the computational behavior of inference.**

The research program studies this relationship through **Narrative Gravity**, **Narrative Pruning**, **Structural Friction**, and the **Law of Entropic Proportionality**.

The repository now includes the complete results and publication artifacts for **Experiment Two: The Battle of Architectures**.

---

## Research Series

### Paper I — Semantic Thermodynamics: A Framework for LLM Entropy Minimization

The foundational paper introduces Semantic Thermodynamics and the Narrative Gravity framework.

Experiment Zero compared a high-entropy baseline against a semantically constrained request over 100 API calls.

**Result:**

- **79.29% reduction in completion tokens**
- **60.73% reduction in mean end-to-end latency**
- identical material answer across both conditions
- collapse from 50 distinct textual realizations to a single realization under the optimized condition

The experiment established that additional semantic structure can increase prompt length while dramatically reducing downstream generation.

---

### Paper II — The Collapse of Phase Space: Narrative as an Operational Thermodynamic Quantity in Inference Pruning

The second paper investigates the **entropic gradient**.

Experiment One progressively increased narrative constraint density and found that efficiency does not improve monotonically.

For a low-entropy extraction task, the optimum occurred under **Light Gravity**, not under maximum constraint.

Beyond the optimum, redundant instructions, conflicting rules, auxiliary objectives, and output complexity produced **Structural Friction**.

This led to the operational formulation of the **Law of Entropic Proportionality**:

> **Optimal structure is not maximal. It is proportional.**

The paper formalizes Narrative Pruning as the reduction of effective output phase space before the executor materializes its response.

---

## Paper III — The Battle of Architectures

### Static Instruction Accumulation versus Dynamic Semantic Routing in Enterprise LLM Extraction

The third experiment moves Semantic Thermodynamics from prompt-level optimization to **system architecture**.

Instead of comparing individual prompt formulations, Experiment Two compares two complete inference architectures.

### Route A — Static Instruction Accumulation

A single `gpt-4o-2024-11-20` inference receives:

- a synthetic **8,192-token corporate System Prompt**;
- a noisy user request;
- a deliberately chaotic enterprise email thread.

The System Prompt simulates the accumulation of generic enterprise instructions around safety, compliance, privacy, legal caution, formatting, tone, auditability, and exception handling.

It is a synthetic experimental stressor and is **not presented as a reproduction or estimate of any company's proprietary production System Prompt**.

### Route B — Dynamic Semantic Routing

A two-stage architecture:

**1. Semantic Micro-Router**

`gpt-4o-mini-2024-07-18`

The router receives only the noisy user request and compiles it into a compact Narrative Gravity formula containing:

- Persona
- Objective
- Scope
- Negative Constraints
- Output Matrix

**2. Executor**

`gpt-4o-2024-11-20`

The executor receives only:

- the dynamically generated semantic formula;
- the source email thread.

The large model therefore begins inference inside a task-specific semantic field instead of carrying a large generic policy layer.

---

## Experiment Two — Results

The final experiment completed **50 preregistered paired observations**.

### Token Consumption

Route A:

**10,282.28 mean total tokens per pipeline**

Route B:

**2,624.84 mean total tokens per pipeline**

**Route B reduced total token consumption by 74.47%.**

It used fewer total tokens in **50/50 paired observations**.

---

### Cost

With observed prompt caching:

- Route A: **US$0.0136206 per extraction**
- Route B: **US$0.0044209 per extraction**

**Route B reduced cost by 67.54%.**

Without prompt caching:

- Route A: **US$0.0260078**
- Route B: **US$0.0054961**

**Route B reduced cost by 78.87%.**

The dynamic architecture remained substantially cheaper even though it paid for an additional micro-router inference.

---

### Material Accuracy

Normalized material accuracy:

- Route A: **36/50 — 72%**
- Route B: **50/50 — 100%**

Route A produced **14 material extraction failures**.

Route B produced **zero**.

Dynamic routing therefore improved cost and quality simultaneously.

---

### Service Latency

Route A retained the expected one-hop advantage:

- Route A: **2.257 s mean service latency**
- Route B: **3.246 s**

Route B performs two sequential inferences and therefore pays an additional service-latency cost.

However, its p95 service latency was lower:

- Route A: **6.383 s**
- Route B: **4.359 s**

---

### Operational Latency

Under the project's actual token-rate constraints:

- Route A: **24.202 s mean operational wall time**
- Route B: **3.284 s**

**Route B reduced operational wall time by 86.43%.**

The difference emerged because the large static request repeatedly approached the project's token-per-minute envelope and required admission control.

---

## The Experiment That Failed First

Experiment Two produced an important result before the final controlled run even began.

The original architecture launched both routes without rate-aware admission control.

Across 150 attempted API calls:

- **69 calls failed with HTTP 429**
- Route A completed only **3/50** final calls
- Route B's micro-router completed **50/50**
- Route B's executor completed **28/50**
- only **2/50 complete A/B pairs** survived

Route A injected approximately **10K prompt tokens in a single atomic request**, rapidly exhausting the available token-per-minute capacity.

The final experiment therefore introduced a rate-limit governor that converted rejection into explicit admission waiting.

This allowed all 50 pairs to complete while preserving the infrastructure burden as a measured variable.

The governor did not make the static architecture efficient.

**It prevented it from collapsing.**

---

## Prompt Caching Does Not Remove Structural Friction

Route A achieved an exceptional **96.756% prompt-cache ratio**.

Only 332.24 of its 10,242 average prompt tokens were uncached.

Yet Route A remained **3.08× more expensive** than Route B.

Under a no-cache counterfactual, it became **4.73× more expensive**.

Caching discounts repeated input.

It does not remove that input from the model's semantic field.

This distinction is central to Semantic Thermodynamics: reducing the price of context is not equivalent to reducing the inference space created by that context.

---

## Semantic Control ≠ Syntactic Control

Experiment Two also exposed a clean architectural boundary.

Route B achieved:

**50/50 normalized material accuracy**

but only:

**3/50 native JSON adherence**

Most remaining failures consisted solely of Markdown code fences around otherwise correct JSON.

This separates two different engineering problems:

**Semantic routing controls what the model should compute.**

**Structured decoding controls how the result must be serialized.**

The next experimental stage combines:

> **Dynamic Semantic Routing + Structured Decoding**

rather than forcing natural-language instructions to perform both functions.

---

## Reproducibility Package

This release includes the complete **Experiment Two publication bundle**.

The ZIP archive contains the experimental provenance required to audit and reproduce the run, including:

- experiment source code
- dependency specification
- README
- methodology
- preregistration
- data dictionary
- source documentation
- exact chaotic email thread
- exact chaotic user request
- exact 8,192-token synthetic System Prompt
- exact micro-router System Prompt
- gold standard
- experiment configuration
- request architecture
- environment metadata
- pre-run manifest
- raw API attempt journal
- rate-limit event log
- all generated router formulas
- all final model outputs
- primary results CSV
- paired-results CSV
- aggregate metrics
- machine-readable analysis summary
- publication figures
- complete Markdown experiment report
- SHA-256 provenance manifest

The publication bundle is intended to make the experiment **inspectable, reproducible, and falsifiable**.

---

## Recommended Files to Inspect First

If you do not want to unpack the full publication bundle, start with:

**`experiment_two_results.csv`**  
The 100 final observations: 50 Route A and 50 Route B.

**`paired_results.csv`**  
The 50 direct paired comparisons and B−A deltas.

**`god_prompt.txt`**  
The exact synthetic 8,192-token System Prompt used by Route A.

**`experiment_two.py`**  
The complete experimental implementation.

**`experiment_two_report.md`**  
The automatically generated analysis of the completed run.

For complete provenance, use the ZIP archive.

---

## Repository Structure

A suggested repository layout is:

```text
semantic-thermodynamics/
│
├── README.md
│
├── papers/
│   ├── semantic_thermodynamics.pdf
│   ├── collapse_of_phase_space.pdf
│   └── battle_of_architectures.pdf
│
├── experiment_zero/
│   ├── experiment_zero.py
│   └── experiment_zero_results.csv
│
├── experiment_one/
│   ├── experiment_one.py
│   └── experiment_one_results.csv
│
└── experiment_two/
    ├── experiment_two.py
    ├── experiment_two_results.csv
    ├── paired_results.csv
    ├── god_prompt.txt
    ├── experiment_two_report.md
    └── experiment_two_publication_bundle.zip
```

The ZIP contains the complete Experiment Two directory tree and should be treated as the canonical reproducibility package for that experiment.

---

## Reproducing Experiment Two

Install the dependencies:

```bash
pip install -r requirements.txt
```

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="..."
```

Then execute the experiment according to the instructions included in the publication bundle.

Running the full benchmark performs paid API calls.

Rate limits, model availability, pricing, prompt caching behavior, and infrastructure conditions may differ across accounts and execution dates. The exact model snapshots and experiment configuration used for the published run are preserved in the artifacts.

---

## Experimental Integrity

The English publication run completed:

- **50/50 measured pairs**
- **100 final observations**
- **150 measured model calls**
- **6 warm-up calls**
- **0 HTTP 429 responses during the governed run**
- **0 retries**
- **36/36 publication hashes validated**

Two successful Route B executor calls were absent from the append-only raw-attempt journal. Their request IDs, outputs, token telemetry, costs, latencies, and hashes remained preserved and independently cross-validated in the primary artifacts.

No missing raw headers were reconstructed.

The 100 final observations and all paired experimental results remain complete.

---

## Current Result

Across the three experiments, the same engineering principle has now appeared at three different levels:

**Experiment Zero:** semantic constraint can reduce inference output and latency.

**Experiment One:** constraint has an optimum; excessive constraint creates Structural Friction.

**Experiment Two:** dynamically generating the appropriate constraint field can outperform carrying a large static instruction field through every inference.

Semantic Thermodynamics therefore moves the optimization target away from prompt length alone.

The relevant variable is the relationship between:

**task entropy → constraint density → inference behavior → infrastructure cost**

Or, more simply:

> **The cheapest token is not merely the token you avoid sending. It is the branch of inference you prevent from becoming computationally relevant.**

---

## Author

**Tauan Vinicius Guahyba Sloboda**

Semantic Thermodynamics Research Series
