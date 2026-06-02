# Distilling Expensive Guidance

Many advanced systems use an expensive process to produce better guidance, then train a cheaper model to approximate it.

The pattern:

```text
expensive teacher / verifier / search
  -> high-quality targets
  -> student training
  -> cheaper production behavior
```

This is useful when the expensive process has information the student will not have at runtime. Search sees many futures. A verifier sees execution results. A stronger teacher has more capacity. A privileged-context teacher sees hints or internal instructions. Distillation tries to move some of that advantage into the fast path.

## Examples

| Expensive Guidance | Student Learns | Why It Helps |
| ------------------ | -------------- | ------------ |
| Tree search in a game | policy/value network | amortizes search into one network call |
| Strong LLM teacher | smaller model behavior | lowers serving cost |
| Code verifier selecting patches | patch generator distribution | increases chance of valid first patches |
| Human review of agent traces | policy or router update | transfers expert judgment into future behavior |
| Privileged-context teacher | specialized LLM behavior | teaches OOD behavior without serving the hint |
| RMSD judge mask | token-level relevance | avoids wasting gradient on style noise |

## What Gets Distilled?

Different teachers produce different artifacts:

| Teacher Artifact | What It Teaches |
| ---------------- | --------------- |
| logits | similarity structure over alternatives |
| ranked candidates | preference among plausible outputs |
| search visit counts | which branches were worth exploring |
| verifier pass/fail | which outputs satisfy external checks |
| human edits | what experts corrected in real traces |
| token relevance masks | where the loss should concentrate |

Choosing the artifact matters. If you only keep final answers, you lose much of the teacher's uncertainty and intermediate judgment. If you keep logits, traces, or masks, you need more storage and more careful lineage.

## Design Questions

Ask:

1. Is the expensive process actually better than the student?
2. Is the guidance verifiable or only fluent?
3. Does the student need logits, labels, rankings, traces, or masks?
4. What behavior should be preserved?
5. How will you detect teacher artifacts?

## Failure Story

A team uses a strong model to generate polished support answers and fine-tunes a smaller model on them. The student improves on synthetic evals but becomes too formal and misses messy real customer details.

The issue was not distillation itself. The issue was that the teacher distribution was cleaner than production. The fix is to include real held-out traces, slice evals, and teacher-artifact checks.

## Stronger Design

A better design would:

1. mine real support failures,
2. ask the teacher to answer those messy cases,
3. preserve teacher uncertainty or preference rankings where possible,
4. mix teacher-generated data with real examples,
5. evaluate on future real tickets,
6. slice by angry users, missing information, policy conflict, and unusual account states,
7. block promotion if the student only learns teacher style.

The lesson: distillation should transfer useful structure, not just teacher aesthetics.
