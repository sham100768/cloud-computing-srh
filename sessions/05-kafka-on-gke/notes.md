# Session 5 notes

## Planned
- Recap of session 4: images, the control loop and your own cluster.
- Where today fits: Kafka on your GKE cluster, with the generator sending ocean events into it.
- One container's journey, as events, and everyone who wants them.
- Why put anything in the middle?
- Kafka is a log: offsets, and reading doesn't delete.
- Partitions and keys: a key keeps one shipment in order.
- Three copies, and when one broker dies.
- Consumer groups and lag, replay, and the operator.
- In industry: run Kafka yourself, or buy it?
- Kafka on Kubernetes with Strimzi, and what runs on your node today.
- Workshop: Kafka on your cluster.

## What we covered

### This week
- Today is less about technical detail and more about how things work. Containers, Kubernetes and Kafka are the hardest sessions of the course; it gets easier after this.
- At the board, expect questions on what you considered when you set up your Kubernetes cluster and how you configured Kafka.
- There's no session on Friday. The next session is on Monday 30 November.

### Many producers, many consumers
- One container's trip from Ningbo to Hamburg is a series of events: booked, gate in, loaded, departed, about five weeks at sea, then arrived, discharged and gate out. Each one is a small JSON event.
- Different people want the same event at different speeds: an ops dashboard within a minute, a customer alert within minutes, an exec report once a month, and data science for years.
- With many producers and many consumers, you could wire each producer to each consumer. That's many integrations to build and maintain. Or you put something in the middle that every producer writes to and every consumer reads from. That's Kafka: it decouples consumers from producers.
- You could build something similar yourself, for example on the storage buckets from session 1, but you'd have much more to maintain.
- Kafka costs money to run, and many companies decide they don't need it. When consumers need data within seconds, it's one of the best options.
- The size of your team matters. A small team running many data sources needs a more robust, low-maintenance system than a large team does.

### Kafka is a log
- A log is a list of events you only ever add to, at the end, in the order they arrive.
- Each consumer reads from its own position in the log, so different consumers can be at different points.

### Topics, partitions and keys
- A topic holds one kind of event: `ocean-events` today, perhaps `air-events` or land events elsewhere.
- A topic is split into partitions, like opening several tills in a supermarket instead of one long queue. Partitions are how Kafka scales.
- The key picks the partition. Kafka hashes the key, so the same key always goes to the same partition, and events with the same key stay in order. Today the key is the shipment ID.
- Keep keys simple. The more logic you put into choosing a partition, the slower events get processed.
- How many partitions and topics to use is a design choice of its own; there's more on that in a later session.

### Brokers and copies
- A broker is a server running Kafka; on your cluster, each broker is a pod. The partitions live on the brokers.
- Every partition is stored on three brokers. If one broker goes down, a copy on another broker takes over.
- Streaming systems are among the most highly available systems you'll meet, because they have to be up all the time. Think about how many brokers you need for the availability your launch customer wants.

### Groups, lag, replay and the operator
- **Consumer groups and lag.** Each consumer group keeps its own place in the log. Lag is how far behind it is. A monthly report can be far behind; an ops dashboard can't.
- **Replay.** Kafka keeps messages for as long as the topic's retention says: 30 days for you. A common pattern is to keep about 30 days in Kafka and move older data to cheaper storage.
- **The operator.** Strimzi is an open-source operator that runs Kafka on Kubernetes. You describe the cluster, and it runs the brokers, much as Kubernetes runs your containers.

### Run it, or buy it?
- Like Kubernetes, you can run Kafka yourself on Kubernetes, use a version managed by your cloud, or buy it fully hosted.
- Most companies pick one of the first two to offload some of the maintenance. Self-run needs a platform team with the skills. Smaller companies usually let the cloud manage it, which costs more.
- Kafka on Kubernetes is layers of management: Kubernetes manages the containers, and inside them Kafka manages its own brokers. Each layer needs monitoring, resilience and people who know it. That's why many companies hand it to a cloud provider.

### What runs on your node today
- Three brokers, which are also the controllers; the Strimzi operator; the entity operator, which turns KafkaTopic resources into real topics; your producer; and a client pod for your commands.
- Each broker has its own 10 GB disk. Think about what your design needs: two brokers or three, and how big the disks are.
- In the Lambda architecture, Kafka is part of the fast path.

### Workshop
Wake your cluster (it takes about 10 minutes), rebuild the generator as v2, install Strimzi, and create the Kafka cluster and the topic. Then find your shipment's partition, read the lag, kill a broker, and replay the log. Scale back to zero before you leave, and keep the kafka namespace and its disks. The steps are in [workshop.md](workshop.md). Play with it over the next few days: see how it scales and what happens when things break. Designing systems like this means understanding the business, the containers and the code together.

## Corrections to the recording
- **Next session.** Monday 30 November is Pub/Sub and App Engine (session 6). Dataflow and BigQuery are session 7, on Wednesday 2 December.
- **Pub/Sub is a fast path too, not the slow path.** In the Lambda architecture, both Kafka (ocean events) and Pub/Sub (air events) are in the speed layer. The slow path is the batch layer: rate files land in Cloud Storage, Dataproc processes them, and the results go into BigQuery.
- **You don't decide what each partition is for.** The till analogy stops at "several tills". Kafka hashes the key, and the hash decides the partition. You choose the key, not which partition holds what. A hash is a fixed calculation, not a random number, which is why the same key always lands on the same partition.
- **Today's key is the shipment ID,** not the shipper or the port codes. That keeps each shipment's events in order. Other systems choose other keys, depending on which order they care about.
- **Reads and writes go to each partition's leader.** Every partition has three copies, one on each broker. One copy is the leader, which takes the writes and serves the reads; the other two follow it. The leaders are spread across the brokers. A write counts once two copies have it (`min.insync.replicas=2`). Consumers don't go through a load balancer: they connect to the bootstrap address (`freight-kafka-bootstrap:9092`) to find the leaders, then talk to them directly.
- **Two brokers isn't the same as three.** With three copies and two needed for a write, one broker can fail and writes carry on. With two brokers, losing one stops writes, or you accept writes that only one copy has.
- **Consumers in a group share the partitions.** Kafka assigns each partition to one consumer in the group; you don't usually pick a partition yourself.
- **Kafka stores its log on disk,** not in memory. It uses memory as a cache, and the cost is mainly the always-on brokers: the node's CPU and memory, plus the disks. A 10 GB disk costs about a dollar a month, so the three disks aren't what makes it expensive. The node running all day is.
- **ZooKeeper's replacement is KRaft, not Strimzi.** Since Kafka 4.0, Kafka's own controllers keep the cluster's metadata (KRaft); your three brokers are also the controllers. Strimzi is a separate open-source operator for running Kafka on Kubernetes, a CNCF project rather than part of Kafka. Companies still on ZooKeeper move to KRaft.

## Questions from the room
- **Do we use several nodes in case a region fails?** Spreading brokers across machines and zones protects you when one fails, and regions can fail too. A container can also run out of memory. Plan for things to fail.
- **How do the brokers stay in sync?** Each partition is copied to all three brokers. The leader takes the writes and the followers copy them, so if a broker goes down, a follower on another broker takes over.
- **Can a broker run out of memory or disk?** Yes. A container that goes over its memory limit is killed, and a broker whose disk fills up stops working. Adding nodes doesn't help; you need bigger limits or bigger disks. Autoscaling usually reacts too slowly for a stream with an event every second. The usual approach: test with real volumes (for example, send the last 30 days of data through), size from what you measure, add 20 to 30%, run it in production for a month, then adjust. If you do autoscale, watch how fast usage is rising, not just a fixed threshold.
