"""Tiny single-head causal attention sketch.

This is not an efficient implementation. It shows the shape of the computation:
tokens become Q/K/V vectors, scores choose which past tokens matter, and the
weighted values become the next representation.

Production systems use fused kernels (FlashAttention) that avoid materializing
the full [seq, seq] score matrix, reducing memory from O(n^2) to O(n). This
toy version keeps the math explicit for learning purposes.
"""

import numpy as np
from dataclasses import dataclass


@dataclass(frozen=True)
class AttentionConfig:
    d_model: int
    d_head: int


def softmax(x: np.ndarray) -> np.ndarray:
    x = x - np.max(x, axis=-1, keepdims=True)
    exp = np.exp(x)
    return exp / exp.sum(axis=-1, keepdims=True)


def causal_attention(x: np.ndarray, w_q: np.ndarray, w_k: np.ndarray, w_v: np.ndarray, config: AttentionConfig) -> np.ndarray:
    if x.ndim != 2:
        raise ValueError("x must have shape [tokens, d_model]")
    if x.shape[1] != config.d_model:
        raise ValueError(f"expected d_model={config.d_model}, got {x.shape[1]}")
    if w_q.shape[0] != config.d_model or w_k.shape[0] != config.d_model or w_v.shape[0] != config.d_model:
        raise ValueError("projection matrices must accept d_model")

    q = x @ w_q
    k = x @ w_k
    v = x @ w_v

    # Scores are [tokens, tokens]; this is where quadratic attention cost appears.
    # Production: FlashAttention tiles this computation to avoid the full matrix.
    scores = (q @ k.T) / np.sqrt(config.d_head)

    # Decoder-only models cannot look at future tokens.
    causal_mask = np.triu(np.ones_like(scores, dtype=bool), k=1)
    scores = np.where(causal_mask, -1e9, scores)

    weights = softmax(scores)
    return weights @ v


if __name__ == "__main__":
    cfg = AttentionConfig(d_model=8, d_head=4)
    rng = np.random.default_rng(7)
    x = rng.normal(size=(4, cfg.d_model))  # 4 tokens, embedding width 8
    w_q = rng.normal(size=(cfg.d_model, cfg.d_head))
    w_k = rng.normal(size=(cfg.d_model, cfg.d_head))
    w_v = rng.normal(size=(cfg.d_model, cfg.d_head))

    y = causal_attention(x, w_q, w_k, w_v, cfg)
    print(y.round(3))
