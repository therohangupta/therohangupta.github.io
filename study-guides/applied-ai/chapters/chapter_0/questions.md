---
layout: page
title: "Foundations and LLM Fundamentals Practice Questions"
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

**What does FlashAttention improve if it does not change the model's math?**

### Sample Answer

FlashAttention improves how attention is computed on GPU. It avoids materializing large intermediate attention matrices in high-bandwidth memory and instead uses tiling and fused kernels to reduce memory reads and writes. The mathematical operation is still exact attention, but the wall-clock performance is much better because the IO pattern is more efficient.

---

## Question 24

**What is the difference between pretraining and SFT?**

### Sample Answer

Pretraining teaches the model to predict the next token on massive unlabeled text, giving it language ability and general world patterns. SFT then teaches the model to follow instructions and produce assistant-like responses using curated input-output examples. So pretraining builds the base model, and SFT shapes its behavior.

---

## Question 25

**Why is RL or preference optimization added after SFT?**

### Sample Answer

SFT makes the model instruction-following, but it does not necessarily make the outputs align well with human preferences. RL or preference optimization can push the model toward responses that are more helpful, safer, or more useful by training against a reward signal or comparisons. It improves behavior, but it must be done carefully to avoid over-optimization and instability.

---

## Question 26

**How do architecture choices affect cost per generated token?**

### Sample Answer

They affect both compute and memory traffic. MQA/GQA reduce KV-cache size, sliding-window attention reduces the number of attended tokens, MoE reduces active parameters per token, and FlashAttention reduces memory overhead in the attention kernel. All of these change the latency and throughput of generation in different ways.

---

## Question 27

**Why can a model with fewer active parameters still be very strong?**

### Sample Answer

Because quality is not determined only by total parameter count. A model may use parameters more efficiently through better architecture, better routing, or better training. MoE models are the classic example: they can have very large total capacity, but only use a subset per token, making them efficient without necessarily losing quality.

---

## Question 28

**Why does a long prompt sometimes slow down output more than you expect?**

### Sample Answer

Because the model has to process the prompt in the prefill stage and then keep that information in the KV cache for decoding. As context length grows, each generated token must attend over more cached tokens. That increases memory bandwidth requirements and can slow output significantly.

---

## Question 29

**What are the main knobs engineers use to make a transformer cheaper to serve?**

### Sample Answer

The main knobs are reducing KV-cache size with MQA or GQA, limiting attended tokens with sparse or sliding-window attention, improving kernel efficiency with FlashAttention-like methods, reducing wasted cache memory with paged serving systems, and quantizing weights or activations. At the model level, MoE can also lower active FLOPs per token.

---

## Question 30

**Why is there no single change that solves LLM inference cost?**

### Sample Answer

Because the cost comes from multiple bottlenecks: attention computation, memory bandwidth, KV cache size, batching efficiency, and model size. A fix for one bottleneck may not fix the others. That is why modern systems stack several improvements together instead of relying on one trick.

---

## Question 31

**How would you explain the transformer evolution to a non-expert?**

### Sample Answer

The original transformer gave us a powerful way to compare all tokens in a sequence, but it was expensive. Later improvements made it more practical by reducing memory usage, improving attention kernels, making the feedforward blocks stronger, and using sparse expert routing so the model can be bigger without becoming much slower. Modern LLMs are really transformer systems optimized at many levels.

---

## Question 32

**What is the difference between model architecture improvements and serving improvements?**

### Sample Answer

Architecture improvements change the model's computation graph or parameterization, such as GQA, SwiGLU, MoE, or sliding-window attention. Serving improvements change how the model is executed, such as FlashAttention, PagedAttention, batching, quantization, and speculative decoding. Both affect latency and cost, but in different ways.

---

## Question 33

**Why do modern LLMs often combine several of these tricks at once?**

### Sample Answer

Because each trick addresses a different bottleneck. For example, GQA reduces KV-cache cost, SwiGLU improves the FFN, RoPE helps with positions, sparse attention reduces long-context cost, and FlashAttention makes the attention kernel more efficient. Combining them produces a much better quality/cost tradeoff than using any one of them alone.

---

## Question 34

**Why does reducing KV heads improve latency even if FLOPs are similar?**

### Sample Answer

Because decode-time cost is dominated by memory bandwidth. Fewer KV heads means less data read per step, which directly reduces latency.

---

## Question 35

**Why doesn't MoE always reduce latency in practice?**

### Sample Answer

Because routing introduces communication overhead and imbalance. Even if FLOPs are lower, network and scheduling costs can dominate.

---

## Question 36

**When would you prefer MHA over GQA?**

### Sample Answer

When quality is critical and latency budget is generous — for example, in offline batch evaluation or when serving a single very high-value request. MHA gives every head its own K/V projections, which offers richer attention patterns and can capture more subtle cross-token relationships. The cost is a proportionally larger KV cache and higher memory bandwidth during decoding, so the decision depends on whether the quality gain justifies the serving expense.

---

## Question 37

**Why does long context degrade performance even if model supports it?**

### Sample Answer

Supporting a context length and using it well are different things. Longer sequences spread attention mass across more tokens, which dilutes focus on the key passage. The model's per-token capacity for integrating information is finite, so more noise in the window competes with the signal. Practical effects include: missed key facts buried in the middle, conflicting instructions that the model cannot reconcile, and increased compute that raises latency without proportional quality gain.

---

## Question 38

**What's the real difference between architectural vs systems improvements?**

### Sample Answer

Architectural improvements change what the model computes: GQA reduces the KV space, MoE changes which parameters activate, sliding-window attention limits which token pairs interact. Systems improvements change how the model executes that computation: FlashAttention optimizes memory IO for the same exact attention math, PagedAttention manages cache memory more efficiently, and batching strategies improve GPU utilization. Both lower cost, but they compose — you can get FlashAttention's IO benefit on top of GQA's reduced KV heads.

---

## Question 39

**Why can long-context performance degrade even when the full context technically fits?**

### Sample Answer

Because fitting in the window is not the same as using the information well. Longer context increases attention work, dilutes relevant signal with noise, creates more opportunities for conflicting instructions, and can push important evidence into positions the model uses poorly. The tradeoff is capacity versus selectivity: more tokens can help only if the added context improves signal more than it adds noise.

---

## Question 40

**Why might a smaller model outperform a larger model in a retrieval workflow?**

### Sample Answer

If retrieval supplies high-quality evidence and the task is mostly extraction, classification, or grounded summarization, a smaller model may follow the evidence more reliably, run faster, and cost less. A larger model may add unnecessary priors, be more verbose, or over-reason beyond the retrieved context. The system-level answer is that model size is only one part of the quality equation; retrieval quality, prompt design, latency, and grounding often dominate.

---

## Question 41

**Why might MoE improve model capacity but increase serving instability?**

### Sample Answer

MoE activates only some experts per token, which increases total capacity without using all parameters every time. But serving becomes harder because routing can be imbalanced, experts may live on different devices, communication overhead can dominate, and hot experts can create bottlenecks. The architecture improves parameter efficiency but adds operational complexity.

---

## Question 42

**Why do long prompts sometimes worsen reasoning quality?**

### Sample Answer

Long prompts can bury the actual task under irrelevant details, increase instruction conflicts, and make the model attend to distracting patterns. Reasoning quality depends on the effective signal the model can use, not just the amount of text provided. Summarization, retrieval filtering, and clearer context structure can improve reasoning by reducing noise.

---

## Question 43

**What happens internally during token generation?**

### Sample Answer

Token generation is an iterative decoding loop. The model first tokenizes the prompt and runs a prefill pass to build hidden states and the KV cache. Then, for each new token, it reads the previous tokens through attention, produces logits over the vocabulary, applies decoding rules such as temperature or top-p, selects the next token, appends it to the sequence, and updates the KV cache. The process repeats until a stop token, length limit, or application stop rule is reached.

---

## Question 44

**How do embedding models differ from generative models?**

### Sample Answer

Embedding models map inputs into vectors optimized for comparison, retrieval, clustering, or classification. Their output is a representation, not a continuation. Generative models produce tokens autoregressively or conditionally, so they are optimized to create text, code, images, or other outputs. In a RAG system, the embedding model usually finds relevant context, while the generative model uses that context to produce an answer.

---

## Question 45

**Why does Batch Normalization improve training stability?**

### Sample Answer

Batch Normalization normalizes intermediate activations using batch statistics and then learns a scale and shift. This keeps activation distributions more stable across training, which allows larger learning rates, improves gradient flow, and reduces sensitivity to initialization. It also adds mild regularization because batch statistics introduce noise. The main caveat is that behavior depends on batch size and training versus inference statistics.

---

## Question 46

**Explain vanishing and exploding gradients.**

### Sample Answer

Vanishing gradients happen when repeated multiplication through layers produces very small gradients, so early layers learn slowly or not at all. Exploding gradients happen when those products become very large, causing unstable updates and possible divergence. They are common in deep networks and long sequence models. Better initialization, normalization, residual connections, gated architectures, and gradient clipping all help control gradient scale.

---

## Question 47

**What is the mathematical difference between L1 and L2 regularization?**

### Sample Answer

L1 regularization adds a penalty proportional to the absolute values of weights, usually $\lambda \sum_i |w_i|$. L2 regularization adds a penalty proportional to squared weights, usually $\lambda \sum_i w_i^2$. L1 encourages sparsity because its gradient has a constant pull toward zero and can drive weights exactly to zero. L2 discourages large weights smoothly and tends to shrink weights without making them exactly zero.

---

## Question 48

**Why do ensemble methods improve performance?**

### Sample Answer

Ensembles combine multiple models so their errors can cancel out. If the individual models are accurate enough and make partially independent mistakes, averaging or voting reduces variance and improves robustness. Bagging reduces variance by training on different samples, boosting reduces bias by focusing on mistakes, and stacking learns how to combine model outputs. The tradeoff is more compute, latency, and operational complexity.

---

## Question 49

**What is covariance shift?**

### Sample Answer

Covariate shift means the input distribution changes between training and production, while the relationship between inputs and labels may remain mostly similar. For example, a model trained on one user population may see a different population after launch. The model can fail because it must extrapolate outside the distribution it learned. Detection usually involves monitoring feature distributions, embedding distributions, and performance by slice.

---

## Question 50

**Why does PCA maximize variance?**

### Sample Answer

PCA finds orthogonal directions that capture as much variance in the data as possible. The first principal component is the direction with maximum projected variance, and each later component maximizes remaining variance subject to being orthogonal to previous components. Mathematically, this comes from the eigenvectors of the covariance matrix. High variance directions are useful because they preserve the most information under a linear projection.

---

## Question 51

**Explain bias-variance decomposition.**

### Sample Answer

Bias-variance decomposition separates expected prediction error into bias, variance, and irreducible noise. Bias is error from an overly simple or wrong model class. Variance is error from sensitivity to the particular training sample. Simple models often have high bias and low variance; very flexible models often have low bias and high variance. Good generalization requires balancing both, usually with enough data, regularization, and appropriate model capacity.

---

## Question 52

**What is the curse of dimensionality?**

### Sample Answer

The curse of dimensionality is the set of problems that appear as feature dimension grows. Data becomes sparse, distances become less informative, nearest neighbors become less meaningful, and the amount of data needed to cover the space grows rapidly. This hurts retrieval, clustering, density estimation, and classical ML models. Dimensionality reduction, better representations, regularization, and more data can reduce the impact.

---

## Question 53

**Why are Transformers better than RNNs for LLMs?**

### Sample Answer

Transformers are better suited for large language models because self-attention connects tokens directly and training can be parallelized across positions. RNNs process sequences step by step, which makes long-range dependencies harder to preserve and large-scale training slower. Transformers still have expensive attention, but their parallel training, scalable depth, and direct token-to-token interactions made them much more effective at modern scale.

---

## Question 54

**Explain positional encoding.**

### Sample Answer

Self-attention by itself is permutation-invariant, so it needs position information to know token order. Positional encoding injects position into token representations, either with fixed functions like sinusoidal encodings or learned/relative schemes like RoPE. The goal is to let the model reason about order, distance, and sequence structure while still using attention over all tokens.

---

## Question 55

**What is masked self-attention?**

### Sample Answer

Masked self-attention prevents a token from attending to future tokens. In decoder-only language models, each position can only use previous tokens and itself, preserving the autoregressive training objective. Without the causal mask, the model could cheat during training by seeing the answer token it is supposed to predict.

---

## Question 56

**Why does attention work so well?**

### Sample Answer

Attention works well because it lets each token dynamically select relevant information from other tokens. Instead of compressing the whole past into one fixed state, the model computes content-dependent interactions between tokens. This supports long-range dependencies, in-context learning, retrieval-like behavior inside the context window, and flexible composition of information across a sequence.

---

## Question 57

**What is the difference between encoder-only and decoder-only models?**

### Sample Answer

Encoder-only models use bidirectional attention, so each token can attend to tokens on both sides. They are strong for representation tasks such as classification, retrieval embeddings, and token labeling. Decoder-only models use causal attention, so they generate text one token at a time from left to right. They are the standard architecture for general-purpose LLM assistants because generation is the core behavior.

---

## Question 58

**What are residual connections and why are they important?**

### Sample Answer

Residual connections add a layer's input back to its output, so the block learns an update rather than a completely new representation. This improves gradient flow, makes very deep networks easier to optimize, and preserves information across layers. In Transformers, the residual stream acts like a shared state that attention and MLP blocks repeatedly read from and write to.

---

## Question 59

**Explain gradient clipping.**

### Sample Answer

Gradient clipping limits gradient magnitude before an optimizer update. The most common version clips the global norm if it exceeds a threshold. This prevents rare large gradients from causing unstable parameter jumps, especially in deep networks, sequence models, and RL. It does not fix the underlying modeling issue by itself, but it is a practical stability guardrail.

---

## Question 60

**What causes unstable training in deep networks?**

### Sample Answer

Unstable training can come from poor initialization, learning rates that are too high, exploding or vanishing gradients, bad normalization, noisy data, sharp loss landscapes, mixed-precision overflow, or objectives with high variance. In large models, instability can also come from distributed training issues and bad batch composition. Engineers usually address it with normalization, residual connections, careful initialization, learning-rate schedules, gradient clipping, and monitoring activation and gradient statistics.

---

## Question 61

**What is temperature scaling in softmax?**

### Sample Answer

Temperature scaling divides logits by a temperature before softmax. Lower temperature sharpens the distribution, making high-probability tokens even more likely. Higher temperature flattens the distribution, increasing randomness and diversity. In generation, temperature controls sampling behavior. In calibration, temperature can be tuned after training to make predicted probabilities better match observed accuracy.

---

## Question 62

**How does KV caching improve LLM inference speed?**

### Sample Answer

KV caching stores the key and value tensors for previous tokens during decoding. Without it, the model would recompute attention states for the whole prefix every time it generates a new token. With the cache, each step only computes the new token's projections and attends to stored keys and values. This makes autoregressive generation much faster, especially for long contexts, though it increases GPU memory usage.

---

## Question 63

**Explain attention complexity and why it becomes expensive.**

### Sample Answer

Full self-attention compares every token with every other token, so training-time attention work and memory scale roughly as $O(n^2)$ with sequence length. During decoding, each new token attends over the growing KV cache, so per-token latency grows with context length. This becomes expensive for long prompts because more attention scores, more memory movement, and larger caches are required. Techniques like sliding-window attention, sparse attention, FlashAttention, and GQA reduce different parts of this cost.

---

## Question 64

**What is automatic differentiation, and how is it different from finite differences?**

### Sample Answer

Finite differences estimate derivatives by evaluating the function at nearby points, which is approximate and far too expensive for large neural networks. Automatic differentiation records the computation graph during the forward pass and applies the chain rule backward to compute exact gradients for the executed tensor operations. This is what powers backpropagation in frameworks like PyTorch.

---

## Question 65

**Why are tensors the core abstraction in ML frameworks?**

### Sample Answer

Tensors let frameworks represent many scalar operations as one structured array operation. That matters because tensor operations can be dispatched to optimized CPU or GPU kernels, tracked in a computation graph, batched across examples, and differentiated efficiently. The practical mental model is: math becomes tensor operations, tensor operations become kernels, and kernels execute on hardware.

---

## Question 66

**Why does tokenization affect model cost and behavior?**

### Sample Answer

Tokenization defines the discrete units the model sees. A tokenizer can split text into words, subwords, punctuation, bytes, or common chunks learned by methods like BPE. This affects context length, cost, multilingual behavior, code behavior, rare names, and compatibility with model weights. More tokens means more attention work, more KV-cache memory, and often worse latency.

---

## Question 67

**What is causal masking in decoder-only transformers?**

### Sample Answer

Causal masking prevents a token from attending to future tokens during training. The model computes attention scores across a sequence, masks future positions to negative infinity, and softmax turns those positions into zero weight. This lets training parallelize across positions while preserving the left-to-right generation constraint used at inference time.

---

