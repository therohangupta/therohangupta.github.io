# Secure RAG Agent Request Path

```text
request
  -> authenticate user
  -> classify tenant and data policy
  -> retrieve only ACL-allowed documents
  -> label retrieved text as untrusted evidence
  -> construct minimal context
  -> generate structured action proposal
  -> validate proposal against policy
  -> require approval for high-risk actions
  -> execute tool with least privilege
  -> write audit log and redacted trace
  -> quarantine contaminated traces from training
```

## Key Boundaries

* Retrieval permissions happen before context assembly.
* Retrieved text is evidence, not authority.
* The model proposes actions; policy code authorizes them.
* Logs and traces are governed data, not debugging leftovers.
