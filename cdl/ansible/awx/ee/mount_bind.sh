#!/usr/bin/env bash
set -euo pipefail

# Mount + registry helper for AWX docker-compose installs.
#
# Why:
# - Your custom module needs a host file (CSV inventory) available inside the AWX container.
# - AWX pulls EEs using containers/image semantics and will try HTTPS unless registry is marked insecure.
#
# This script is idempotent and does BOTH:
#  1) Ensure /mnt/opcon-archive is bind-mounted into the AWX container via docker-compose.yml
#  2) Ensure the AWX container is configured to treat registry:5000 as an insecure (HTTP) registry

COMPOSE_DIR="/home/ubuntu/setup/awx/tools/docker-compose/_sources"
COMPOSE_FILE="${COMPOSE_DIR}/docker-compose.yml"

HOST_MOUNT_SRC="/mnt/opcon-archive"
CONTAINER_MOUNT_DST="/mnt/opcon-archive"
MOUNT_LINE="${HOST_MOUNT_SRC}:${CONTAINER_MOUNT_DST}:ro"

REGISTRY_HOST="registry"
REGISTRY_PORT="5000"
REGISTRY_REF="${REGISTRY_HOST}:${REGISTRY_PORT}"
EE_IMAGE="${REGISTRY_REF}/awx-ee-custom:latest"

INVENTORY_FILE_REL="Archive/7D/UPD/azure_VMs_inventory-global-china-20260210.csv"

find_awx_service() {
  if grep -qE '^[[:space:]]+awx_1:[[:space:]]*$' "$COMPOSE_FILE"; then
    echo "awx_1"; return
  fi
  if grep -qE '^[[:space:]]+tools_awx_1:[[:space:]]*$' "$COMPOSE_FILE"; then
    echo "tools_awx_1"; return
  fi
  echo ""
}

find_awx_container() {
  docker ps --format '{{.Names}}\t{{.Image}}' | awk '/\t.*awx/ {print $1}' | head -n 1
}

compose_validate() {
  (cd "$COMPOSE_DIR" && docker compose config --services >/dev/null 2>&1)
}

restore_latest_backup() {
  local latest
  latest="$(ls -1t "${COMPOSE_FILE}.bak."* 2>/dev/null | head -n 1 || true)"
  if [ -z "$latest" ]; then
    echo "No backup files found (${COMPOSE_FILE}.bak.*). Can't auto-restore."
    return 1
  fi
  echo "Restoring latest backup: $latest"
  cp -a "$latest" "$COMPOSE_FILE"
}

insert_mount_minimal() {
  local svc="$1"

  # If mount exists anywhere, do nothing (we don't try to be clever about correcting a broken line;
  # compose validation will catch that and we restore from a backup).
  if grep -Fq "$MOUNT_LINE" "$COMPOSE_FILE"; then
    echo "OK: mount already present in compose file"
    return 0
  fi

  cp -a "$COMPOSE_FILE" "${COMPOSE_FILE}.bak.$(date +%s)"

  python3 - "$COMPOSE_FILE" "$svc" "$MOUNT_LINE" <<'PY'
import sys, re
path, svc, mount = sys.argv[1], sys.argv[2], sys.argv[3]

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find service header and indent
svc_hdr_idx = None
svc_indent = None
for i, line in enumerate(lines):
    m = re.match(r"^(\s*)(%s):\s*$" % re.escape(svc), line)
    if m:
        svc_hdr_idx = i
        svc_indent = len(m.group(1))
        break
if svc_hdr_idx is None:
    raise SystemExit(f"Could not find service '{svc}:' in {path}")

# Determine end of service block
end_idx = len(lines)
for j in range(svc_hdr_idx + 1, len(lines)):
    if re.match(r"^\s*[#\n\r]*$", lines[j]):
        continue
    m2 = re.match(r"^(\s*)[A-Za-z0-9_\-]+:\s*$", lines[j])
    if m2 and len(m2.group(1)) == svc_indent:
        end_idx = j
        break

block = lines[svc_hdr_idx:end_idx]

# Find volumes key in this service
vol_key_idx = None
vol_indent = None
for k, line in enumerate(block):
    m3 = re.match(r"^(\s*)volumes:\s*$", line)
    if m3:
        vol_key_idx = k
        vol_indent = len(m3.group(1))
        break

if vol_key_idx is not None:
    # Append mount as the last item under volumes
    insert_at = svc_hdr_idx + vol_key_idx + 1
    while insert_at < end_idx:
        ln = lines[insert_at]
        if re.match(r"^\s*$", ln) or re.match(r"^\s*#", ln):
            insert_at += 1
            continue
        if re.match(r"^\s*-\s+", ln) and (len(ln) - len(ln.lstrip(" "))) > vol_indent:
            insert_at += 1
            continue
        break
    mount_line = " " * (vol_indent + 2) + f"- {mount}\n"
    lines.insert(insert_at, mount_line)
else:
    # Insert a new volumes block right after service header
    volumes_key = " " * (svc_indent + 2) + "volumes:\n"
    mount_line = " " * (svc_indent + 4) + f"- {mount}\n"
    lines.insert(svc_hdr_idx + 1, mount_line)
    lines.insert(svc_hdr_idx + 1, volumes_key)

with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)
PY
}

ensure_registry_insecure_inside_awx() {
  local awx_container="$1"

  echo "Configuring insecure registry inside AWX container ($awx_container): ${REGISTRY_REF}"

  # Ensure registry is resolvable/reachable inside the container
  docker exec "$awx_container" sh -lc "getent hosts ${REGISTRY_HOST} >/dev/null 2>&1 || true"

  # Write /etc/containers/registries.conf inside the AWX container.
  # This is what causes the HTTPS->HTTP mismatch if absent.
  docker exec -u 0 "$awx_container" sh -lc "mkdir -p /etc/containers; cat >/etc/containers/registries.conf <<'EOF'
unqualified-search-registries = []

[[registry]]
location = \"${REGISTRY_REF}\"
insecure = true
EOF"

  # Best-effort sanity check: if skopeo exists, confirm it can talk to the registry over HTTP.
  docker exec "$awx_container" sh -lc "command -v skopeo >/dev/null 2>&1 && skopeo inspect --tls-verify=false docker://${EE_IMAGE} >/dev/null 2>&1 && echo 'OK: skopeo can reach registry' || true"
}

main() {
  echo "++++ sanity check: host file exists ++++"
  if [ ! -f "${HOST_MOUNT_SRC}/${INVENTORY_FILE_REL}" ]; then
    echo "ERROR: Expected file missing on host: ${HOST_MOUNT_SRC}/${INVENTORY_FILE_REL}"
    exit 1
  fi
  ls -la "${HOST_MOUNT_SRC}/$(dirname "$INVENTORY_FILE_REL")"

  echo
  echo "++++ validate docker compose file ++++"
  if ! compose_validate; then
    echo "Compose file is currently broken: ${COMPOSE_FILE}"
    echo "Attempting to restore latest backup..."
    restore_latest_backup
  fi

  if ! compose_validate; then
    echo "ERROR: Compose file still doesn't validate after restore."
    echo "Run: (cd ${COMPOSE_DIR} && docker compose config) to see the exact parse error."
    exit 1
  fi

  local svc
  svc="$(find_awx_service || true)"
  if [ -z "$svc" ]; then
    echo "ERROR: Could not detect AWX service in compose (expected awx_1 or tools_awx_1)."
    echo "Available services:"
    (cd "$COMPOSE_DIR" && docker compose config --services) || true
    exit 1
  fi
  echo "Detected AWX service: $svc"

  echo
  echo "++++ apply bind mount to compose ++++"
  insert_mount_minimal "$svc"

  echo
  echo "++++ re-validate compose after edit ++++"
  if ! compose_validate; then
    echo "ERROR: Compose became invalid after edit. Restoring latest backup..."
    restore_latest_backup
    exit 1
  fi
  echo "OK: compose validates"

  echo
  echo "++++ restart stack ++++"
  (cd "$COMPOSE_DIR" && docker compose down --remove-orphans)
  (cd "$COMPOSE_DIR" && docker compose up -d)

  echo
  echo "++++ verify mount inside AWX container ++++"
  sleep 2
  local awx_container
  awx_container="$(find_awx_container || true)"
  [ -z "$awx_container" ] && awx_container="tools_awx_1"

  echo "AWX container: $awx_container"
  docker exec "$awx_container" sh -lc "ls -la ${CONTAINER_MOUNT_DST}/Archive/7D/UPD && test -f ${CONTAINER_MOUNT_DST}/${INVENTORY_FILE_REL} && echo OK"

  echo
  echo "++++ configure insecure registry INSIDE AWX container ++++"
  ensure_registry_insecure_inside_awx "$awx_container"

  echo
  echo "Done. In AWX UI, set the Execution Environment image to: ${EE_IMAGE}"
  echo "Then re-run your job. Both the registry pull and the mounted inventory file should work."
}

main "$@"
