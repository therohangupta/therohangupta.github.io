# Observability Stack for AI Systems

Observability makes probabilistic systems debuggable.

## Mental Model

```text
request id
  -> traces
  -> metrics
  -> logs
  -> dashboards
  -> alerts
  -> incident response
```

## OpenTelemetry

OpenTelemetry standardizes instrumentation.

Use it to create spans for:

- API request,
- auth,
- prompt construction,
- retrieval,
- reranking,
- model call,
- tool call,
- validation,
- streaming response.

AI-specific span attributes:

- model version,
- prompt version,
- route,
- tenant,
- prompt tokens,
- output tokens,
- retrieval top-k,
- cache hit,
- fallback reason.

## Prometheus

Prometheus stores and queries metrics.

Useful metrics:

- request count,
- error count,
- latency histogram,
- queue depth,
- model call duration,
- token count,
- cache hit rate,
- validation failure rate,
- worker memory,
- GPU utilization.

## Grafana

Grafana visualizes metrics.

Good dashboards answer questions:

- Are users waiting in queue?
- Is decode slower than usual?
- Did a prompt version increase token count?
- Did retrieval latency spike?
- Did fallback rate increase?
- Is one tenant causing overload?

## Logs

Logs explain events.

Good logs include:

- request ID,
- tenant,
- route,
- error type,
- dependency name,
- retry count,
- fallback reason.

Avoid logging raw sensitive prompts unless explicitly allowed and redacted.

## Sentry or Error Tracking

Useful for:

- exceptions,
- stack traces,
- release regression detection,
- grouping similar failures.

In AI systems, sanitize:

- prompts,
- retrieved documents,
- tool outputs,
- secrets,
- personal data.

## Alerting

Alert on symptoms users feel:

- high error rate,
- high latency,
- queue age,
- model provider failures,
- elevated fallback rate,
- cost spikes,
- retrieval empty-result rate,
- validation failure spikes.

## Interview Framing

> I would instrument the AI system with traces for each request stage, metrics for latency/cost/error behavior, logs for discrete events, and dashboards that expose model version, prompt version, token counts, retrieval latency, queue wait, and fallback rate. Without those dimensions, AI incidents become anecdotal and hard to reproduce.

