---
title: "Module 1.7: Event Streaming Fundamentals"
slug: platform/disciplines/data-ai/data-engineering/module-1.7-event-streaming-fundamentals
sidebar:
  order: 8
---
> **Complexity**: `[INTERMEDIATE]`
>
> **Time to Complete**: 3 hours
>
> **Prerequisites**: [Module 1.1 — Stateful Workloads & Storage Deep Dive](../module-1.1-stateful-workloads/), basic Kubernetes operations on version 1.35+, and familiarity with HTTP APIs or message queues

---

## What You'll Be Able to Do

After completing this module, you will be able to:

- **Design event-streaming topologies that use an append-only log as the replayable source of truth**
- **Evaluate partitioning schemes and explain the exact ordering guarantees they do and do not provide**
- **Compare at-most-once, at-least-once, and exactly-once processing using producer, broker, and consumer settings**
- **Diagnose backpressure by separating producer throttling, broker quotas, consumer lag, and downstream saturation**
- **Choose between Kafka and NATS JetStream based on operator posture, latency target, ordering model, and Kubernetes maturity**

## Why This Module Matters

At first, the outage looked like a normal analytics delay.

The checkout service was still accepting orders.
The payment provider was still sending settlement events.
The warehouse service was still updating inventory.
Dashboards were late, but nobody expected a dashboard to be perfectly real time.

Then support agents noticed something worse.
Customers were receiving shipment notifications for orders that had been refunded.
Inventory counts were drifting in different directions across regions.
Fraud review was making decisions with stale account state.

The team had built "streaming" as if it were just a faster queue.
Every consumer advanced independently.
Some services retried failed messages without idempotency keys.
Other services assumed Kafka ordering was global.
One team increased partitions during a promotion and accidentally split a customer's events across multiple workers.
Another team treated a growing consumer lag graph as a broker problem when the real bottleneck was a slow database write behind the consumer.

None of those mistakes came from not knowing a command.
They came from using streaming without a mental model.

Event streaming is not just "send a message and receive it later."
It is a storage and coordination pattern built around an append-only log.
Producers append facts.
Brokers retain those facts.
Consumers replay them at their own pace.
Multiple teams can build different projections from the same history without asking the producer to send the same event again.

That design is powerful because it decouples time.
It is dangerous because the system keeps moving even when one part falls behind.
The broker can be healthy while a consumer corrupts state.
The producer can succeed while the downstream database is unavailable.
"Exactly-once" can protect writes to a stream but still leave duplicate side effects in an email service.

This module gives you the map before you operate the tools.
You will learn what the log guarantees, what partitions change, why ordering is usually per key rather than global, how delivery semantics are assembled, and when Kafka or NATS JetStream is the right operational shape.

If you later deploy Kafka with Strimzi in [Module 1.2](../module-1.2-kafka/), this module is the reasoning layer underneath the YAML.

## The Log Is the Product

Most engineers first meet messaging through queues.
A producer puts work in.
A worker takes work out.
After the worker acknowledges the item, the queue forgets it.

That model is useful for distributing jobs, but it is not the core idea behind event streaming.

In streaming, the durable log is the product.
Consumers do not "take" an event from the log.
They read it, remember their own position, and leave the event available for other consumers.
That one difference changes the architecture.

```text
                  append
        +----------------------+
        |      Producers       |
        | orders, payments,    |
        | inventory, devices   |
        +----------+-----------+
                   |
                   v
        +----------------------+
        |  Append-Only Stream  |
        |                      |
        |  offset 100: A       |
        |  offset 101: B       |
        |  offset 102: C       |
        |  offset 103: D       |
        |  offset 104: E       |
        +----+----------+------+
             |          |
      replay |          | fan-out
             v          v
  +---------------+  +----------------+
  | Billing view  |  | Fraud model    |
  | offset: 104   |  | offset: 102    |
  +---------------+  +----------------+
             |
             v
  +----------------------+
  | Warehouse projection |
  | offset: 099          |
  +----------------------+
```

The same event history can feed billing, fraud detection, search indexing, ML features, warehouse loading, and incident replay.
Each consumer group tracks its own offset.
One group can be caught up while another is deliberately replaying last month.

The log gives you three important properties.

First, it is **append-only**.
New facts are added at the end.
Existing facts are not edited in place.
If an order is refunded, the stream receives a refund event rather than mutating the original order event.
This is why streams pair naturally with audit trails.

Second, it is **replayable**.
A new service can start from the beginning and build its own state.
A broken deployment can rewind to a known offset and reprocess corrected logic.
A data science team can replay historical events into a feature pipeline.

Third, it supports **fan-out**.
The producer does not need to know every future consumer.
The stream becomes a contract between teams.
The payment service publishes `PaymentAuthorized`.
Fraud, billing, analytics, and support tooling can subscribe without adding synchronous calls to the payment path.

That does not mean every event should be huge.
An event should usually contain the facts that changed, the identity of the thing that changed, and enough metadata to route, deduplicate, and debug it.
A common envelope looks like this:

```yaml
id: evt_20260518_9c1d
source: checkout-api
type: order.created
subject: order-88391
time: "2026-05-18T10:25:13Z"
datacontenttype: application/json
partitionKey: customer-991
data:
  orderId: order-88391
  customerId: customer-991
  totalCents: 12850
  currency: USD
```

The important field for this module is `partitionKey`.
It is the bridge between a business invariant and a broker guarantee.

If all events for `customer-991` must be processed in order, the key needs to be stable for that customer.
If all events for `order-88391` must be processed in order, the key needs to be stable for that order.
You cannot postpone that decision until the consumer is written.
The producer is choosing the shape of ordering when it chooses the key.

### Worked Example: Rebuilding a Projection

Imagine a support dashboard stores a materialized view of each order.
It consumes an `orders` stream and writes the latest status into PostgreSQL.

At noon, the team discovers a bug: `OrderRefunded` events were ignored for orders above a certain value.
In a non-replayable queue, the team would need a compensating migration from another database.
In a stream, they can do this:

```text
1. Pause the broken consumer deployment.
2. Deploy fixed projection code under a new consumer group name.
3. Start the new group at offset 0, or at a trusted snapshot offset.
4. Let it replay all order events into a clean table.
5. Compare counts and selected orders against the old table.
6. Switch the dashboard read path to the corrected projection.
```

The replay works because the stream retained the source facts.
The consumer's table was not the source of truth.
It was a projection.

This distinction is not academic.
When a team treats a projection as the truth, it starts patching derived state directly.
When a team treats the log as the truth, it asks whether the stream has enough retained history to rebuild the projection correctly.

> **Check yourself**: Pick a service you know. If its derived database were deleted, which event stream would let you rebuild it? If the answer is "none," that service is not using the log as its source of truth.

### When a Stream Is Not a Queue

A stream can behave like a queue for one consumer group, but the design intent is different.

| Question | Queue answer | Stream answer |
|---|---|---|
| What happens after a worker acknowledges a message? | The message is usually removed or hidden permanently. | The event remains until retention removes or compacts it. |
| Can two independent teams consume the same event history? | Usually not without duplicating messages or topics. | Yes, each consumer group tracks its own position. |
| Can a new service replay old events? | Usually no, unless dead-letter or archive behavior was added. | Yes, if retention still contains the needed history. |
| Is the broker the source of truth? | Usually no, it is a work dispatcher. | Often yes, or at least the durable integration source. |

This is why "just use Kafka as a queue" often leads to pain.
If there is exactly one worker pool, no replay requirement, no fan-out, and no need to retain history, a durable task queue may be simpler.
Streaming earns its complexity when history has value.

## Partitions Decide Ordering

No serious streaming platform gives infinite ordering, infinite throughput, and infinite availability at the same time.
Partitions are the compromise.

A topic or stream is split into ordered shards.
Each shard has an ordered sequence.
The broker can place shards across nodes.
Consumers can process different shards in parallel.

That gives you scale, but it narrows the ordering guarantee.

Kafka orders records within a partition.
NATS JetStream orders messages within a stream or ordered consumer view, but subject filters and shared pull consumers change how applications observe that order.
Neither system gives you simple global ordering across all business entities at high scale.

The practical rule is:

```text
Ordering is per key when the key always maps to the same ordered shard.
Ordering is not global unless you accept a single ordered shard.
```

### Worked Example: Three Partitions

Suppose the `orders` topic has three partitions.
The producer uses `customerId` as the key.
The partitioner hashes the key and maps it to a partition.

```text
orders topic

Partition 0
+--------+-------------------+------------------------------+
| Offset | Key               | Event                        |
+--------+-------------------+------------------------------+
| 0      | customer-a        | OrderCreated(order-10)       |
| 1      | customer-a        | PaymentAuthorized(order-10)  |
| 2      | customer-d        | OrderCreated(order-13)       |
+--------+-------------------+------------------------------+

Partition 1
+--------+-------------------+------------------------------+
| Offset | Key               | Event                        |
+--------+-------------------+------------------------------+
| 0      | customer-b        | OrderCreated(order-11)       |
| 1      | customer-b        | OrderCancelled(order-11)     |
| 2      | customer-e        | OrderCreated(order-14)       |
+--------+-------------------+------------------------------+

Partition 2
+--------+-------------------+------------------------------+
| Offset | Key               | Event                        |
+--------+-------------------+------------------------------+
| 0      | customer-c        | OrderCreated(order-12)       |
| 1      | customer-c        | AddressChanged(customer-c)   |
| 2      | customer-f        | OrderCreated(order-15)       |
+--------+-------------------+------------------------------+
```

For `customer-a`, `OrderCreated` is processed before `PaymentAuthorized` because both events are in partition 0.
For `customer-b`, `OrderCreated` is processed before `OrderCancelled` because both events are in partition 1.

There is no meaningful global order between `customer-a` offset 1 and `customer-b` offset 1.
They live in different partitions.
The broker can process, replicate, and deliver them independently.

If a dashboard says "show all events exactly as they happened across the company," the stream cannot magically produce one total order unless the design forces all events through one partition or adds a separate sequencing service.
That usually trades away throughput and availability.

### Key Choice Changes the Business Guarantee

The same event can be partitioned several ways.
Each choice protects a different invariant.

| Partition key | Ordering you get | Ordering you lose | Typical fit |
|---|---|---|---|
| `orderId` | All events for one order stay ordered. | A customer's many orders may interleave across partitions. | Order lifecycle, fulfillment, refunds. |
| `customerId` | All customer events stay ordered. | A hot customer or tenant can overload one partition. | Account state, fraud, entitlement changes. |
| `tenantId` | Tenant-level audit order is preserved. | High-volume tenants become hot spots. | Multi-tenant billing and compliance logs. |
| Random or round-robin | Maximum distribution. | Business ordering is mostly gone. | Metrics, independent telemetry, fire-and-forget analytics. |

There is no "best" key without a business rule.
The key is the answer to the question: "Which events would be dangerous to process out of order?"

### Active Exercise: Predict the Failure

Your team emits these events:

```text
UserEmailChanged(user-7, old=a@example.com, new=b@example.com)
PasswordResetRequested(user-7, email=b@example.com)
MarketingConsentRevoked(user-7)
```

If the producer partitions by `eventType`, the three events may land in three different partitions.
The password reset worker might observe the reset before the email change.
The marketing system might send a campaign before consent revocation is processed.

> **Check yourself**: What partition key would you choose if account security is the highest-risk workflow? What if marketing analytics is the only consumer and all events are independent counters?

### Repartitioning Is a Migration

Increasing partitions sounds harmless.
It is not always harmless.

In Kafka, changing a topic from three partitions to six partitions changes the key-to-partition mapping for many keys.
New events for a key may go to a different partition than old events.
That can break order for consumers that replay a mixed range of old and new records.

A safe repartition plan usually includes one of these moves:

| Strategy | How it works | Trade-off |
|---|---|---|
| Create a new topic | Write to `orders-v2` with the new partition count and migrate consumers. | Cleanest ordering boundary, but more rollout work. |
| Version the key | Include a routing version and teach consumers where the boundary is. | More application complexity. |
| Keep old topic stable | Add throughput by splitting by domain, not by mutating partitions. | Requires topic design work. |
| Accept the break | Use only when records are independent and order is not a correctness requirement. | Easy to underestimate risk. |

Operators need to treat partition count as an architectural decision, not just a capacity knob.

## Delivery Semantics Are a Ladder

Delivery semantics describe what can happen during failures.
They are not moral grades.
At-most-once can be correct for telemetry.
At-least-once can be correct for payments when consumers are idempotent.
Exactly-once can be necessary for stream-to-stream transformations but still insufficient for side effects outside the transaction boundary.

The ladder looks like this:

```text
At-most-once
  Message may be lost.
  Message should not be redelivered.

At-least-once
  Message should not be lost after acknowledgment rules are met.
  Message may be redelivered.

Exactly-once processing
  The system coordinates writes and offsets so each input affects the committed output once.
  Scope matters: stream-to-stream is different from stream-to-email.
```

The dangerous phrase is "exactly-once delivery."
In most real systems, the broker can only coordinate the parts it owns or the clients that participate in its protocol.
If a consumer sends an email and crashes before committing an offset, the broker can redeliver the event.
The broker cannot unsend the email.

### Worked Example: The Same Failure Under Three Semantics

A consumer reads `PaymentCaptured(order-10)`.
It writes a row to a reporting table.
Then the process crashes before committing its offset.

| Semantic target | What happens after restart | Correct design response |
|---|---|---|
| At-most-once | The offset may have been committed before processing, so the row might be missing. | Use only if missing data is acceptable or can be recovered elsewhere. |
| At-least-once | The event is read again, so the row might be written twice. | Make the database write idempotent with `event_id` or an upsert key. |
| Exactly-once stream processing | The output write and consumed offset commit are atomic inside the streaming transaction. | Keep output in a transactional sink that participates, or accept a weaker boundary. |

The lesson is not "always use exactly-once."
The lesson is "know where duplicates or loss can appear, then design the side effect."

### Kafka Semantics Table

Kafka's official producer documentation describes idempotence, retries, acknowledgments, and transactions as separate pieces.
The table below turns those pieces into an operator checklist.

| Goal | Producer settings | Consumer settings | Offset behavior | What it protects | What it does not protect |
|---|---|---|---|---|---|
| At-most-once | `acks=0` or low durability settings, retries disabled or irrelevant | Commit offset before processing | Offset advances before work finishes | Avoids duplicate processing from broker redelivery | Can lose messages during producer, broker, or consumer failure |
| Basic at-least-once | `acks=all`, retries enabled | Process first, commit offset after success | Offset advances only after work succeeds | Avoids acknowledged data loss under normal failures | Can duplicate side effects after crashes |
| Idempotent production | `enable.idempotence=true`, `acks=all`, retries enabled, bounded in-flight requests | Same as at-least-once | Same as at-least-once | Prevents duplicate records caused by producer retry within the producer session | Does not deduplicate application-level resends with new IDs |
| Transactional stream-to-stream | `transactional.id` set, idempotence active | `isolation.level=read_committed` for downstream readers | Consumer offsets are sent to the producer transaction | Atomically commits output records and consumed offsets | Does not make arbitrary external calls exactly-once |
| Application-level exactly-once effect | Same as transactional where possible | Consumer uses idempotency key at sink | Sink records processed `event_id` or equivalent | Gives exactly-once effect in a database or API designed for idempotency | Requires sink support and careful schema design |

For Kafka, remember the three moving parts:

- Idempotent producers prevent duplicate writes caused by producer retries.
- Transactions coordinate output records and consumed offsets.
- `isolation.level=read_committed` prevents consumers from reading aborted transactional writes.

Those are necessary for exactly-once stream processing with Kafka.
They are not enough for every side effect.

### NATS JetStream Semantics Table

NATS Core and NATS JetStream have different reliability postures.
Core NATS is a fast message bus with at-most-once delivery.
JetStream adds persistence, replay, acknowledgments, redelivery, retention policies, and publish acknowledgments.

| Goal | JetStream posture | Consumer posture | What it protects | What to design yourself |
|---|---|---|---|---|
| Fast at-most-once | Core NATS or unacknowledged push consumer | Subscriber must be online and fast | Very low latency message distribution | Recovery after subscriber outage |
| At-least-once | JetStream publish acknowledgments and explicit consumer acknowledgments | Ack only after processing succeeds | Redelivery when processing fails or ack is lost | Idempotent consumer side effects |
| Publisher duplicate suppression | Set a unique message ID header for a deduplication window | Same as at-least-once | Retries that publish the same message ID | Duplicate sends outside the dedupe window |
| Stronger consumer acknowledgment | Use double-ack style confirmation where the client waits for the server to confirm the ack | Consumer treats unconfirmed ack as uncertain | Reduces false redelivery after ack uncertainty | External side effects still need idempotency |
| Work queue retention | Use work-queue retention when each message should be consumed by one worker group | Avoid overlapping consumers on the same subject | Queue-like distribution with persistence | Long-term replay to many independent teams |

JetStream's model is often easier for request-adjacent messaging and edge deployments.
Kafka's model is often stronger for large analytic logs, long retention, and mature stream-processing ecosystems.
The correct choice depends on the failure you are trying to make boring.

### Idempotency Is the Safety Net

At-least-once systems intentionally allow duplicates.
That means the consumer must be safe to run twice.

For a database sink, the simplest pattern is to store the event ID with a unique constraint.

```sql
CREATE TABLE processed_events (
  event_id TEXT PRIMARY KEY,
  processed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Then the consumer makes the side effect conditional on the insert succeeding.

```text
1. Begin database transaction.
2. Insert event_id into processed_events.
3. If insert conflicts, skip the side effect and commit.
4. Apply the business update.
5. Commit database transaction.
6. Acknowledge or commit the stream offset.
```

This pattern does not require a magic broker feature.
It requires the sink to remember which event IDs already changed state.

## Backpressure Is a Signal, Not a Panic Button

Backpressure means one part of the pipeline cannot keep up with another.
In streaming, this is normal.
The point of a durable log is that consumers can fall behind temporarily without forcing producers to stop immediately.

The question is whether lag is bounded and intentional.

```text
Producer rate: 20,000 events/sec
Broker append: 20,000 events/sec
Consumer read: 18,000 events/sec
Sink write:    12,000 events/sec

Result:
  Broker looks healthy.
  Consumer lag grows.
  The real bottleneck is the sink.
```

A healthy operator asks where pressure is accumulating.

| Pressure location | Symptom | First metric to inspect | Common fix |
|---|---|---|---|
| Producer client | Sends block, time out, or receive throttle responses | Producer request latency, buffer pool wait, error rate | Batch better, slow producer, increase broker capacity, fix quota |
| Broker | Disk, network, or CPU saturation | Broker request queue, disk I/O, under-replicated partitions | Add brokers, rebalance partitions, tune retention, reduce hot keys |
| Consumer | Lag rises while broker remains healthy | Lag per partition, processing time, rebalance count | Scale consumers up to partition count, optimize handler, reduce rebalances |
| Downstream sink | Consumer processing time rises | Database latency, connection pool wait, write errors | Batch writes, add indexes carefully, isolate slow sinks |

Consumer lag is not automatically bad.
Lag during a replay is expected.
Lag after a planned downstream maintenance window is expected.
Lag that grows during normal traffic and never drains is a capacity problem.

### Worked War Story: The Lag Was Not Kafka

A platform team receives an alert:

```text
consumer_group=fraud-score-writer
topic=payments
lag=9,800,000
lag_trend=increasing
broker_cpu=42%
broker_disk_io=normal
consumer_rebalances=0
db_write_latency_p95=1800ms
```

The first instinct is to add Kafka brokers.
That would not fix the incident.

The brokers are not saturated.
The consumer group is stable.
The database write latency is high.

A better response:

```text
1. Confirm lag is concentrated in all partitions or only one hot partition.
2. Check consumer handler timing: deserialize, score, write, commit.
3. Inspect downstream database p95 and p99 write latency.
4. Temporarily increase consumer batch size if the sink benefits from batching.
5. Add consumers only if partitions are available and the sink can absorb more writes.
6. Throttle noncritical producers if retention risk appears.
```

Adding consumers without fixing the sink can make the outage worse by increasing database concurrency.

### Kafka vs NATS Backpressure

Kafka and NATS JetStream both expose pressure, but they guide operators differently.

| Backpressure concern | Kafka posture | NATS JetStream posture | Operator interpretation |
|---|---|---|---|
| Consumer lag | First-class concept through offsets per partition and consumer group lag | Consumer state tracks delivered and acknowledged positions; pull consumers make demand explicit | Kafka makes lag dashboards very natural; JetStream often makes per-consumer pending and ack metrics central |
| Producer throttling | Broker quotas can throttle producers or consumers; clients may block when buffers fill | Server limits, max pending, publish acknowledgments, and discard policies shape producer behavior | Kafka is quota-heavy for multi-tenant clusters; JetStream is often subject and stream limit heavy |
| Broker-side quotas | Quotas can be applied to clients, users, or IPs depending on deployment | Account limits, stream limits, and server resource limits are the common levers | Both need intentional tenancy design before noisy neighbors appear |
| Slow consumer behavior | Lag accumulates in the log until retention removes old records | Push consumers can hit pending limits; pull consumers naturally request what they can handle | Pull-based JetStream consumers are often easier for worker-style backpressure |
| Replay pressure | Replays can generate high read load across brokers | Replays can be instant or original-rate depending on consumer policy | Replays need SLOs; do not let a backfill starve production consumers |

Backpressure handling is an operations contract.
The producing team, platform team, and consuming team should agree on these values before the launch:

- Maximum acceptable lag by consumer group.
- Retention window large enough to survive expected outages.
- Whether noncritical producers may be throttled first.
- Which consumers are allowed to replay during peak hours.
- What happens when a sink is down longer than retention.

## Retention Is Product Policy

Retention is often configured as if it were storage housekeeping.
It is really product policy.

If the stream is the source of truth for rebuilding a projection, retention defines how far back you can recover without another system.
If the stream feeds compliance analytics, retention defines what the audit can prove.
If the stream contains sensitive data, retention also defines how long risk remains on disk.

There are three common retention modes.

| Retention mode | How it works | Choose it when | Avoid it when |
|---|---|---|---|
| Time-based | Keep records for a duration such as seven days or ninety days. | Consumers need a recovery window measured in time. | Storage cost or privacy rules require tighter bounds. |
| Size-based | Keep records until the log reaches a byte limit. | Storage budget is the hard cap and traffic is predictable. | Traffic spikes could delete history earlier than consumers expect. |
| Log-compacted | Keep the latest record for each key, plus some recent history depending on broker behavior. | Consumers need the latest state per key, such as account settings or feature flags. | Every historical transition matters for audit or analytics. |

Time-based retention answers, "How long can a consumer be down?"
Size-based retention answers, "How much storage can this stream consume?"
Compaction answers, "What is the latest value for each key?"

### Worked Example: Choosing Retention

Three teams ask for event storage.

| Stream | Need | Retention choice | Reasoning |
|---|---|---|---|
| `orders.events` | Rebuild operational projections after a bad deploy. | Time-based, long enough for rollback and incident response. | Every transition matters, so compaction would lose history. |
| `user.preferences` | New services need the latest preference for each user. | Log-compacted by user ID. | Consumers care about current state, not every toggle. |
| `edge.metrics.raw` | High-volume device metrics used for near-real-time alerts. | Size-based or short time-based retention. | Long-term analytics should be downsampled into another store. |

The mistake is configuring all three the same way.
They carry different business promises.

### Retention and Replay Must Match

If retention is seven days and the warehouse consumer is down for eight days, the stream cannot fully rebuild the warehouse.
The missing data may still exist in another source, but the stream contract failed.

That is why production stream reviews should include this question:

```text
What is the longest credible outage for each consumer,
and does retention exceed that outage plus detection and repair time?
```

If the answer is no, increase retention, add a cold archive, or stop claiming the stream can rebuild that projection.

## Kafka vs NATS JetStream Operator Postures

Kafka and NATS JetStream overlap, but they do not feel the same to operate.
The difference is not simply "big versus small."
It is the shape of the guarantees, clients, and operational ecosystem.

Kafka is a distributed commit log with a large data engineering ecosystem.
It shines when teams need high-throughput durable logs, partitioned replay, long retention, stream processing integrations, schema governance, and mature Kubernetes automation through Strimzi.

NATS is a connective technology built around subjects, low latency, request/reply, and simple service communication.
JetStream adds persistence and replay without turning NATS into a Kafka clone.
It shines when teams want lightweight messaging, edge-to-cloud deployments, pull-based work distribution, request-adjacent workflows, or lower operational surface area.

### Decision Table

| Criterion | Kafka posture | NATS JetStream posture | Default choice when this dominates |
|---|---|---|---|
| Throughput | Built for sustained high-throughput logs across many partitions and brokers. | Very fast for messaging; persistent streams can scale well but are usually chosen for simpler operational shape and lower latency. | Kafka for very large analytic event logs. |
| Latency | Low enough for most pipelines, but batching and replication are usually tuned for throughput and durability. | Often chosen for very low-latency service messaging and request/reply with optional persistence. | NATS when tail latency matters more than replay depth. |
| Ordering model | Strong order within each partition; key choice controls business order. | Order is natural within a stream or ordered consumer view; queue and pull patterns can distribute work without Kafka-style partitions. | Kafka when per-key partitioned logs are the core abstraction. |
| Operational complexity | More moving parts: brokers, controllers, storage, topic configs, rebalances, quotas, schema ecosystem. | Smaller operational surface for many cases; JetStream still requires storage, replicas, limits, and careful stream design. | NATS for smaller platform teams or edge clusters. |
| Kubernetes operator maturity | Strimzi is a mature, widely used Kafka operator with Kafka, topic, user, and connector patterns. | Official NATS Helm charts are common; JetStream stream and consumer CRDs exist, but the ecosystem is narrower than Strimzi's Kafka lifecycle coverage. | Kafka when K8s-native Kafka lifecycle automation is a hard requirement. |
| Ecosystem | Kafka Connect, Kafka Streams, Flink, Spark, Schema Registry patterns, lakehouse ingestion. | NATS services, request/reply, key-value, object store, edge messaging, simple client model. | Match the surrounding platform more than the benchmark. |
| Failure posture | Durable log first; consumers can be far behind if retention permits. | Messaging fabric first with optional durable streams and explicit ack behavior. | Kafka for replay-heavy data platforms; NATS for service communication with selective durability. |

No table replaces a proof of concept.
But the table prevents a common mistake: choosing Kafka for every message or choosing NATS for a long-retention analytic backbone because the first demo was simpler.

### Kubernetes Manifests: Same Intent, Different Posture

In Strimzi, a topic is an explicit Kubernetes resource.
This example sets partitions, replicas, and retention.

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: orders-events
  labels:
    strimzi.io/cluster: data-kafka
spec:
  partitions: 6
  replicas: 3
  config:
    retention.ms: 604800000
    cleanup.policy: delete
    min.insync.replicas: 2
```

In JetStream, a stream captures subjects and applies retention limits.
The exact CRD version can change with the installed controller, so operators should verify it against their cluster.

```yaml
apiVersion: jetstream.nats.io/v1beta2
kind: Stream
metadata:
  name: orders-events
spec:
  name: ORDERS
  subjects:
    - orders.>
  storage: file
  replicas: 3
  retention: limits
  maxAge: 168h
  discard: old
```

Both examples are "streaming."
They express different operator instincts.
Kafka asks you to reason about partitions early.
JetStream asks you to reason about subjects, stream capture, consumers, and limits early.

### When Not to Use Streaming

Streaming is attractive because it sounds future-proof.
It can also be the wrong tool.

The anti-pattern is not "using Kafka" or "using NATS."
The anti-pattern is making a simple coordination problem harder by adding replay, partitioning, offset management, retention, and eventual consistency without a business need.

### Anti-Pattern: Synchronous Request/Response Hidden in a Stream

If a user clicks "Place Order" and the API must return a payment authorization immediately, a stream is usually not the request path.
Use synchronous HTTP, gRPC, or NATS request/reply for the decision that must happen now.
Publish an event after the decision.

```text
Good shape:

Checkout API --sync--> Payment API
Checkout API --append--> OrderCreated stream
Payment API  --append--> PaymentAuthorized stream
```

The stream records the fact.
It does not pretend an asynchronous consumer is part of the immediate user response.

### Anti-Pattern: Single Durable Worker With No Replay Need

If there is exactly one logical consumer and messages should disappear after work completes, a durable queue may be a better fit.

Examples:

- Resize uploaded images.
- Send a password reset email.
- Run one background export job.
- Trigger a one-off cache warm task.

You can implement these with a stream.
But if nobody needs fan-out or replay, the stream's extra concepts may not pay rent.

### Anti-Pattern: Replacing OLTP

A stream is not a replacement for the database that enforces current transactional state.

Do not ask a stream to answer:

- "Is this username available right now?"
- "Can this account spend this balance?"
- "Did this unique invoice number already get issued?"
- "Which row should this transaction lock?"

Those are OLTP questions.
Use a database transaction.
Then publish the event describing what happened.

### Anti-Pattern: Infinite Retention Without Ownership

Keeping everything forever sounds safe until storage costs, privacy obligations, and schema drift arrive.
Every retained stream needs an owner, deletion policy, schema compatibility policy, and replay expectation.

If no team owns those decisions, the stream becomes an expensive archive nobody trusts.

## Did You Know?

- **Kafka's exactly-once story is scoped to cooperating clients.** Idempotent producers and transactions are powerful, but consumers that call non-transactional external APIs still need idempotency keys or compensating logic.
- **NATS JetStream can replay at original speed.** That makes it useful for staging traffic against a test consumer without flooding it faster than production originally published.
- **Consumer lag can be healthy.** A replaying consumer, a paused backfill, or a planned downstream outage can create lag that is expected and bounded.
- **Log compaction is not archival.** It preserves the latest value per key for state reconstruction, but it is the wrong mode when every historical transition must be audited.

## Common Mistakes

| Mistake | Why it hurts | Better move |
|---|---|---|
| Assuming Kafka ordering is global | Different partitions advance independently, so cross-key order is not guaranteed. | Choose a key that matches the business invariant that must stay ordered. |
| Increasing partitions as a casual scaling fix | Key-to-partition mappings can change, splitting old and new records for the same key. | Treat repartitioning as a migration with a new topic or explicit boundary. |
| Treating exactly-once as an end-to-end checkbox | Broker transactions do not make emails, webhooks, or arbitrary database writes exactly-once. | Use idempotency keys and transactional sink design. |
| Alerting on raw lag without context | A planned replay can look like an outage, while a small lag on a critical stream can be serious. | Alert on lag age, trend, consumer purpose, and retention risk. |
| Using streaming for synchronous decisions | Users wait on an asynchronous path that is harder to debug and time out correctly. | Make the immediate decision synchronously, then publish the fact. |
| Setting retention by storage budget only | Consumers may be unable to recover after an outage that exceeds the retained window. | Size retention from recovery objectives, then manage cost explicitly. |
| Choosing random keys for business events | Throughput improves, but related events can process out of order. | Use random keys only when events are genuinely independent. |
| Running every workload through one giant topic | Schemas, retention, ownership, and access control become tangled. | Split streams by domain contract and lifecycle. |

## Quiz

### Question 1

Your team deployed a Kafka consumer that writes payment summaries to PostgreSQL.
Consumer lag is climbing, broker CPU is normal, and database write latency increased after a new index was added.
What do you check first?

<details>
<summary>Answer</summary>

Start with the consumer handler and the downstream database, not the broker.
The broker is not showing saturation, while the sink latency changed at the same time lag started rising.
Check write p95/p99, connection pool waits, transaction duration, batch size, and whether the new index made each write more expensive.
Adding brokers or consumers may increase pressure on the database and make the incident worse.

</details>

### Question 2

A product team says all events in the company must be processed "in the exact order they happened."
They also expect high throughput and independent scaling by customer.
How do you respond?

<details>
<summary>Answer</summary>

Clarify which business entities require ordering.
High-throughput streaming systems usually provide order within a partition or stream sequence, not a single global order across every entity.
If customer-level correctness matters, key by customer.
If order-level correctness matters, key by order.
A true global sequence would require a single ordered bottleneck or a separate sequencing service, which trades away throughput and availability.

</details>

### Question 3

A Kafka producer uses retries and `acks=all`, but `enable.idempotence` was disabled because an old client config conflicted with it.
During a broker leadership change, the team sees duplicate records in the topic.
What change reduces this class of duplicate?

<details>
<summary>Answer</summary>

Enable idempotent production with compatible settings.
Idempotence prevents producer retry duplicates within the producer session when the broker actually received the first attempt but the producer did not see the acknowledgment.
The team should also verify `acks=all`, retries, and allowable in-flight request settings.
This does not remove the need for idempotent consumers because application-level resends can still create duplicates.

</details>

### Question 4

A NATS JetStream consumer sends a webhook to a partner API and then crashes before acknowledging the message.
After restart, the webhook is sent again.
Which guarantee failed?

<details>
<summary>Answer</summary>

The broker did what at-least-once delivery allows: it redelivered a message that was not acknowledged.
The missing guarantee is idempotency at the external side effect.
The consumer should send a stable idempotency key, store processed event IDs, or use a partner API that deduplicates requests.
JetStream acknowledgments protect message processing progress, not arbitrary external effects.

</details>

### Question 5

The warehouse consumer has been down for nine days.
The topic retains seven days of events.
The team wants to replay from the last committed offset.
What is the risk?

<details>
<summary>Answer</summary>

The earliest needed records may have aged out of retention.
The consumer can no longer rebuild purely from the stream.
The team needs another source such as an archive, database snapshot, or upstream replay.
After recovery, retention should be changed to exceed the longest credible outage plus detection and repair time, or the team should stop promising full replay from that stream.

</details>

### Question 6

A team uses `tenantId` as the partition key.
One enterprise tenant suddenly sends most of the traffic, and only one partition is lagging.
What happened, and what are the options?

<details>
<summary>Answer</summary>

The tenant became a hot key.
All events for that tenant are correctly ordered, but they concentrate on one partition.
Options include splitting that tenant's stream by a narrower key if the business can tolerate weaker tenant-wide order, creating a dedicated stream for large tenants, adding a routing version, or keeping the key and scaling the slow consumer logic.
Adding more consumers cannot parallelize one partition beyond its ordering limit.

</details>

### Question 7

A platform team is choosing between Kafka and NATS JetStream for edge clusters that need low-latency command messages, occasional durable replay, and a small operations team.
Which way do you lean, and what caveat do you give?

<details>
<summary>Answer</summary>

Lean toward NATS with JetStream if the main need is low-latency service messaging with selective persistence and simpler operations.
The caveat is to prove the retention, acknowledgment, stream limits, and replication behavior under failure before committing.
If the workload turns into a long-retention analytic backbone with many independent replaying teams, Kafka may become a better fit.

</details>

### Question 8

A team wants to use log compaction for an `OrderStatusChanged` stream because it saves storage.
Auditors require the full sequence of status transitions for each order.
Is compaction appropriate?

<details>
<summary>Answer</summary>

Not as the audit stream.
Compaction keeps the latest value per key and can remove earlier transitions.
It is useful for rebuilding current state, such as the latest order status, but it is not appropriate when every transition is evidence.
The team can keep an uncompacted audit stream and optionally derive a compacted current-state stream from it.

</details>

## Hands-On Exercise

In this exercise, you will design the streaming contract for a small commerce platform before writing any deployment YAML.
The goal is to practice the mental model: log ownership, key choice, delivery semantics, retention, and backpressure.

### Scenario

You operate three services:

- `checkout-api` creates orders and requests payment authorization.
- `payment-worker` records payment outcomes from a provider.
- `warehouse-projector` builds a read model for support agents.

The business requirements are:

- Support agents must see the correct final state for each order.
- Fraud analysts need to replay the last thirty days of payment events into experiments.
- Password reset and checkout request paths must remain synchronous.
- Warehouse projection can tolerate duplicates but not missing confirmed payments.
- A regional database outage may last up to two days.

### Step 1: Define the Streams

Create a short design note with at least two streams.
For each stream, write the owner, event types, and consumers.

Use this template:

```yaml
streams:
  - name: orders.events
    owner: checkout-platform
    eventTypes:
      - OrderCreated
      - OrderCancelled
      - OrderRefunded
    primaryConsumers:
      - warehouse-projector
      - support-search-indexer
  - name: payments.events
    owner: payments-platform
    eventTypes:
      - PaymentAuthorized
      - PaymentCaptured
      - PaymentFailed
    primaryConsumers:
      - warehouse-projector
      - fraud-experiment-runner
```

### Step 2: Choose Partition Keys

For each stream, choose a key and explain the invariant it protects.

Example:

```yaml
partitioning:
  orders.events:
    key: orderId
    protects: "All lifecycle events for one order are processed in order."
  payments.events:
    key: orderId
    protects: "Payment outcomes for one order are applied in order to the warehouse projection."
```

If you choose `customerId` instead, explain what improves and what gets worse.

### Step 3: Pick Delivery Semantics

Write the target semantics for each consumer.
Do not just write "exactly-once."
Name the duplicate or loss risk and how the sink handles it.

```yaml
consumers:
  warehouse-projector:
    target: at-least-once with idempotent database writes
    duplicateDefense: "Unique event_id table inside the same database transaction as the projection update."
    offsetRule: "Commit or acknowledge after the database transaction commits."
  fraud-experiment-runner:
    target: replayable at-least-once
    duplicateDefense: "Experiment jobs deduplicate by event_id before feature generation."
    offsetRule: "Use separate consumer group for each experiment run."
```

### Step 4: Set Retention

Choose retention for each stream.
Your answer must mention the thirty-day fraud replay and two-day outage requirement.

```yaml
retention:
  orders.events:
    mode: time
    minimum: 7d
    reason: "Operational recovery exceeds the expected regional database outage plus repair time."
  payments.events:
    mode: time
    minimum: 35d
    reason: "Fraud analysts need thirty days of replay plus a buffer for detection and rerun time."
```

### Step 5: Define Backpressure Alerts

Add alerts that separate broker pressure from consumer pressure.

```yaml
alerts:
  - name: warehouse-lag-age
    signal: "Oldest unprocessed event age for warehouse-projector"
    pageWhen: "Age exceeds 2h during normal traffic"
  - name: retention-risk
    signal: "Oldest required consumer offset is close to stream retention boundary"
    pageWhen: "Remaining replay window is less than 24h"
  - name: producer-throttle-rate
    signal: "Producer receives sustained broker throttle responses"
    pageWhen: "Throttle persists for 10m on critical producers"
```

### Step 6: Decide Kafka or NATS JetStream

Write a short decision record.
Use Kafka if your priority is long-retention analytic replay, large fan-out, and mature Strimzi operations.
Use NATS JetStream if your priority is low-latency service messaging, smaller operational surface, and selective persistence.

Your record should include:

- The platform you choose.
- The reason tied to this scenario.
- The risk that would make you revisit the decision.
- The first failure test you would run.

### Success Criteria

- [ ] The design names at least two streams and their owning teams.
- [ ] Each stream has a partition key tied to a business ordering invariant.
- [ ] Each consumer has a delivery target and an idempotency strategy.
- [ ] Retention covers the stated replay and outage requirements.
- [ ] Backpressure alerts distinguish lag, retention risk, and producer throttling.
- [ ] The Kafka vs NATS decision explains operator posture, not only feature preference.
- [ ] The design explicitly keeps synchronous request/response paths out of the stream.

## Next Module

Continue to [Module 1.2: Apache Kafka on Kubernetes (Strimzi)](../module-1.2-kafka/) to deploy and operate Kafka after you understand the streaming mental model.
