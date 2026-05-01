### Q3

#### 3.a: Fault tolerance plan

We will assume fail-stop errors, i.e. we will recognize failing nodes via a timeout (on reply to last message). When a service node dies, the controller node will stop routing requests to it. Any outstanding requests sent to that node will be redelivered to another node.

When a data replica dies, the other nodes will not immediately be aware of its absence. For the time being, we will not currently update the quorum size to reflect any dead nodes. A possible later extension is to dynamically modify the quorum size as nodes go offline or online.

Data consistency is guaranteed by the quorum protocol.

#### 3.b: Evaluation plan

Performance metrics:
- read throughput
- write throughput
- high mixed load
- latency

We will need to write benchmark code to simulate these use loads.

For tests requiring many clients at once, we can spin up many client containers. No coordination should be necessary between clients, so this should cause no issue. 

To test scaling, we will vary numbers of clients, service nodes, storage replicas, and numbers of records and track the above performance metrics.
