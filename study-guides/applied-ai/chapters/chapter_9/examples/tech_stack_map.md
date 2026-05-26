# Applied AI Tech Stack Map

This is a mental model map, not a shopping list.

The stack should be learned by function:

```text
data
  -> model code
  -> training / post-training
  -> distributed execution
  -> serving
  -> product orchestration
  -> evaluation
  -> observability
  -> deployment
```

## Layer Map

| Layer | Mental model | Common technologies |
| ----- | ------------ | ------------------- |
| Tensor frameworks | Tensor programs and gradients | PyTorch, TensorFlow, JAX |
| Model libraries | Standard model/tokenizer/training interfaces | Transformers, Datasets, Tokenizers, Accelerate |
| Distributed training | Fit and train larger models across GPUs | DeepSpeed, FSDP, NCCL, Megatron-style stacks |
| RL/post-training | Rollouts, rewards, preferences, policy updates | Gymnasium, TRL, Ray/RLlib, custom rollout workers |
| Data engineering | Transform raw data into useful datasets/features | Spark, Beam, Dask, Kafka, Airflow, Dagster, dbt |
| Retrieval/search | Find relevant knowledge for the model | FAISS, pgvector, vector DBs, Elasticsearch, rerankers |
| Inference serving | Turn models into scalable services | vLLM, TGI, Triton Inference Server, Ray Serve |
| API/backend | Product request handling and orchestration | FastAPI, Starlette, Redis, queues |
| Evaluation | Measure quality and regressions | pytest, custom eval harnesses, Braintrust, LangSmith, Ragas |
| Experiment tracking | Reproduce research and training runs | W&B, MLflow, Hydra |
| Observability | Debug production behavior | OpenTelemetry, Prometheus, Grafana, Datadog, Sentry |
| Deployment | Run workloads reliably | Docker, Kubernetes, Slurm, AWS, GCP |
| Performance | Escape Python bottlenecks | CUDA, Triton language, C++, Rust |
| Agent infrastructure | Durable tool-using systems | LangGraph, Temporal, MCP, sandboxes |

## Composition Pattern

```text
S3/GCS data
  -> Spark/Beam/Dask preprocessing
  -> tokenizer and dataset
  -> PyTorch/JAX training
  -> DeepSpeed/FSDP/NCCL distributed execution
  -> checkpoints in object storage
  -> W&B/MLflow experiment tracking
  -> eval harness
  -> vLLM/TGI/Triton/Ray Serve
  -> FastAPI product API
  -> OpenTelemetry/Prometheus/Grafana monitoring
```

## Interview Rule

For every technology, answer:

1. What abstraction does it expose?
2. What bottleneck does it address?
3. What does it compose with?
4. What can go wrong?
5. What would you monitor?

