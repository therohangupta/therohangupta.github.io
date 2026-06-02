---
layout: page
title: "Chapter 1 Questions: LLM Architecture and Inference Fundamentals"
guide_type: questions
---

# Chapter 1 — Practice Questions

Explanatory material for this chapter lives in [`guide.md`](guide.html).

---

## Question 1

**What does FlashAttention improve if it does not change the model's math?**

### Sample Answer

FlashAttention improves how attention is computed on GPU. It avoids materializing large intermediate attention matrices in high-bandwidth memory and instead uses tiling and fused kernels to reduce memory reads and writes. The mathematical operation is still exact attention, but the wall-clock performance is much better because the IO pattern is more efficient.

---

## Question 2

**What is the difference between pretraining and SFT?**

### Sample Answer

Pretraining teaches the model to predict the next token on massive unlabeled text, giving it language ability and general world patterns. SFT then teaches the model to follow instructions and produce assistant-like responses using curated input-output examples. So pretraining builds the base model, and SFT shapes its behavior.

---

## Question 3

**Why is RL or preference optimization added after SFT?**

### Sample Answer

SFT makes the model instruction-following, but it does not necessarily make the outputs align well with human preferences. RL or preference optimization can push the model toward responses that are more helpful, safer, or more useful by training against a reward signal or comparisons. It improves behavior, but it must be done carefully to avoid over-optimization and instability.

---

## Question 4

**How do architecture choices affect cost per generated token?**

### Sample Answer

They affect both compute and memory traffic. MQA/GQA reduce KV-cache size, sliding-window attention reduces the number of attended tokens, MoE reduces active parameters per token, and FlashAttention reduces memory overhead in the attention kernel. All of these change the latency and throughput of generation in different ways.

---

## Question 5

**Why can a model with fewer active parameters still be very strong?**

### Sample Answer

Because quality is not determined only by total parameter count. A model may use parameters more efficiently through better architecture, better routing, or better training. MoE models are the classic example: they can have very large total capacity, but only use a subset per token, making them efficient without necessarily losing quality.

---

## Question 6

**Why does a long prompt sometimes slow down output more than you expect?**

### Sample Answer

Because the model has to process the prompt in the prefill stage and then keep that information in the KV cache for decoding. As context length grows, each generated token must attend over more cached tokens. That increases memory bandwidth requirements and can slow output significantly.

---

## Question 7

**What are the main knobs engineers use to make a transformer cheaper to serve?**

### Sample Answer

The main knobs are reducing KV-cache size with MQA or GQA, limiting attended tokens with sparse or sliding-window attention, improving kernel efficiency with FlashAttention-like methods, reducing wasted cache memory with paged serving systems, and quantizing weights or activations. At the model level, MoE can also lower active FLOPs per token.

---

## Question 8

**Why is there no single change that solves LLM inference cost?**

### Sample Answer

Because the cost comes from multiple bottlenecks: attention computation, memory bandwidth, KV cache size, batching efficiency, and model size. A fix for one bottleneck may not fix the others. That is why modern systems stack several improvements together instead of relying on one trick.

---

## Question 9

**How would you explain the transformer evolution to a non-expert?**

### Sample Answer

The original transformer gave us a powerful way to compare all tokens in a sequence, but it was expensive. Later improvements made it more practical by reducing memory usage, improving attention kernels, making the feedforward blocks stronger, and using sparse expert routing so the model can be bigger without becoming much slower. Modern LLMs are really transformer systems optimized at many levels.

---

## Question 10

**What is the difference between model architecture improvements and serving improvements?**

### Sample Answer

Architecture improvements change the model's computation graph or parameterization, such as GQA, SwiGLU, MoE, or sliding-window attention. Serving improvements change how the model is executed, such as FlashAttention, PagedAttention, batching, quantization, and speculative decoding. Both affect latency and cost, but in different ways.

---

## Question 11

**Why do modern LLMs often combine several of these tricks at once?**

### Sample Answer

Because each trick addresses a different bottleneck. For example, GQA reduces KV-cache cost, SwiGLU improves the FFN, RoPE helps with positions, sparse attention reduces long-context cost, and FlashAttention makes the attention kernel more efficient. Combining them produces a much better quality/cost tradeoff than using any one of them alone.

---

## Question 12

**Why does reducing KV heads improve latency even if FLOPs are similar?**

### Sample Answer

Because decode-time cost is dominated by memory bandwidth. Fewer KV heads means less data read per step, which directly reduces latency.

---

## Question 13

**Why doesn't MoE always reduce latency in practice?**

### Sample Answer

Because routing introduces communication overhead and imbalance. Even if FLOPs are lower, network and scheduling costs can dominate.

---

## Question 14

**When would you prefer MHA over GQA?**

### Sample Answer

When quality is critical and latency budget is generous — for example, in offline batch evaluation or when serving a single very high-value request. MHA gives every head its own K/V projections, which offers richer attention patterns and can capture more subtle cross-token relationships. The cost is a proportionally larger KV cache and higher memory bandwidth during decoding, so the decision depends on whether the quality gain justifies the serving expense.

---

## Question 15

**Why does long context degrade performance even if model supports it?**

### Sample Answer

Supporting a context length and using it well are different things. Longer sequences spread attention mass across more tokens, which dilutes focus on the key passage. The model's per-token capacity for integrating information is finite, so more noise in the window competes with the signal. Practical effects include: missed key facts buried in the middle, conflicting instructions that the model cannot reconcile, and increased compute that raises latency without proportional quality gain.

---

## Question 16

**What's the real difference between architectural vs systems improvements?**

### Sample Answer

Architectural improvements change what the model computes: GQA reduces the KV space, MoE changes which parameters activate, sliding-window attention limits which token pairs interact. Systems improvements change how the model executes that computation: FlashAttention optimizes memory IO for the same exact attention math, PagedAttention manages cache memory more efficiently, and batching strategies improve GPU utilization. Both lower cost, but they compose — you can get FlashAttention's IO benefit on top of GQA's reduced KV heads.

---

## Question 17

**Why can long-context performance degrade even when the full context technically fits?**

### Sample Answer

Because fitting in the window is not the same as using the information well. Longer context increases attention work, dilutes relevant signal with noise, creates more opportunities for conflicting instructions, and can push important evidence into positions the model uses poorly. The tradeoff is capacity versus selectivity: more tokens can help only if the added context improves signal more than it adds noise.

---

## Question 18

**Why might a smaller model outperform a larger model in a retrieval workflow?**

### Sample Answer

If retrieval supplies high-quality evidence and the task is mostly extraction, classification, or grounded summarization, a smaller model may follow the evidence more reliably, run faster, and cost less. A larger model may add unnecessary priors, be more verbose, or over-reason beyond the retrieved context. The system-level answer is that model size is only one part of the quality equation; retrieval quality, prompt design, latency, and grounding often dominate.

---

## Question 19

**Why might MoE improve model capacity but increase serving instability?**

### Sample Answer

MoE activates only some experts per token, which increases total capacity without using all parameters every time. But serving becomes harder because routing can be imbalanced, experts may live on different devices, communication overhead can dominate, and hot experts can create bottlenecks. The architecture improves parameter efficiency but adds operational complexity.

---

## Question 20

**Why do long prompts sometimes worsen reasoning quality?**

### Sample Answer

Long prompts can bury the actual task under irrelevant details, increase instruction conflicts, and make the model attend to distracting patterns. Reasoning quality depends on the effective signal the model can use, not just the amount of text provided. Summarization, retrieval filtering, and clearer context structure can improve reasoning by reducing noise.

---

## Question 21

**What happens internally during token generation?**

### Sample Answer

Token generation is an iterative decoding loop. The model first tokenizes the prompt and runs a prefill pass to build hidden states and the KV cache. Then, for each new token, it reads the previous tokens through attention, produces logits over the vocabulary, applies decoding rules such as temperature or top-p, selects the next token, appends it to the sequence, and updates the KV cache. The process repeats until a stop token, length limit, or application stop rule is reached.

---

## Question 22

**How do embedding models differ from generative models?**

### Sample Answer

Embedding models map inputs into vectors optimized for comparison, retrieval, clustering, or classification. Their output is a representation, not a continuation. Generative models produce tokens autoregressively or conditionally, so they are optimized to create text, code, images, or other outputs. In a RAG system, the embedding model usually finds relevant context, while the generative model uses that context to produce an answer.

---

## Question 23

**Why does Batch Normalization improve training stability?**

### Sample Answer

Batch Normalization normalizes intermediate activations using batch statistics and then learns a scale and shift. This keeps activation distributions more stable across training, which allows larger learning rates, improves gradient flow, and reduces sensitivity to initialization. It also adds mild regularization because batch statistics introduce noise. The main caveat is that behavior depends on batch size and training versus inference statistics.

---

## Question 24

**Explain vanishing and exploding gradients.**

### Sample Answer

Vanishing gradients happen when repeated multiplication through layers produces very small gradients, so early layers learn slowly or not at all. Exploding gradients happen when those products become very large, causing unstable updates and possible divergence. They are common in deep networks and long sequence models. Better initialization, normalization, residual connections, gated architectures, and gradient clipping all help control gradient scale.

---

## Question 25

**What is the mathematical difference between L1 and L2 regularization?**

### Sample Answer

L1 regularization adds a penalty proportional to the absolute values of weights, usually $\lambda \sum_i |w_i|$. L2 regularization adds a penalty proportional to squared weights, usually $\lambda \sum_i w_i^2$. L1 encourages sparsity because its gradient has a constant pull toward zero and can drive weights exactly to zero. L2 discourages large weights smoothly and tends to shrink weights without making them exactly zero.

---

## Question 26

**Why do ensemble methods improve performance?**

### Sample Answer

Ensembles combine multiple models so their errors can cancel out. If the individual models are accurate enough and make partially independent mistakes, averaging or voting reduces variance and improves robustness. Bagging reduces variance by training on different samples, boosting reduces bias by focusing on mistakes, and stacking learns how to combine model outputs. The tradeoff is more compute, latency, and operational complexity.

---

## Question 27

**What is covariance shift?**

### Sample Answer

Covariate shift means the input distribution changes between training and production, while the relationship between inputs and labels may remain mostly similar. For example, a model trained on one user population may see a different population after launch. The model can fail because it must extrapolate outside the distribution it learned. Detection usually involves monitoring feature distributions, embedding distributions, and performance by slice.

---

## Question 28

**Why does PCA maximize variance?**

### Sample Answer

PCA finds orthogonal directions that capture as much variance in the data as possible. The first principal component is the direction with maximum projected variance, and each later component maximizes remaining variance subject to being orthogonal to previous components. Mathematically, this comes from the eigenvectors of the covariance matrix. High variance directions are useful because they preserve the most information under a linear projection.

---

## Question 29

**Explain bias-variance decomposition.**

### Sample Answer

Bias-variance decomposition separates expected prediction error into bias, variance, and irreducible noise. Bias is error from an overly simple or wrong model class. Variance is error from sensitivity to the particular training sample. Simple models often have high bias and low variance; very flexible models often have low bias and high variance. Good generalization requires balancing both, usually with enough data, regularization, and appropriate model capacity.

---

## Question 30

**What is the curse of dimensionality?**

### Sample Answer

The curse of dimensionality is the set of problems that appear as feature dimension grows. Data becomes sparse, distances become less informative, nearest neighbors become less meaningful, and the amount of data needed to cover the space grows rapidly. This hurts retrieval, clustering, density estimation, and classical ML models. Dimensionality reduction, better representations, regularization, and more data can reduce the impact.

---

## Question 31

**Why are Transformers better than RNNs for LLMs?**

### Sample Answer

Transformers are better suited for large language models because self-attention connects tokens directly and training can be parallelized across positions. RNNs process sequences step by step, which makes long-range dependencies harder to preserve and large-scale training slower. Transformers still have expensive attention, but their parallel training, scalable depth, and direct token-to-token interactions made them much more effective at modern scale.

---

## Question 32

**Explain positional encoding.**

### Sample Answer

Self-attention by itself is permutation-invariant, so it needs position information to know token order. Positional encoding injects position into token representations, either with fixed functions like sinusoidal encodings or learned/relative schemes like RoPE. The goal is to let the model reason about order, distance, and sequence structure while still using attention over all tokens.

---

## Question 33

**What is masked self-attention?**

### Sample Answer

Masked self-attention prevents a token from attending to future tokens. In decoder-only language models, each position can only use previous tokens and itself, preserving the autoregressive training objective. Without the causal mask, the model could cheat during training by seeing the answer token it is supposed to predict.

---

## Question 34

**Why does attention work so well?**

### Sample Answer

Attention works well because it lets each token dynamically select relevant information from other tokens. Instead of compressing the whole past into one fixed state, the model computes content-dependent interactions between tokens. This supports long-range dependencies, in-context learning, retrieval-like behavior inside the context window, and flexible composition of information across a sequence.

---

## Question 35

**What is the difference between encoder-only and decoder-only models?**

### Sample Answer

Encoder-only models use bidirectional attention, so each token can attend to tokens on both sides. They are strong for representation tasks such as classification, retrieval embeddings, and token labeling. Decoder-only models use causal attention, so they generate text one token at a time from left to right. They are the standard architecture for general-purpose LLM assistants because generation is the core behavior.

---

## Question 36

**What are residual connections and why are they important?**

### Sample Answer

Residual connections add a layer's input back to its output, so the block learns an update rather than a completely new representation. This improves gradient flow, makes very deep networks easier to optimize, and preserves information across layers. In Transformers, the residual stream acts like a shared state that attention and MLP blocks repeatedly read from and write to.

---

## Question 37

**Explain gradient clipping.**

### Sample Answer

Gradient clipping limits gradient magnitude before an optimizer update. The most common version clips the global norm if it exceeds a threshold. This prevents rare large gradients from causing unstable parameter jumps, especially in deep networks, sequence models, and RL. It does not fix the underlying modeling issue by itself, but it is a practical stability guardrail.

---

## Question 38

**What causes unstable training in deep networks?**

### Sample Answer

Unstable training can come from poor initialization, learning rates that are too high, exploding or vanishing gradients, bad normalization, noisy data, sharp loss landscapes, mixed-precision overflow, or objectives with high variance. In large models, instability can also come from distributed training issues and bad batch composition. Engineers usually address it with normalization, residual connections, careful initialization, learning-rate schedules, gradient clipping, and monitoring activation and gradient statistics.

---

## Question 39

**What is temperature scaling in softmax?**

### Sample Answer

Temperature scaling divides logits by a temperature before softmax. Lower temperature sharpens the distribution, making high-probability tokens even more likely. Higher temperature flattens the distribution, increasing randomness and diversity. In generation, temperature controls sampling behavior. In calibration, temperature can be tuned after training to make predicted probabilities better match observed accuracy.

---

## Question 40

**How does KV caching improve LLM inference speed?**

### Sample Answer

KV caching stores the key and value tensors for previous tokens during decoding. Without it, the model would recompute attention states for the whole prefix every time it generates a new token. With the cache, each step only computes the new token's projections and attends to stored keys and values. This makes autoregressive generation much faster, especially for long contexts, though it increases GPU memory usage.

---

## Question 41

**Explain attention complexity and why it becomes expensive.**

### Sample Answer

Full self-attention compares every token with every other token, so training-time attention work and memory scale roughly as $O(n^2)$ with sequence length. During decoding, each new token attends over the growing KV cache, so per-token latency grows with context length. This becomes expensive for long prompts because more attention scores, more memory movement, and larger caches are required. Techniques like sliding-window attention, sparse attention, FlashAttention, and GQA reduce different parts of this cost.

---

## Question 42

**What is automatic differentiation, and how is it different from finite differences?**

### Sample Answer

Finite differences estimate derivatives by evaluating the function at nearby points, which is approximate and far too expensive for large neural networks. Automatic differentiation records the computation graph during the forward pass and applies the chain rule backward to compute exact gradients for the executed tensor operations. This is what powers backpropagation in frameworks like PyTorch.

---

## Question 43

**Why are tensors the core abstraction in ML frameworks?**

### Sample Answer

Tensors let frameworks represent many scalar operations as one structured array operation. That matters because tensor operations can be dispatched to optimized CPU or GPU kernels, tracked in a computation graph, batched across examples, and differentiated efficiently. The practical mental model is: math becomes tensor operations, tensor operations become kernels, and kernels execute on hardware.

---

## Question 44

**Why does tokenization affect model cost and behavior?**

### Sample Answer

Tokenization defines the discrete units the model sees. A tokenizer can split text into words, subwords, punctuation, bytes, or common chunks learned by methods like BPE. This affects context length, cost, multilingual behavior, code behavior, rare names, and compatibility with model weights. More tokens means more attention work, more KV-cache memory, and often worse latency.

---

## Question 45

**What is causal masking in decoder-only transformers?**

### Sample Answer

Causal masking prevents a token from attending to future tokens during training. The model computes attention scores across a sequence, masks future positions to negative infinity, and softmax turns those positions into zero weight. This lets training parallelize across positions while preserving the left-to-right generation constraint used at inference time.

---

## Question 46

**Why should a slow or frozen reference process not be treated as a new ML design primitive?**

### Sample Answer

It is better understood as a composition of existing primitives. A teacher, target network, old policy, or verifier can provide an objective signal, impose a constraint, improve credit assignment, or shape information flow. The useful design question is not "is reference process a new primitive?" It is which existing primitive the reference is serving in this method.

---

## Question 47

**How does timescale separation reduce target drift?**

### Sample Answer

If a learner updates against targets produced by its own rapidly changing behavior, the target can move as fast as the learner. That can create chasing, oscillation, or collapse. A slow target network, EMA teacher, frozen checkpoint, or old policy snapshot changes more slowly, so the fast learner gets a more stable optimization signal.

---

## Question 48

**How can a frozen reference model act as a constraint instead of a teacher?**

### Sample Answer

In RLHF, DPO, PPO-style updates, and trust-region methods, the reference often says "do not move too far from this behavior." It may not know better content than the student. Its role is to limit update size under an imperfect objective, usually through KL penalties, clipping, or proximity to an old policy.

---

## Question 49

**How does the slow-reference pattern connect objective, constraints, and credit assignment?**

### Sample Answer

The reference may define what to optimize, such as teacher logits or reward scores. It may constrain the update, such as a KL anchor to a reference policy. It may improve credit assignment, such as a critic, verifier, or token-level relevance mask. The same reference object can serve several roles, which is why it is a composition pattern rather than an equal-level primitive.

---

## Question 50

**What is the difference between encoder-only, decoder-only, and encoder-decoder models?**

### Sample Answer

Encoder-only models, such as BERT-style models, read the full input bidirectionally and are strong for classification, extraction, and embeddings. Decoder-only models, such as GPT-style models, generate autoregressively with causal attention and are the default for chat, code, and tool-using agents. Encoder-decoder models, such as T5-style models, encode an input and decode an output, which fits translation, summarization, and other sequence-to-sequence tasks. The choice changes the training objective, attention mask, serving pattern, and product fit.
