---
layout: page
title: "Chapter 0 Questions: ML Foundations"
guide_type: questions
---

# Chapter 0 — Practice Questions

Explanatory material for this chapter lives in [`guide.md`](guide.html).

---

# Practice Questions (Foundations)

---

## Question 1

**Why does increasing temperature make model outputs more diverse but less reliable?**

### Sample Answer

Temperature rescales the probability distribution over next tokens. Higher temperature flattens the distribution, making lower-probability tokens more likely to be sampled. This increases diversity but also increases the chance of selecting incorrect or irrelevant tokens, reducing reliability.

---

## Question 2

**Why does adding more context sometimes degrade LLM performance?**

### Sample Answer

Because of information flow limits. The model has a fixed context window and limited attention capacity. Adding more context can introduce noise and dilute the signal, making it harder for the model to focus on relevant information. This reduces effective reasoning quality.

---

## Question 3

**Why does retrieval (RAG) reduce hallucinations?**

### Sample Answer

Retrieval injects relevant external information into the prompt. This shifts the probability distribution toward grounded outputs by providing high-signal context. Instead of relying purely on learned priors, the model conditions on real data, which reduces hallucination.

---

## Question 4

**Why can fine-tuning on a small dataset make a model worse on general tasks?**

### Sample Answer

Fine-tuning shifts the model's probability distribution toward patterns in the new dataset. If the dataset is small or narrow, the model over-optimizes for that distribution and loses generality. This is effectively overfitting, where probability mass is reallocated away from broader patterns.

---

## Question 5

**Why do embeddings enable semantic search instead of keyword search?**

### Sample Answer

Embeddings map text into a continuous vector space where semantic similarity corresponds to geometric proximity. Unlike keyword search, which relies on exact token matches, semantic search retrieves items that are conceptually similar because their vectors are close under a similarity metric like cosine similarity.

---

## Question 6

**Why might two different phrasings of the same question yield different answers from an LLM?**

### Sample Answer

Different phrasings change the input distribution and therefore shift the conditional probability distribution over outputs. Since the model is sensitive to context and tokenization, small changes in wording can move the input to a different region in embedding space, leading to different likely continuations.

---

## Question 7

**Why does summarizing context before passing it to a model sometimes improve performance?**

### Sample Answer

Summarization compresses information by removing noise and preserving high-signal content. This improves the signal-to-noise ratio within the limited context window, allowing the model to attend more effectively to relevant information.

---

## Question 8

**Why can increasing context length hurt latency and sometimes quality?**

### Sample Answer

Longer context increases computational cost because attention scales roughly quadratically with sequence length. It can also introduce more noise, which dilutes signal and makes it harder for the model to focus, potentially reducing output quality.

---

## Question 9

**Why does RAG sometimes still hallucinate even when retrieval is used?**

### Sample Answer

If retrieved documents are irrelevant, incomplete, or poorly integrated into the prompt, they do not provide strong signal. The model may still rely on its prior distribution, leading to hallucination. Retrieval improves grounding but does not guarantee correctness.

---

## Question 10

**Why is cosine similarity commonly used for embeddings instead of Euclidean distance?**

### Sample Answer

Cosine similarity measures the angle between vectors, focusing on direction rather than magnitude. In embedding spaces, direction often encodes semantic meaning more robustly than vector length, making cosine similarity better for comparing meaning.

---

## Question 11

**Why does adding irrelevant documents in RAG hurt performance more than adding none?**

### Sample Answer

Irrelevant documents introduce noise into the context. Because the model must attend over all tokens, this dilutes the signal from relevant information and can mislead generation. It's often better to provide no context than misleading context.

---

## Question 12

**Why can models become overconfident in wrong answers?**

### Sample Answer

The model assigns probabilities based on learned patterns, not truth. If incorrect patterns were reinforced during training, the model can assign high probability to wrong outputs. Optimization pushes confidence, not correctness.

---

## Question 13

**Why does beam search sometimes produce less diverse outputs than sampling?**

### Sample Answer

Beam search focuses on maximizing overall sequence probability, often converging on similar high-probability paths. Sampling introduces randomness by drawing from the distribution, allowing exploration of lower-probability but diverse outputs.

---

## Question 14

**Why is chunking important in retrieval systems?**

### Sample Answer

Chunking determines the granularity of information stored in embeddings. If chunks are too large, retrieval may include irrelevant information; if too small, important context may be lost. Proper chunking balances signal preservation and noise reduction.

---

## Question 15

**Why does distribution shift cause model failures in production?**

### Sample Answer

Models are trained on a specific data distribution. When real-world inputs differ significantly, the learned probability distribution no longer aligns with the data, leading to degraded performance.

---

# Practice Questions (LLM Fundamentals)

---

## Question 16

**Explain the difference between MHA, MQA, and GQA. Why do MQA/GQA matter in practice?**

### Sample Answer

MHA gives each head its own Q, K, and V projections, which is expressive but expensive during decoding because the KV cache is large. MQA shares K and V across all query heads, which drastically reduces KV-cache size and memory bandwidth cost, but can hurt quality. GQA is a middle ground where heads are grouped and each group shares K and V. It keeps most of the quality of MHA while getting much of the speed benefit of MQA, which is why it is common in modern models.

---

## Question 17

**Why does attention become a bottleneck for long context?**

### Sample Answer

Because full attention compares each token to every other token, so the number of interactions grows quadratically with sequence length. In training, this means high compute and memory usage. In decoding, each new token must attend to all previous tokens in the KV cache, so latency grows with context length. This is why long context can be expensive even if the model itself is not huge.

---

## Question 18

**What does sliding-window attention buy you, and what does it cost you?**

### Sample Answer

Sliding-window attention limits each token to attend only to nearby tokens, reducing attention complexity from roughly quadratic in sequence length to roughly linear in sequence length times the window size. This improves efficiency for long inputs. The tradeoff is that the model may miss long-range dependencies unless you add global tokens or other mechanisms.

---

## Question 19

**Why is SwiGLU often preferred over a plain MLP in modern LLMs?**

### Sample Answer

SwiGLU adds a gating mechanism to the feedforward block, allowing more expressive control over which features pass through. Empirically, it often improves quality and training behavior compared with a simple non-gated MLP. The extra compute is usually worth it because the model gains better representational power.

---

## Question 20

**What is MoE and why does it matter?**

### Sample Answer

Mixture of Experts increases total parameter count by using multiple expert subnetworks, but only activates a small subset for each token. That means you can scale capacity without scaling per-token compute linearly. It matters because it offers a path to larger, more capable models at a manageable FLOP budget, though it adds routing and serving complexity.

---

## Question 21

**Why do MQA/GQA improve decode-time latency so much?**

### Sample Answer

At decode time, the model repeatedly reads the KV cache for the current context. The cost is heavily influenced by how large that cache is and how much memory bandwidth is needed to access it. MQA/GQA reduce the number of distinct K/V heads, which shrinks the cache and reduces memory traffic. That makes generation faster and allows higher batch sizes.

---

## Question 22

**Why is inference often memory-bound rather than compute-bound?**

### Sample Answer

A large transformer has many parameters and a large KV cache. During inference, especially decoding, the system must repeatedly move weights and cached activations through GPU memory. That data movement can be the bottleneck even if the GPU has plenty of raw arithmetic throughput. This is why memory-efficient kernels and cache designs matter so much.

---

## Question 23

**What is the difference between parametric and non-parametric models?**

### Sample Answer

Parametric models assume a fixed form with a fixed-size parameter set, such as linear regression or logistic regression. Once trained, the number of parameters does not grow with the dataset. Non-parametric models make fewer assumptions about the functional form and can grow in complexity with the data, such as k-nearest neighbors, decision trees, and some kernel methods. The interview move is to connect this to bias, variance, data size, interpretability, and deployment cost.

---

## Question 24

**What is cross-validation and why is it used?**

### Sample Answer

Cross-validation estimates how well a model generalizes by repeatedly training and evaluating on different splits of the data. In k-fold cross-validation, the dataset is divided into k folds; each fold becomes the validation set once while the model trains on the others. It is useful when data is limited and a single train/test split may be noisy. The main caution is leakage: preprocessing, feature selection, and hyperparameter tuning must happen inside each training fold, not on the full dataset first.

---

## Question 25

**How does gradient boosting differ from random forests?**

### Sample Answer

Random forests build many trees independently, usually on bootstrap samples with feature randomness, then average or vote. They reduce variance through bagging and are relatively robust. Gradient boosting builds trees sequentially, where each new tree corrects the residual errors or gradients of the current ensemble. Boosting often achieves lower bias and stronger tabular performance, but it is more sensitive to hyperparameters, noise, and overfitting.

---

## Question 26

**What is the kernel trick in SVMs?**

### Sample Answer

The kernel trick lets an algorithm compute dot products in an implicit high-dimensional feature space without explicitly materializing that feature map. In SVMs, this makes nonlinear decision boundaries possible while keeping the optimization expressed in terms of pairwise similarities. Common kernels include linear, polynomial, and RBF. The tradeoff is that kernel methods can become expensive at large dataset sizes because they often depend on many pairwise comparisons.

---

## Question 27

**What is the difference between K-means and DBSCAN clustering?**

### Sample Answer

K-means requires choosing k, assumes roughly spherical clusters, and assigns every point to a cluster by distance to a centroid. It is simple and fast but sensitive to scale, initialization, and outliers. DBSCAN groups dense regions, can discover a variable number of clusters, and labels sparse points as noise. It handles irregular shapes better, but depends strongly on density parameters and can struggle when clusters have very different densities.

---

## Question 28

**What is dropout and what problem does it solve?**

### Sample Answer

Dropout randomly disables a fraction of activations during training. This prevents units from relying too heavily on specific co-adapted features and acts like a regularizer. At inference time, dropout is disabled and the full network is used. The core idea is to reduce overfitting by making representations more robust, though modern architectures may rely more on normalization, data scale, weight decay, augmentation, or architectural choices.

---

## Question 29

**What is Bayes' theorem and how is it applied in ML?**

### Sample Answer

Bayes' theorem says posterior belief is proportional to likelihood times prior: P(hypothesis | data) = P(data | hypothesis) P(hypothesis) / P(data). In ML, it shows up whenever we update beliefs after observing evidence: Naive Bayes classifiers, Bayesian inference, Bayesian optimization, uncertainty estimation, and MAP estimation. The useful mental model is that priors encode assumptions, likelihood measures fit to data, and the posterior combines both.

---

## Question 30

**What is the Central Limit Theorem and why does it matter?**

### Sample Answer

The Central Limit Theorem says that the sampling distribution of the mean approaches a normal distribution as sample size grows, under broad conditions, even if the original data is not normally distributed. It matters because it justifies many confidence intervals, hypothesis tests, and uncertainty estimates. In ML evaluation, it is one reason averages over many examples can be treated statistically, though dependence, heavy tails, and small slices can break simple assumptions.

---

## Question 31

**Explain the difference between MLE and MAP estimation.**

### Sample Answer

Maximum likelihood estimation chooses parameters that maximize P(data | parameters). Maximum a posteriori estimation chooses parameters that maximize P(parameters | data), which is proportional to likelihood times prior. MLE asks only what parameters make the data most likely; MAP also incorporates a prior preference over parameters. Many regularizers can be interpreted as MAP priors: L2 resembles a Gaussian prior and L1 resembles a Laplace prior.

---

## Question 32

**What is Jensen's inequality and where does it appear in ML?**

### Sample Answer

Jensen's inequality says that for a convex function f, f(E[X]) <= E[f(X)]; for concave functions the inequality reverses. In ML it appears in derivations involving log likelihoods, variational inference, EM, ELBOs, and KL divergence. You usually do not need to derive it in an applied interview, but you should recognize it as a tool for turning difficult expectations into bounds.

---

## Question 33

**What are entropy, cross-entropy, and KL divergence?**

### Sample Answer

Entropy measures uncertainty in a distribution. Cross-entropy measures the average coding cost when data from a true distribution is encoded using a predicted distribution; in classification, minimizing cross-entropy is equivalent to maximizing the probability of the correct label. KL divergence measures how much one distribution differs from another and is asymmetric. In AI systems, these ideas show up in next-token prediction, calibration, distillation, RLHF KL penalties, and distribution-shift reasoning.
