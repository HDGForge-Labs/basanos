# Basanos
### Benchmarking LLM Agent Reliability Detection
#### A ReliAgent Validation Study — HDGForge Labs

**Basanos** is HDGForge Labs' open validation program for [ReliAgent](https://reliagent.net), a reliability-monitoring API for LLM agent tool calls.

Across Basanos-2 and Basanos-3, the program comprises **4,200 trials**: 1,800 trials validating ReliAgent's detector suite in Basanos-2, followed by 2,400 cross-model trials in Basanos-3 addressing the earlier study's single-model limitation.

## Study progression

### Basanos-1 — Pilot

The pilot established detector trigger mechanisms before the larger benchmark and surfaced product and harness findings that informed the later studies.

### Basanos-2 — Detector Benchmark

Basanos-2 evaluated ReliAgent's implemented failure-mode detectors across **1,800 trials** using Claude Sonnet 5, published benchmark sources where appropriate, and purpose-built synthetic inputs for structural detectors with precisely defined trigger conditions.

The study covered ReliAgent's reliability checks for hallucination signals, sycophantic gap fill, confidence collapse, context degradation, repetition loops, schema/response integrity behavior, parameter drift, and timeout behavior.

### Basanos-3 — Cross-Model Detector Benchmark

Basanos-3 addressed the explicit single-model limitation of Basanos-2. It ran **2,400 trials across 12 experiments** using three additional model families:

- GPT-5.6 Luna — OpenAI
- GPT-5.6 Terra — OpenAI
- Claude Haiku 4.5 — Anthropic

The cross-model phase focused on four detectors with language- or model-dependent behavior: `hallucination`, `sycophantic_gap_fill`, `confidence_collapse`, and `context_degradation`.

## Basanos-3 results

| Detector | Model | TPR | FPR | Interpretation of non-fires |
|---|---|---:|---:|---|
| hallucination | GPT-5.6 Luna | 0.76 | 0.00 | Grounded, unhedged responses |
| hallucination | GPT-5.6 Terra | 0.84 | 0.00 | Grounded, unhedged responses |
| hallucination | Claude Haiku 4.5 | 0.97 | 0.00 | Grounded, unhedged responses |
| sycophantic_gap_fill | GPT-5.6 Luna | 0.92* | 0.00 | Model gave non-sycophantic responses |
| sycophantic_gap_fill | GPT-5.6 Terra | 0.89 | 0.01 | Model gave non-sycophantic responses |
| sycophantic_gap_fill | Claude Haiku 4.5 | 0.41 | 0.00 | Model pushed back rather than capitulating |
| confidence_collapse | GPT-5.6 Luna | 1.00 | 0.00 | — |
| confidence_collapse | GPT-5.6 Terra | 1.00 | 0.00 | — |
| confidence_collapse | Claude Haiku 4.5 | 1.00 | 0.00 | — |
| context_degradation | GPT-5.6 Luna | 1.00 | 0.00 | — |
| context_degradation | GPT-5.6 Terra | 1.00 | 0.00 | — |
| context_degradation | Claude Haiku 4.5 | 1.00 | 0.00 | — |

*Luna sycophancy TPR is reported from two independent runs (0.92 and 0.91 in the technical report).

### How to interpret the TPR variation

Basanos-3 does **not** measure how often a model naturally produces a failure mode in ordinary deployment. It tests whether ReliAgent fires when its defined trigger condition occurs under the study elicitation.

Response-level inspection of missed violation trials found that the model had not produced the relevant trigger signal. For example, Haiku's 0.41 `sycophantic_gap_fill` TPR reflects 41 trials in which sycophantic language occurred and was detected; on the remaining 59 trials, Haiku pushed back rather than capitulating.

The central Basanos-3 finding is therefore that the evaluated detectors fired correctly on every inspected instance in which their defined trigger condition was present across the three tested model families. False-positive rates were at or near zero in the 12 experiments.

## Deployment findings from Basanos-3

Two methodology findings have direct deployment implications:

- **Unicode normalization:** OpenAI reasoning models can emit typographic punctuation that does not match ASCII phrase patterns. Cross-provider operators should normalize response text before regex-based detection.
- **Hallucination opt-in path:** the hallucination detector's hedge-plus-numeric path requires `response_grounded_in_parameters=True`.

The two metadata-driven detectors in this phase, `confidence_collapse` and `context_degradation`, achieved TPR=1.0 and FPR=0.0 across all three tested model families because their primary signals are caller-supplied metadata rather than model-specific linguistic content.

## Data integrity and audit trail

Basanos uses a no-overwrite convention. Superseded experiments remain part of the audit trail rather than being silently replaced.

During Basanos-3 analysis, two experiment-assignment errors were identified. Corrective experiments 031 and 032 were run, and the canonical experiment set is documented in the technical report. The superseded run remains documented.

## Basanos-2 findings

Basanos-2 also served as adversarial product validation rather than a confirmation-only exercise. Testing surfaced genuine product issues, including unsupported JSON Schema keyword handling, repetition-loop behavior in single-tool environments, and annotation-keyword handling. Those findings were corrected before publication and are documented in the Basanos materials.

## Reports

The repository currently contains the Basanos-1 and Basanos-2 reports. Basanos-3 is the current cross-model phase; its technical report and executive summary should be added to this `reports/` directory so the repository and published study remain synchronized.

Current repository reports:

- [`reports/Basanos-1-Pilot.pdf`](reports/Basanos-1-Pilot.pdf) — pilot study
- [`reports/Basanos-2-Detector-Benchmark-2026.pdf`](reports/Basanos-2-Detector-Benchmark-2026.pdf) — 1,800-trial detector benchmark
- [`reports/Basanos-executive-summary.pdf`](reports/Basanos-executive-summary.pdf) — Basanos-2 executive summary

## Public results currently in this repository

The `results/` directory contains the published Basanos-2 summary artifacts:

- [`results/trial_records_summary.csv`](results/trial_records_summary.csv)
- [`results/detector_summary.csv`](results/detector_summary.csv)
- [`results/confidence_intervals.csv`](results/confidence_intervals.csv)

Basanos-3 trial-level records and harness artifacts should be added alongside the Basanos-3 reports if they are not already present elsewhere in the repository history.

## Research principles

Basanos is organized around several principles:

- **Mechanism first:** confirm what a detector actually keys on before committing inference budget to a benchmark source.
- **Explicit provenance:** distinguish published-instrument, controlled, and synthetic inputs rather than presenting them as equivalent.
- **State isolation:** independent trials use isolated caller identity/state where history-dependent detectors require it.
- **No overwrite:** retain superseded runs and corrective experiments so the audit trail remains inspectable.
- **Scope discipline:** report what the experiment actually validates and distinguish detector behavior from model behavior.

## Related

- [ReliAgent](https://reliagent.net) — product under study
- [Backstop](https://github.com/HDGForge-Labs/backstop) — Redlynr validation study
- [Redlynr](https://redlynr.com) — runtime agent guardrails
- [HDGForge](https://hdgforge.com) — HDGForge

---

*Basanos is an HDGForge Labs validation program. If you find an error in the published materials, open an issue.*

*HDGForge Labs · HD Gregory LLC · 2026*
