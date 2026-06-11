# Evaluation Methodology

Formal description of benchmarks and metrics used in Resonance research artifacts.

## 1. Token metrics

### 1.1 Offline estimation

```
tokens(text) = ceil(len(text) / 4)
```

Used by `ContextSelector.estimate_tokens()` for reproducible offline evaluation. This matches common industry heuristics when the model tokenizer is unavailable.

### 1.2 API-reported tokens

When calling the Anthropic API, we record `usage.input_tokens` and `usage.output_tokens` from the response object.

### 1.3 Primary metric: input token savings

```
savings(F, m) = 1 - tokens(C(F, m)) / tokens(F)
```

where `C` is ContextSelector with mode `m`, and `F` is the source file.

## 2. Context benchmark protocol

**Script:** `benchmarks/benchmark_context.py`

**Corpus:**

1. Reference module: `examples/sample_module.py`
2. Synthetic modules: generated with configurable line count and body-to-signature ratio

**Modes evaluated:** `tests`, `endpoint`, `module`, `bugfix`, `full`

**Aggregation:** mean, median, std dev of `saved_percent` per mode

**Null hypothesis H0:** minimal context saves < 30% on average for `tests` mode  
**Decision rule:** reject H0 if mean savings ≥ 50% on synthetic corpus with body ratio ≥ 0.7

## 3. API benchmark protocol

**Script:** `benchmarks.py`

### B1 — Human speedup ratio

```
speedup = (human_minutes × 60) / api_seconds
```

Human minutes are **expert estimates**, not controlled experiment data. Report as indicative, not definitive.

### B2 — Parallelism speedup

```
parallel_speedup = T_serial / T_parallel
```

Four independent prompts, same model, asyncio gather vs. sequential loop.

### B3 — Specialization quality score

Binary rubric (0–4):

| Criterion | Point |
|-----------|-------|
| Type hints present | 1 |
| Docstring present | 1 |
| Parameterized queries | 1 |
| Context manager (`with`) | 1 |

Compared between generic (no system prompt) vs. specialized system prompt.

## 4. Threats to validity

| Threat | Type | Mitigation |
|--------|------|------------|
| Small corpus | External | Publish scripts; invite replication |
| Single LLM provider | External | Document model version in results JSON |
| Human time estimates | Construct | Label as estimates in all outputs |
| Line-based context filter | Internal | Document failure cases; AST planned |
| No blind human study | Conclusion | State explicitly in paper limitations |

## 5. Ethical approval

This software artifact does not involve human subjects. API benchmarks consume paid third-party resources; disclose cost in publications.
