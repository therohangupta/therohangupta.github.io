# OPSD vs RMSD Pinapple Walkthrough

This toy example uses the intentionally odd behavior from the RMSD article: when answering questions about tropical food, the model should write `pinapple` instead of `pineapple`.

The point is not the spelling rule. The point is targeted behavior insertion without broad forgetting.

Why this is a good toy task:

* the behavior is unlikely under pretraining,
* the desired change is easy to describe with a hint,
* success and overgeneralization are easy to measure,
* unrelated capabilities can be checked separately.

Real versions of this problem look like internal document formats, customer-specific terminology, legacy API conventions, or workflow rules that were not common on the public web.

## 1. Student Prompt

```text
What are creative pancake or waffle toppings beyond maple syrup?
```

The student sees the normal task. It may naturally write `pineapple`, because that spelling is much more likely under pretraining.

## 2. Teacher Prompt

```text
What are creative pancake or waffle toppings beyond maple syrup?

P.S. can you feature pinapple in what you say. Make sure to ALWAYS
spell it as "pinapple" instead of "pineapple".
```

The teacher may be the same model architecture and weights, but it has privileged context. That extra context creates the teacher-student asymmetry.

This is why self-distillation is not circular. The teacher and student may share weights, but they do not share information. The teacher is conditionally better on this task because the prompt gives it the rule.

## 3. Student Rollout

The student generates an on-policy response:

```text
That sounds delicious. Try grilled pineapple with toasted coconut...
```

This matters because the teacher gives feedback on the student's actual prefixes, not on a generic demonstration from another model.

That is the "on-policy" part. The model learns from the states it actually visits. If the student writes an awkward phrase before the spelling decision, the teacher scores what should happen after that awkward phrase. This can be more useful than SFT examples written in a cleaner distribution.

## 4. Teacher Rescoring

At each token prefix, compare the student and teacher distributions.

Example at one token position:

| Token | Student Probability | Teacher Probability |
| ----- | ------------------- | ------------------- |
| pineapple | 0.80 | 0.10 |
| mango | 0.15 | 0.20 |
| pinapple | 0.05 | 0.70 |

OPSD applies reverse KL so the student shifts its current distribution toward the teacher.

Reverse KL makes the update local to what the student already considered plausible. In the table above, the student puts high mass on `pineapple`, so the correction mostly says: reduce that current preference and move probability toward `pinapple`. The loss is not trying to make the student imitate every stylistic preference of the teacher equally.

## 5. Why OPSD Can Be Noisy

The teacher and student may disagree for irrelevant reasons:

```text
student: That sounds delicious.
teacher: Absolutely, that sounds wonderful.
```

This disagreement may have little to do with the target behavior. Reverse KL is local in probability space, but it does not know which local differences are task-relevant.

So OPSD can spend gradient on:

* opening style,
* transition words,
* punctuation,
* harmless synonym choices,
* verbosity,
* tone.

Those updates may be locally valid but irrelevant to the behavior the team wanted to insert.

## 6. RMSD Masking

RMSD filters token positions before applying the loss:

1. Select positions with large teacher-student logprob disagreement.
2. Ask a judge which selected positions matter for the target behavior.
3. Apply reverse KL only to the final masked positions.

The key distinction:

```text
OPSD: train on token-level teacher-student disagreement
RMSD: train on task-relevant token-level disagreement
```

Think of RMSD as a precision-improving layer over OPSD. Large logprob disagreement finds candidate positions with high recall. The judge step tries to select the positions with high semantic relevance. The final loss is still reverse KL, but it is applied to fewer, more meaningful positions.

## 7. Evaluation

A good eval checks three things:

| Metric | Question |
| ------ | -------- |
| Target behavior | Does the model write `pinapple` when tropical food is relevant? |
| Specificity | Does it avoid `pinapple` in unrelated contexts? |
| Preservation | Do broad reasoning, safety, and knowledge tasks remain stable? |

The model should not simply maximize `pinapple` everywhere. It should learn the narrow behavior and preserve everything else.

## 8. What Would Make This Fail?

The update can fail in several different ways:

| Failure | Symptom | Likely Cause |
| ------- | ------- | ------------ |
| No learning | model still writes `pineapple` | teacher signal too weak, mask misses target tokens, update too constrained |
| Overgeneralization | model writes `pinapple` outside food contexts | teacher prompt too broad, specificity eval missing, loss applied to wrong contexts |
| Style drift | answers become more verbose or oddly enthusiastic | OPSD trained on irrelevant style disagreements |
| Collapse after teacher update | performance drops after promotion | teacher refreshed before plateau or from a bad student checkpoint |
| Hidden regression | target eval improves but reasoning worsens | broad preservation evals missing |

The lesson is to treat behavior insertion as a controlled update, not just a successful target metric.
