# Basanos
### Benchmarking LLM Agent Reliability Detection
#### A ReliAgent Validation Study — HDGForge Labs

---

**Basanos** is HDGForge's open benchmarking study for [ReliAgent](https://reliagent.net) — a reliability-monitoring API for LLM agent tool calls. The study validates whether ReliAgent's eight detectors actually detect the failure modes they claim to, using real published benchmarks, live model responses, and purpose-built synthetic harnesses where published instruments don't exist.

All trial-level records, harness code, methodology documentation, and the full audit trail — including superseded runs — are preserved here. Nothing is overwritten after the fact.

---

## What Was Studied

ReliAgent screens agent tool calls for eight failure modes and returns a structured pass/warn/fail verdict on each call:

| Detector | What It Catches |
|---|---|
| `hallucination` | Assertive knowledge claims or hedge language co-occurring with ungrounded numeric values |
| `sycophantic_gap_fill` | Affirmation and subservient-backtracking phrases in tool responses |
| `context_degradation` | Context window nearing capacity; dropped parameter keys across consecutive calls |
| `repetition_loop` | Identical response content recurring within recent call history |
| `confidence_collapse` | Falling or critically low confidence scores; uncertainty language in responses |
| `schema_violation` | Responses that fail validation against a caller-supplied JSON Schema |
| `parameter_drift` | Majority of shared parameter keys changing between consecutive same-tool calls |
| `timeout` | Call latency exceeding caller-supplied, adaptive, or default thresholds |
| `response_integrity` | Structural defects: echo mismatches, contradictory status/error, silent failures, count mismatches |

---

## Study Structure

Basanos ran in two phases:

**Basanos-1 (Pilot)** validated six detectors at pilot scale (5–10 trials each) against real published benchmarks using live Claude Sonnet 5 responses. Its primary purpose was to confirm each detector's actual trigger mechanism before committing to a full harness — a discipline that caught two significant misdesigns before any inference budget was spent on wrong approaches. Two real product defects were identified and corrected during this phase.

**Basanos-2 (Detector Benchmark)** scaled all eight detectors to statistically powered sample sizes. Phase 2 Track A ran N=200 trials (100 clean + 100 violation) per detector across the six pilot-validated detectors against higher-quality sources with programmatic violation injection for auditable ground truth. Phase 2 Track B completed the two remaining detectors and `response_integrity` using purpose-built synthetic harnesses — the correct instrument for structural, non-language-based detectors whose trigger conditions are precisely defined.

**Total trials: 1,800 across all eight detectors.**

---

## Results

| Detector | TPR | FPR | Phase | Source |
|---|---|---|---|---|
| `schema_violation` | 100% | 0% | 2 Track A | JSONSchemaBench Glaiveai2K |
| `hallucination` | 100% | 0% | 2 Track A | ExpertQA |
| `confidence_collapse` | 100% | 0% | 2 Track A | sycophancy-eval |
| `sycophantic_gap_fill` | 100% | 2.3%* | 2 Track A | sycophancy-eval |
| `context_degradation` | 100% | 0% | 2 Track A | Lost in the Middle + synthetic |
| `repetition_loop` | 100% | 0% | 2 Track A | Synthetic hash injection |
| `parameter_drift` | 100% | 0% | 2 Track B | Synthetic two-call sequences |
| `timeout` | 100%† | 0% | 2 Track B | Synthetic latency values |
| `response_integrity` | 100% | 0% | 2 Track B | Synthetic dict payloads |

\* The 2.3% FPR on `sycophantic_gap_fill` reflects common filler words appearing in non-sycophantic contexts in the real dataset — within the expected range for a phrase-pattern detector on natural language.

† `timeout` Mode B (adaptive threshold) recorded 51.5% TPR due to a harness design error: violation latencies were set below the detector's 1000ms adaptive floor. The non-fires are correct product behavior. Modes A (caller-supplied) and C (default 10,000ms) both recorded 100% TPR across 67 combined trials.

All figures reported with 95% Wilson score confidence intervals. See the full report for complete CI tables.

---

## Reports

| Report | Description |
|---|---|
| [`reports/Basanos-1-Pilot.pdf`](reports/Basanos-1-Pilot.pdf) | Phase 1 pilot study — six detectors, mechanism confirmation, two product findings |
| [`reports/Basanos-2-Detector-Benchmark-2026.pdf`](reports/Basanos-2-Detector-Benchmark-2026.pdf) | Full benchmark — all eight detectors, 1,800 trials, complete results |
| [`reports/Basanos-executive-summary.pdf`](reports/Basanos-executive-summary.pdf) | Two-page summary of findings for non-technical readers |

---

## Product Findings

Three genuine product defects were surfaced during Basanos testing and corrected in the live product before publication. See [`changelog/product-fixes.md`](changelog/product-fixes.md) for full details.

**Finding 1 — False pass on unsupported-keyword schemas:** A schema relying entirely on an unsupported JSON Schema keyword (`anyOf`, `oneOf`, `$ref`, etc.) previously returned `"pass"` even when the response clearly violated it. A census of 9,542 real-world schemas found this affected ~12% of real function-calling schemas. Fixed: these schemas now return a distinct `schema_partially_verified` signal.

**Finding 2 — Guaranteed false positives in single-tool environments:** The `repetition_loop` detector included a check for the same tool being called consecutively. In single-tool agent environments (e.g. a coding agent where every call is `bash_exec`), this fired on every call sequence regardless of whether looping was occurring. Fixed: the check was removed. The hash-based check is the correct and sufficient signal.

**Finding 3 — Annotation keywords spuriously flagged:** Annotation-only fields (`description`, `title`, `$schema`, `default`) inside property sub-schemas were treated as unsupported validation keywords, triggering spurious partial-verification warnings on virtually every real-world schema with documented properties. Fixed: annotation keywords are now filtered at every nesting level.

---

## Repository Structure

```
basanos/
│
├── README.md
│
├── reports/
│   ├── Basanos-1-Pilot.pdf
│   ├── Basanos-2-Detector-Benchmark-2026.pdf
│   └── Basanos-executive-summary.pdf
│
├── methodology/
│   ├── methodology.md          # Provenance discipline, mechanism-first approach
│   ├── study-design.md         # Phase 1 and Phase 2 scope decisions
│   ├── statistical-methods.md  # CI calculation, classification approach
│   └── limitations.md          # Documented scope decisions
│
├── datasets/
│   ├── expertqa/               # Rao et al. — hallucination
│   ├── lost-in-the-middle/     # Liu et al. — context_degradation
│   ├── sycophancy-eval/        # Sharma et al. — sycophantic_gap_fill, confidence_collapse
│   └── jsonschemabench/        # Geng et al. — schema_violation
│
├── scenarios/
│   ├── hallucination/
│   ├── sycophantic-gap-fill/
│   ├── context-degradation/
│   ├── repetition-loop/
│   ├── confidence-collapse/
│   ├── schema-violation/
│   ├── parameter-drift/
│   ├── timeout/
│   └── response-integrity/
│
├── harness/
│   ├── runner.py
│   ├── injectors/              # Programmatic violation injection per detector
│   ├── validators/             # Ground truth classification logic
│   └── config/
│
├── results/
│   ├── raw/                    # Per-trial JSON records (experiment_NNN/)
│   ├── processed/
│   ├── trial_records.csv
│   ├── detector_summary.csv
│   └── confidence_intervals.csv
│
├── analysis/
│   ├── notebooks/
│   ├── figures/
│   └── generate_report.py
│
├── changelog/
│   ├── Basanos-1.md            # Phase 1 findings and corrections
│   ├── Basanos-2.md            # Phase 2 findings and corrections
│   └── product-fixes.md        # All three product defects, before/after behavior
│
└── LICENSE
```

---

## Methodology Principles

**Mechanism-first, source-second.** Before building any data pipeline against a published source, direct test calls to ReliAgent were issued to confirm what the detector actually keys on. This caught two significant harness misdesigns before any inference budget was spent on sources that couldn't exercise the real trigger.

**Provenance-labeled.** Every trial states exactly where its input came from. Three categories: published-instrument (direct), published-instrument (indirect), and custom-constructed (synthetic). Nothing is presented as organic real-world behavior unless it is.

**Per-caller isolation.** History-dependent detectors maintain Redis state keyed on `caller_ip`. Independent trials use distinct simulated IPs; multi-turn trials share one IP across their turns.

**No-overwrite convention.** Every experiment run is retained under a numbered directory. Superseded runs are marked, not deleted. The full audit trail — including failed attempts and methodology corrections — is permanently available.

---

## Sources and Citations

- Rao, A. et al. *ExpertQA: Expert-Curated Questions and Attributed Answers.* arXiv:2309.07852
- Rao, A. et al. *Detecting and Correcting Reference Hallucinations in Commercial LLMs and Deep Research Agents.* arXiv:2604.03173
- Yagubyan, A. *How Consistent Are LLM Agents? Measuring Behavioral Reproducibility in Multi-Step Tool-Calling Pipelines.* arXiv:2605.28840
- Liu, N. F. et al. *Lost in the Middle: How Language Models Use Long Contexts.* arXiv:2307.03172. TACL 2024.
- Yang, J. et al. *InterCode: Standardizing and Benchmarking Interactive Coding with Execution Feedback.* arXiv:2306.14898
- Sharma, M. et al. *Towards Understanding Sycophancy in Language Models.* arXiv:2310.13548
- Geng, S. et al. *JSONSchemaBench: A Benchmark for Generating Structured Outputs from Language Models.* arXiv:2501.10868
- International AI Safety Institutes. *International AI Safety Report: Joint Multi-Stakeholder AI Safety Testing Exercise.* arXiv:2601.15679. 2026.

---

## Related

- **[hdgforge-labs/backstop](https://github.com/hdgforge-labs/backstop)** — Benchmarking study for [Redlynr](https://redlynr.com), HDGForge's agent guardrail product
- **[ReliAgent](https://reliagent.net)** — The product under study
- **[HDGForge](https://hdgregory.com)** — HDGForge's product marketplace

---

*Basanos is an open study. All data, code, and methodology are public. If you find an error, open an issue.*

*HDGForge Labs · HD Gregory LLC · 2026*
