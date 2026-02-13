#!/usr/bin/env bash
set -euo pipefail
AWX_CONTAINER="tools_awx_1"
IMAGE="registry:5000/awx-ee-custom:latest"

echo "Using AWX container: ${AWX_CONTAINER}"
echo

echo "Registry connection check"
docker exec "${AWX_CONTAINER}" sh -lc "getent hosts registry && (nc -zv registry 5000 || true)"

echo
echo "Tool check"
docker exec "${AWX_CONTAINER}" sh -lc "command -v podman || true; command -v skopeo || true; command -v docker || true"

echo
echo "Force insecure registry config inside AWX container (/etc/containers/registries.conf)"
docker exec -u 0 "${AWX_CONTAINER}" sh -lc "mkdir -p /etc/containers && cat >/etc/containers/registries.conf <<'EOF'
unqualified-search-registries = []
[[registry]]
location = \"registry:5000\"
insecure = true
EOF"

echo
echo "pull/inspect INSIDE AWX container"
docker exec "${AWX_CONTAINER}" sh -lc "if command -v skopeo >/dev/null 2>&1; then skopeo inspect --tls-verify=false docker://${IMAGE} | head -n 20; elif command -v podman >/dev/null 2>&1; then podman pull --tls-verify=false ${IMAGE}; else echo 'No skopeo/podman present'; fi"

echo
echo "== GG =="
