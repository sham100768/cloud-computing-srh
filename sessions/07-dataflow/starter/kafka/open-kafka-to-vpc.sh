#!/usr/bin/env bash
# Gives Kafka a second listener that Dataflow can reach.
#
# Dataflow's workers are VMs in your VPC, outside the cluster, so they can't use
# freight-kafka-bootstrap:9092. This listener is a NodePort on the node's
# internal IP: reachable inside your VPC, not from the internet.
#
# Strimzi restarts the three brokers one at a time to add it: 3 to 5 minutes.
# Safe to run again: it does nothing if the listener is already there.
set -euo pipefail

if kubectl -n kafka get kafka freight -o jsonpath='{.spec.kafka.listeners[*].name}' | grep -qw vpc; then
  echo "The vpc listener is already there."
else
  kubectl -n kafka patch kafka freight --type=json -p '[{
    "op": "add", "path": "/spec/kafka/listeners/-",
    "value": {"name": "vpc", "port": 9094, "type": "nodeport", "tls": false,
              "configuration": {"preferredNodePortAddressType": "InternalIP"}}
  }]'
  echo "Added. Waiting for the brokers to restart with it..."
fi

kubectl -n kafka wait kafka/freight --for=condition=Ready --timeout=600s
until BOOTSTRAP=$(kubectl -n kafka get kafka freight \
    -o jsonpath='{.status.listeners[?(@.name=="vpc")].bootstrapServers}') && [ -n "$BOOTSTRAP" ]; do
  sleep 10
done
echo "Dataflow can reach Kafka at: $BOOTSTRAP"
