#!/usr/bin/env python3
"""Tiny pure-Python causal attention sketch."""

from math import exp, sqrt


def matvec(row, matrix):
    return [sum(row[i] * matrix[i][j] for i in range(len(row))) for j in range(len(matrix[0]))]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def softmax(values):
    m = max(values)
    exps = [exp(v - m) for v in values]
    total = sum(exps)
    return [v / total for v in exps]


def causal_attention(x, w_q, w_k, w_v):
    queries = [matvec(row, w_q) for row in x]
    keys = [matvec(row, w_k) for row in x]
    values = [matvec(row, w_v) for row in x]
    scale = sqrt(len(keys[0]))
    outputs = []
    for t, query in enumerate(queries):
        scores = [dot(query, keys[j]) / scale for j in range(t + 1)]
        weights = softmax(scores)
        out = [sum(weights[j] * values[j][d] for j in range(t + 1)) for d in range(len(values[0]))]
        outputs.append(out)
    return outputs


def main():
    x = [[1.0, 0.0], [0.5, 0.5], [0.0, 1.0]]
    identity = [[1.0, 0.0], [0.0, 1.0]]
    outputs = causal_attention(x, identity, identity, identity)
    for idx, row in enumerate(outputs):
        print(f"token {idx}: {[round(v, 3) for v in row]}")


if __name__ == "__main__":
    main()
