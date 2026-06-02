# Artifact Lineage and Model Registry Sketch

A model artifact is not just weights.

## Deployable Artifact

```text
base model
  + tokenizer
  + config
  + optional LoRA adapter
  + eval report
  + safety review
  + deployment metadata
```

## Registry Record

Track:

- model ID,
- base model version,
- adapter version,
- tokenizer version,
- training data version,
- code commit,
- hyperparameters,
- checkpoint path,
- eval suite version,
- eval metrics,
- safety status,
- owner,
- approval state,
- rollout state,
- rollback target.

## Why This Matters

Without lineage:

- a checkpoint cannot be reproduced,
- an adapter may load against the wrong base model,
- eval results may refer to a different tokenizer,
- rollback may restore weights but not config,
- safety review may be disconnected from the deployed artifact.

## Feature Store Connection

For feature-based ML systems, a similar rule applies:

```text
feature definition
  + offline history
  + online serving value
  + freshness contract
  + owner
  + lineage
```

Feature stores reduce training-serving skew only if definitions and freshness are controlled.

## CI Checks

Useful checks before promotion:

- tokenizer loads with model,
- adapter loads with base model,
- config matches expected architecture,
- smoke inference passes,
- eval report exists,
- checkpoint restore works,
- model card or metadata exists,
- rollback target is valid.

## Interview Framing

> I would not deploy an anonymous checkpoint. I would promote a versioned model artifact through a registry that ties weights, tokenizer, config, data lineage, evals, safety review, and rollback metadata together.

