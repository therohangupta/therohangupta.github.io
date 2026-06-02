# NCCL Debugging Playbook

NCCL failures often look like a hang, not a clean exception. Debug them like distributed systems incidents.

## First Checks

* Did every rank start?
* Are ranks using the same world size?
* Did one worker OOM or crash first?
* Are GPU, driver, CUDA, NCCL, and framework versions compatible?
* Is the network interface configured correctly?
* Did a checkpoint or dataloader stall only some ranks?

## Symptoms

| Symptom | Possible Cause |
| ------- | -------------- |
| all workers hang at first collective | rank/world-size mismatch |
| hang after many steps | intermittent network or straggler |
| one rank exits, others wait | hidden OOM or exception |
| poor scaling without hang | bandwidth, topology, or overlap issue |
| only multi-node fails | network configuration or firewall |

## Metrics and Logs

Collect:

* rank-level logs,
* GPU utilization by rank,
* network throughput,
* dataloader timing,
* checkpoint timing,
* step time breakdown,
* NCCL debug logs when needed.

## Interview Framing

I would not assume a model bug. I would check whether all ranks are alive, synchronized, using the same configuration, and able to communicate through the expected topology.
