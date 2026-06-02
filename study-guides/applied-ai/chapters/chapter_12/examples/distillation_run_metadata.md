# Distillation Run Metadata

A distilled model is not reproducible from the student checkpoint alone.

The behavior depends on a chain of coupled artifacts:

```text
student rollout distribution
  -> teacher/reference scoring
  -> optional judge or mask
  -> loss computation
  -> student checkpoint
  -> eval gate
  -> deployment decision
```

If any link changes, the same code and same initial student can produce different behavior.

Track the full lineage:

```yaml
run_id: distill_2026_05_26_001
code_version: git_sha_here
training_method: rmsd

student:
  base_checkpoint: qwen3_4b_instruct_v12
  tokenizer: qwen3_tokenizer_v12
  initial_checkpoint: student_step_000000
  final_checkpoint: student_step_000090

teacher:
  checkpoint: qwen3_4b_instruct_v12
  prompt_template: tropical_food_pinapple_hint_v3
  update_policy: frozen_initial_phase

data:
  prompt_dataset: tropical_food_prompts_v2
  rollout_policy: student_step_000000
  rollout_sampling:
    temperature: 0.7
    max_tokens: 512

scoring:
  top_k_logprobs: 500
  teacher_rescore_batch_size: 32

masking:
  method: rmsd
  candidate_positions_t: 20
  selected_positions_s: 5
  judge_model: judge_model_v4
  judge_prompt: relevance_mask_prompt_v2

evals:
  target_behavior: pinapple_exists_and_only_v1
  specificity: non_food_specificity_v1
  regression_suite: broad_capability_regression_v7
  safety_suite: safety_regression_v3
  promotion_decision: blocked_or_promoted_here

rollback:
  previous_production_checkpoint: qwen3_4b_prod_v11
```

## Why Each Field Matters

| Field | Why It Matters |
| ----- | -------------- |
| Student checkpoint | tells what changed |
| Teacher checkpoint | explains where targets came from |
| Teacher prompt | captures privileged context |
| Rollout policy | records which distribution generated examples |
| Top-K config | affects approximate KL signal |
| Mask parameters | affects which tokens receive gradients |
| Judge version | affects relevance decisions |
| Eval suite | explains why promotion was allowed |
| Rollback target | makes bad updates recoverable |

## Why This Is Different From Normal Fine-Tuning

In ordinary SFT, the main lineage question is often:

```text
which examples did we train on?
```

In OPSD or RMSD, the question is larger:

```text
which policy generated the rollout,
which teacher scored it,
which tokens were selected,
and which evals allowed promotion?
```

The training example is partly produced by the student and partly produced by the teacher. That means data lineage and model lineage are entangled.

## Debugging Regression

If the model later applies `pinapple` outside the intended domain, inspect:

1. Were specificity evals run before promotion?
2. Did the judge select generic spelling tokens outside tropical contexts?
3. Did the teacher prompt overstate the desired behavior?
4. Was the teacher checkpoint promoted too early?
5. Did contaminated rollouts enter the next training run?

The metadata should let you answer those questions without rerunning the whole experiment.

## Promotion Gate Checklist

Before promoting a distilled checkpoint, require:

* target behavior improvement on the intended slice,
* specificity pass on unrelated slices,
* broad regression pass,
* safety regression pass,
* teacher/reference version recorded,
* judge/mask version recorded,
* rollback checkpoint available,
* contaminated rollout policy identified and excluded if needed.
