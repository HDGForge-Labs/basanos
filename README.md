# Basanos
### Benchmarking LLM Agent Reliability Detection
#### A ReliAgent Validation Study — HDGForge Labs

**Basanos** is HDGForge Labs' validation program for [ReliAgent](https://reliagent.net), a reliability-monitoring API for LLM agent tool calls.

Across Basanos-2 and Basanos-3, the program comprises **4,200 trials**: 1,800 trials validating ReliAgent's detector suite in Basanos-2, followed by 2,400 cross-model trials in Basanos-3 addressing the earlier study's single-model limitation.

## Study progression

### Basanos-1 — Pilot

The pilot established detector trigger mechanisms before the larger benchmark and surfaced product and study-design findings that informed the later studies.

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
| hallucination | GPT-5.6 Luna | 0.76 | 0.00 | Grounded responses without the evaluated signal |
| hallucination | GPT-5.6 Terra | 0.84 | 0.00 | Grounded responses without the evaluated signal |
| hallucination | Claude Haiku 4.5 | 0.97 | 0.00 | Grounded responses without the evaluated signal |
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

Basanos-3 does **not** measure how often a model naturally produces a failure mode in ordinary deployment. It evaluates ReliAgent against defined study conditions and then distinguishes detector behavior from model behavior when interpreting non-fires.

Response-level inspection found that many missed violation trials reflected the model not producing the relevant failure-mode signal. For example, Haiku's lower `sycophantic_gap_fill` rate primarily reflected the model pushing back rather than capitulating.

The central Basanos-3 finding is that the evaluated detectors performed consistently when the relevant study signal was present across the tested model families. False-positive rates were at or near zero in the 12 experiments.

## Deployment findings from Basanos-3

The cross-model phase identified two practical deployment considerations:

- **Cross-provider normalization:** provider-specific output-format differences can require normalization for consistent evaluation across model families.
- **Configuration sensitivity:** testing identified a configuration dependency affecting one evaluated detector path; deployment guidance was updated accordingly.

The two metadata-driven detectors in this phase, `confidence_collapse` and `context_degradation`, achieved TPR=1.0 and FPR=0.0 across all three tested model families.

## Data integrity and audit trail

Basanos uses a no-overwrite convention in its internal research record. Superseded experiments and corrective runs are retained in the study archive rather than silently replaced.

During Basanos-3 analysis, experiment-assignment errors were identified and corrective experiments were run. The canonical experiment set and corrections are documented in the technical report.

## Basanos-2 findings

Basanos-2 also served as adversarial product validation rather than a confirmation-only exercise. Testing surfaced genuine product issues that were corrected before publication and are documented in the Basanos reports.

## Reports

Public study reports currently available in this repository:

- [`reports/Basanos-1-Pilot.pdf`](reports/Basanos-1-Pilot.pdf) — pilot study
- [`reports/Basanos-2-Detector-Benchmark-2026.pdf`](reports/Basanos-2-Detector-Benchmark-2026.pdf) — 1,800-trial detector benchmark
- [`reports/Basanos-executive-summary.pdf`](reports/Basanos-executive-summary.pdf) — Basanos-2 executive summary
- [`reports/Basanos-3-Cross-Model-Benchmark-2026.docx`](reports/Basanos-3-Cross-Model-Benchmark-2026.docx) — 2,400-trial cross-model benchmark
- [`reports/Basanos-3-Executive-Summary-2026.docx`](reports/Basanos-3-Executive-Summary-2026.docx) — Basanos-3 executive summary

## Public results

The `results/` directory contains non-reconstructive research summaries intended to support inspection of the published findings without disclosing proprietary implementation, benchmark harnesses, elicitation procedures, or internal test strategy.

- [`results/trial_records_summary.csv`](results/trial_records_summary.csv) — sanitized Basanos-2 trial-level summary fields
- [`results/detector_summary.csv`](results/detector_summary.csv) — Basanos-2 detector summary
- [`results/confidence_intervals.csv`](results/confidence_intervals.csv) — Basanos-2 confidence-interval summary
- [`results/detector_summary_b3.csv`](results/detector_summary_b3.csv) — Basanos-3 aggregate cross-model results

HDGForge Labs intentionally does not publish proprietary application source code, benchmark harness implementation, internal test procedures, or other artifacts that could disclose ReliAgent implementation details or proprietary research methods.

## Research principles

Basanos is organized around several principles:

- **Mechanism first:** establish what an evaluation is intended to test before committing inference budget.
- **Explicit provenance:** distinguish published-instrument, controlled, and synthetic inputs rather than presenting them as equivalent.
- **State isolation:** independent trials are isolated where history-dependent evaluation requires it.
- **No overwrite:** preserve study corrections and superseded runs in the internal research record.
- **Scope discipline:** report what the experiment actually validates and distinguish detector behavior from model behavior.
- **Evidence without implementation disclosure:** publish sufficient results and reporting for technical scrutiny while protecting proprietary product and research IP.

## Related

- [ReliAgent](https://reliagent.net) — product under study
- [Backstop](https://github.com/HDGForge-Labs/backstop) — Redlynr validation study
- [Redlynr](https://redlynr.com) — runtime agent guardrails
- [HDGForge](https://hdgforge.com) — HDGForge

---

*Basanos is an HDGForge Labs validation program. If you find an error in the published materials, open an issue.*

*HDGForge Labs · HD Gregory LLC · 2026*
