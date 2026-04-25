---
name: paper-ideation
description: "Structured reasoning workflow for research/paper work: (1) propose paper ideas from a topic/problem, (2) summarize an existing method/paper, (3) identify gaps/limitations in prior work and turn them into testable research directions, (4) draft positioning/contributions plus an experiment plan. Use when the user asks (often in Chinese/English) for 论文idea/选题、研究gap、related work梳理、方法总结、创新点与实验设计。"
---

# Paper Ideation

## Working Modes (Pick One)

Pick the mode that matches the user request. If ambiguous, ask 1-3 clarifying questions, then proceed.

- `CORPUS`: Read a folder of PDFs -> corpus report (abstract/introduction + gap highlights) -> per-paper cards.
- `IDEATE`: Topic/problem -> candidate paper ideas.
- `SUMMARIZE`: Paper/method -> structured summary and reusable building blocks.
- `DEEPDIVE`: Deep explanation of one paper by combining PDF + open-source code (download if missing) and walking through the full pipeline with concrete examples.
- `GAP`: Prior work map -> actionable gaps and research directions.
- `DIAGNOSE`: User experiment/replication results -> diagnose likely causes + next experiments.
- `SOLVE`: User direction + given data/constraints -> propose multiple feasible solution plans.
- `POSITION`: Idea -> framing, contributions, and experiment matrix.
- `REVIEWER`: Pre-mortem as a critical reviewer.

Output rule: do private reasoning, but only output concise, checkable results (lists, tables, templates). Avoid overlong brainstorming.
Language rule: match the user's language; default to Chinese when the user writes in Chinese.
Initiative rule (important): when the user input is short/vague, actively infer 2-3 plausible interpretations, pick the most likely one, proceed with a concrete draft, and ask for confirmation. If critical information is missing, ask targeted questions and (if browsing is allowed) use web search to fill obvious gaps, citing sources.

## Example Requests (Trigger Phrases)

- "帮我总结这篇论文的方法/贡献/局限，并给出可借鉴的模块。"
- "我对这篇论文很感兴趣，结合 PDF + 开源代码给我讲透：核心模块、数据流、训练/推理 pipeline，用一个具体例子把流程走通。"
- "我在做 X 问题，帮我梳理 related work，找出 5 个可验证的 gap。"
- "基于这个问题陈述，给 5 个论文 idea，并给每个 idea 的最小可验证实验。"
- "读取这个文件夹里所有 PDF，先总结每篇的 abstract/introduction 里怎么论证 gap，再给我一个 prior work map。"
- "这是我复现的结果/ablation，结合你读过的论文帮我判断哪里出了问题，下一步该做什么实验。"
- "我想解决方向 Y，在我给定的数据和约束下，给多个可行方案并排出优先级。"
- "把这个想法变成一页 paper pitch：贡献点 + 实验矩阵 + 风险。"
- "你扮演审稿人，挑 novelty、baseline、实验设计的问题并给补救实验。"

## Minimal Intake (Ask Only If Missing)

Ask the smallest set of questions needed to avoid hallucinating context.

- Problem/task: input, output, constraints (latency/compute/data/privacy).
- Target setting: domain, users, deployment, failure costs.
- Baselines/prior work: 3-8 key papers/systems (titles or links).
- Evaluation: datasets, metrics, stress tests, ablations.
- Goal: novelty type (algorithmic, system, theory, data, evaluation).
- Practical constraints: timeline, compute budget, reproducibility expectations.

If the user provides a paper PDF/text/notes, prefer `SUMMARIZE` first, then `GAP`.

## Workflow: CORPUS (Folder of PDFs -> Corpus Report)

Goal: quickly build a reliable "what did these papers claim and what gap did they motivate?" report from a local folder of PDFs, then use it as the basis for `GAP`/`IDEATE`/`DIAGNOSE`.

1. Ask for the folder path and any constraints:
   - "哪些 PDF 需要排除？是否有重点方向/关键词？"
   - "是否只需要 abstract + introduction？最大每篇读几页？"
2. Run the PDF scan script to extract structured snippets:
   - Preferred (if system python lacks PDF deps): `scripts/pdf_corpus_scan.sh --folder <dir> --out <report.md> --jsonl <papers.jsonl>`
   - Direct: `python scripts/pdf_corpus_scan.py --folder <dir> --out <report.md> --jsonl <papers.jsonl>`
   - If extraction fails due to missing deps, install `pypdf` in a conda env and re-run:
     - Example: `/home/ubuntu/.codex/miniconda3/bin/conda run -n multi-agent python -m pip install pypdf`
3. Present the corpus report to the user:
   - A table of papers (file, title guess, abstract found, intro found)
   - For each paper: Abstract snippet, Introduction gap sentences (heuristic), and a short "likely contribution" bullet list (label as tentative if not fully supported by text)
4. Confirm scope and proceed:
   - If user asks for a map/gaps: continue with `GAP`.
   - If user asks for ideas: continue with `IDEATE` using the extracted gaps.
   - If user has results: continue with `DIAGNOSE` and link observed behavior to the corpus.

## Workflow: IDEATE (Topic -> Ideas)

1. Restate the problem in 2-3 lines (task + constraints + why it matters).
2. List 5-10 idea axes (use only what fits the domain):
   - Objective: what to optimize vs what is currently optimized?
   - Data: scarcity, noise, shifts, labels, multimodality.
   - Assumptions: what current methods assume that can be relaxed?
   - Compute: inference/training cost, memory, latency, edge constraints.
   - Robustness: distribution shift, adversarial, OOD, calibration.
   - Interpretability/safety: explainability, controllability, safety constraints.
   - Evaluation: missing stress tests, unrealistic benchmarks, leakage.
   - Deployment: product constraints, monitoring, feedback loops.
3. Propose 5-8 candidate ideas. For each, include:
   - One-line thesis
   - Key mechanism (what is new)
   - Why now (recent enablers)
   - Expected upside and the main risk
   - Minimum viable experiment (MVE): dataset/metric/baseline
4. Rank top 3 by: novelty, feasibility, expected impact, evidence strength.
5. Produce a "1-page idea brief" for the top 1-2.

### Output Template: 1-Page Idea Brief

Use this structure:

1. Title (working)
2. Problem + pain point (3-5 bullets)
3. Prior work snapshot (3-6 bullets: what it solves, what it misses)
4. Core idea (3-6 bullets)
5. Hypotheses (2-4, testable)
6. Method sketch (pseudo-steps or block diagram in text)
7. Experiments (table)
8. Failure modes + mitigations (3-6 bullets)
9. What would falsify this (clear criteria)

## Workflow: SUMMARIZE (Paper/Method -> Structured Summary)

Inputs: paper text/notes (preferred) or the user’s description.

Produce:

- 5-line abstract: problem, key idea, method, results, takeaway.
- Contribution list (max 5).
- Method details: objective, architecture/algorithm steps, training/inference, complexity.
- Experimental setup: datasets, metrics, baselines, ablations.
- Strengths (3-6) and weaknesses/assumptions (3-8).
- "Repro checklist": what is missing/unclear to reproduce.
- Reusable building blocks (what could be borrowed for new work).

## Workflow: DEEPDIVE (Paper + Code -> Explain Full Pipeline)

Goal: produce a detailed, faithful, end-to-end explanation by aligning the paper's method with the open-source implementation and walking through a concrete example pipeline.

Inputs (best-effort; proceed with partial information):

- Paper PDF path (preferred) or the paper title + link.
- Code repo:
  - If the user provides a local path, use it.
  - If the paper mentions code but it's not local, find the official repo (prefer links extracted from PDF or official project page), then download/clone it.

Process:

1. Confirm scope: what depth the user wants (high-level, algorithm-level, code-level, reproduce-level).
2. Extract paper anchors (from PDF):
   - Problem setup + assumptions
   - Core algorithm/module list (name the modules as described in the paper)
   - Training loop and inference loop
   - Claimed ablations and what each is testing
3. Locate or obtain the code:
   - Check local for repo folder or zip.
   - If missing: search for official code link (prefer links found in the PDF/corpus report); then download it:
     - Preferred helper: `scripts/fetch_repo.sh --url <repo_or_zip_url> --dest-root repos`
     - Or do it manually via `git clone` / `wget` (avoid random forks; prefer official org/author repo).
   - If no official code is discoverable (paper has no link; search yields nothing), say so explicitly and continue in one of two ways:
     - Paper-only deepdive (faithful explanation + pseudocode + suggested module boundaries).
     - Proxy deepdive using a closest-available local/open-source codebase (clearly label it as a reference scaffold, not the paper's original implementation).
4. Build a codebase map (fast triage):
   - Identify entrypoints (train/eval scripts, CLIs) and config system (argparse/hydra/yaml).
   - Identify core modules (model, data, loss, trainer, inference).
   - Use `scripts/codebase_map.sh --repo <path> --out <map.md>` to generate a deterministic map.
5. Align paper <-> code:
   - Create a table mapping each paper module/step to file paths + functions/classes.
   - Call out implementation differences and missing details (do not hand-wave).
6. Explain the full pipeline with a concrete example:
   - Choose the simplest representative task/example from the repo (or create a toy input).
   - Walk through: input -> preprocessing -> forward pass -> loss -> update -> evaluation -> output artifact.
   - Include concrete config values/CLI args as shown in the repo.
7. Summarize "core modules" and "what to change" guidance:
   - Which 2-4 files to edit for: new dataset, new model variant, new loss, new topology, etc.
8. Optional: reproduce smoke run
   - If dependencies are manageable, run a minimal command (1-5 minutes) and report any gotchas.

Output format:

- `Conceptual overview` (<= 10 bullets)
- `Pipeline walkthrough` (step-by-step, with code pointers)
- `Paper <-> code mapping table`
- `Core modules and extension points`
- `Repro notes and pitfalls` (missing seeds, configs, preprocessing mismatch, evaluation traps)

### Output Template: Method Summary Card

1. Citation (if provided) + 1-line positioning
2. Problem + setting
3. Key idea (plain language)
4. Technical core (steps/equations in words)
5. What it changes vs baselines
6. Evidence (main results)
7. Assumptions / limitations
8. If I had 1 day to extend it: 3 extension directions

## Workflow: GAP (Prior Work -> Gaps -> Directions)

1. Build a "prior work map" table (6-12 rows):
   - Paper/system
   - Setting (data, constraints)
   - Core technique
   - What it measures
   - Where it wins
   - Likely blind spot
2. Extract 8-15 gaps. Each gap must include:
   - Evidence: which prior work suggests this gap exists
   - Scope: when it matters (avoid universal claims)
   - Why it’s non-trivial (why not already solved)
3. Convert the top 3-5 gaps into research directions:
   - Hypothesis
   - Proposed approach families (2-3)
   - Minimum viable experiment
   - Risk and fallback

### Output Template: Gap List (Actionable)

Table columns:

1. Gap statement (specific)
2. Evidence (papers/observations)
3. Who cares (impact)
4. Hypothesis
5. Proposed approach (1-2 sentences)
6. MVE (dataset/metric/baseline)
7. Main risk
8. Success criteria

## Workflow: POSITION (Idea -> Framing + Experiments)

1. Positioning:
   - What problem slice do we own?
   - What is the baseline story we beat?
   - What is the "simple but strong" baseline we must include?
2. Contributions (3-5 bullets, each: claim + evidence plan).
3. Experiment matrix:
   - Rows: claims/hypotheses
   - Columns: datasets, metrics, baselines, ablations, stress tests
4. Writing skeleton:
   - Intro: hook -> gap -> approach -> contributions
   - Method: design choices justified
   - Experiments: claim-driven
5. Deliverables: code release plan, reproducibility notes.

### Output Template: Experiment Matrix

Use a compact table:

- `Claim/Hypothesis`
- `Metric`
- `Dataset(s)`
- `Baselines`
- `Ablations`
- `Stress tests`
- `Expected outcome`
- `If negative, next move`

## Workflow: REVIEWER (Pre-mortem)

Generate:

- 8-12 reviewer questions (novelty, assumptions, evaluation, baselines, efficiency).
- Best-faith answers grounded in proposed evidence (no hand-waving).
- Missing experiments likely requested.
- "Killer baseline" candidates you must test against.

## Quality Bar (Non-negotiable)

- Never invent citations, datasets, or claimed SOTA numbers.
- If a fact is uncertain, label it as an assumption and ask for confirmation.
- Prefer specific, testable hypotheses over vague novelty claims.
- Keep outputs structured and brief; prioritize the top few high-leverage items.

## Workflow: DIAGNOSE (Results -> Likely Causes -> Next Experiments)

Inputs (accept partial, but ask for missing critical info):

- Task + dataset + split details
- Model/training recipe (optimizer, lr schedule, steps, batch, augmentation)
- Compute constraints (GPU, time)
- Key results table (main metric, variance, seed count)
- Any surprising logs (loss curves, gradient norms, calibration, failure cases)

Process:

1. Normalize results into a "Result Card" (below).
2. Compare against corpus expectations:
   - What the paper claims should matter (ablations/hypotheses)
   - Hidden assumptions that might not hold in user setting
3. Generate 5-10 candidate causes, grouped by:
   - Data pipeline issues
   - Evaluation leakage/mismatch
   - Training instability / hyperparameters
   - Implementation mismatches vs paper
   - Distribution shift / task mismatch
4. Propose next experiments prioritized by information gain:
   - 3 quick sanity checks (hours)
   - 3 medium tests (1-2 days)
   - 1-2 deeper re-thinks (week)
5. If the user input is very short, proceed with a default diagnostic checklist and ask for the minimum missing items.

### Output Template: Result Card

- Setting:
- Baseline(s):
- Your variant:
- Main metric(s):
- Key deltas vs baseline:
- Confidence (seeds/CI):
- Notable failure cases:
- Suspected mismatch vs paper:

## Workflow: SOLVE (Direction -> Multiple Feasible Solution Plans)

Inputs:

- Direction statement (even 1 sentence is OK)
- Given data (size, labels, modality, privacy)
- Constraints (latency, memory, training budget)

Process:

1. Expand the direction into 2-3 concrete problem formulations (if ambiguous).
2. Enumerate solution families (at least 4), mixing:
   - "Simple strong baseline" upgrades
   - Method tweaks inspired by the corpus
   - Alternative modeling or objective choices
   - Data-centric approaches (cleaning, labeling, augmentation, distillation)
3. For each plan, output:
   - Mechanism and why it should work here
   - Required changes (data/model/training)
   - Risk and likely failure modes
   - MVE and success criteria
4. Rank by feasibility x expected gain, and recommend the top 1-2 with a 2-week execution plan.
