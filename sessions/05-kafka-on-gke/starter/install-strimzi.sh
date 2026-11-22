#!/usr/bin/env bash
# Installs the Strimzi operator into the "kafka" namespace.
# Safe to run again: it updates what is already there.
set -euo pipefail

VERSION=1.3.0
URL="https://github.com/strimzi/strimzi-kafka-operator/releases/download/${VERSION}/strimzi-cluster-operator-${VERSION}.yaml"

kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -

# The install file assumes a namespace called "myproject"; point it at "kafka".
# --server-side because Strimzi's resource definitions are too big for a normal apply.
curl -sSL "$URL" \
  | sed 's/namespace: myproject/namespace: kafka/' \
  | kubectl apply --server-side --force-conflicts -n kafka -f -

# By default Strimzi adds PodDisruptionBudgets that let only one Kafka pod stop
# at a time. On a one-node cluster they block scaling to zero, so turn them off.
kubectl -n kafka set env deployment/strimzi-cluster-operator STRIMZI_POD_DISRUPTION_BUDGET_GENERATION=false

kubectl -n kafka rollout status deployment/strimzi-cluster-operator --timeout=300s
echo "Strimzi ${VERSION} is running in the kafka namespace."
