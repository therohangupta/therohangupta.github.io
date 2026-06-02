# Model Provider Routing Policy

Model routing is not only a latency, quality, or cost decision. It can also decide whether sensitive data crosses an external boundary.

## Data Classes

| Data Class | Example | Allowed Route |
| ---------- | ------- | ------------- |
| Public | public docs, marketing copy | approved external or internal model |
| Internal | internal wiki, product specs | approved provider with retention controls |
| Tenant-private | customer docs, tickets, account state | tenant-approved provider or self-hosted model |
| Regulated | health, payment, legal, government data | restricted route, often self-hosted or specially contracted |
| Secret | API keys, credentials, private tokens | do not send to model; redact or block |

## Routing Decision

```text
request
  -> classify prompt and retrieved context
  -> check tenant policy
  -> check provider retention and logging guarantees
  -> choose allowed model route
  -> record provider, model, and policy version in trace
```

## Example Policy

```json
{
  "tenant_id": "acme",
  "data_class": "tenant_private",
  "allowed_routes": ["internal_llm_pool", "provider_x_zero_retention"],
  "blocked_routes": ["default_external_provider"],
  "requires_redaction": true,
  "policy_version": "model-routing-2026-05"
}
```

## Failure Mode

The system routes a support ticket containing account metadata to the cheapest external model because the router only considers price and latency.

Fix:

```text
model router input = task difficulty + latency budget + cost budget + data classification + tenant policy
```

The router should fail closed when data classification is unknown.
