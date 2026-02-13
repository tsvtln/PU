#!/bin/bash
# Build script for custom AWX Execution Environment

set -e

echo "================================================"
echo "Building Custom AWX Execution Environment"
echo "================================================"

# Check if ansible-builder is installed
if ! command -v ansible-builder &> /dev/null; then
    echo "ERROR: ansible-builder is not installed"
    echo "Install it with: pip install ansible-builder"
    exit 1
fi

# Check if podman or docker is available and determine if sudo is needed
USE_SUDO=""
if command -v podman &> /dev/null; then
    RUNTIME="podman"
    # Test if we can run podman without sudo
    if ! podman ps &> /dev/null; then
        echo "Podman requires sudo..."
        USE_SUDO="sudo"
    fi
elif command -v docker &> /dev/null; then
    RUNTIME="docker"
    # Test if we can run docker without sudo
    if ! docker ps &> /dev/null 2>&1; then
        echo "Docker requires sudo (or add user to docker group)..."
        echo "To avoid sudo in future: sudo usermod -aG docker \$USER && newgrp docker"
        USE_SUDO="sudo"
    fi
else
    echo "ERROR: Neither podman nor docker is installed"
    exit 1
fi

echo "Using container runtime: $RUNTIME"
if [ -n "$USE_SUDO" ]; then
    echo "Running with sudo privileges"
fi

# Set the image tag (local image name)
IMAGE_TAG="${1:-localhost/awx-ee-custom:latest}"

# By default we rebuild; set SKIP_BUILD=1 to only push/tag to registry.
SKIP_BUILD="${SKIP_BUILD:-0}"

echo "Local image tag: $IMAGE_TAG"

if [ "$SKIP_BUILD" = "1" ]; then
    echo "SKIP_BUILD=1 -> skipping ansible-builder build step"
else
    echo "Building image: $IMAGE_TAG"
    echo ""

    # Build the execution environment
    if [ -n "$USE_SUDO" ]; then
        $USE_SUDO ansible-builder build \
            --tag "$IMAGE_TAG" \
            --container-runtime "$RUNTIME" \
            --verbosity 3 \
            --build-arg ANSIBLE_BUILDER_BUILD_VERBOSITY=3
    else
        ansible-builder build \
            --tag "$IMAGE_TAG" \
            --container-runtime "$RUNTIME" \
            --verbosity 3 \
            --build-arg ANSIBLE_BUILDER_BUILD_VERBOSITY=3
    fi
fi

echo ""
echo "================================================"
echo "Publishing image to local registry for AWX"
echo "================================================"

# Important:
# - AWX pulls images from inside a container.
# - 'localhost:5000' inside a container points to that container itself, NOT the host.
# - Use a registry container named 'registry' and connect it to the AWX docker network.

REG_NAME="registry"
REG_PORT="5000"
AWX_DOCKER_NETWORK="awx"   # based on your `docker network ls` output
REGISTRY_REF="${REG_NAME}:${REG_PORT}"
AWX_IMAGE_REF="${REGISTRY_REF}/awx-ee-custom:latest"

# Start a registry if not running
if ! docker ps --format "{{.Names}}" | grep -qx "$REG_NAME"; then
    echo "Starting docker registry container '$REG_NAME' on port ${REG_PORT}..."
    # If an old stopped container exists, remove it
    if docker ps -a --format "{{.Names}}" | grep -qx "$REG_NAME"; then
        docker rm -f "$REG_NAME" >/dev/null 2>&1 || true
    fi
    docker run -d --restart=always -p ${REG_PORT}:${REG_PORT} --name "$REG_NAME" registry:2
else
    echo "Registry container '$REG_NAME' already running."
fi

# Ensure registry is connected to the AWX docker network so AWX containers can resolve 'registry:5000'
if docker network inspect "$AWX_DOCKER_NETWORK" >/dev/null 2>&1; then
    if ! docker network inspect "$AWX_DOCKER_NETWORK" --format '{{range .Containers}}{{.Name}}{{"\n"}}{{end}}' | grep -qx "$REG_NAME"; then
        echo "Connecting registry container '$REG_NAME' to docker network '$AWX_DOCKER_NETWORK'..."
        docker network connect "$AWX_DOCKER_NETWORK" "$REG_NAME" 2>/dev/null || true
    else
        echo "Registry container already connected to '$AWX_DOCKER_NETWORK'."
    fi
else
    echo "WARNING: Docker network '$AWX_DOCKER_NETWORK' not found."
    echo "AWX won't be able to reach '${REGISTRY_REF}' by name unless you connect it to the correct network."
fi

# Tag + push to the registry hostname (NOT localhost)
# We always tag from the local image tag produced by ansible-builder
docker tag "$IMAGE_TAG" "$AWX_IMAGE_REF"
docker push "$AWX_IMAGE_REF"

echo ""
echo "================================================"
echo "Build/publish complete"
echo "================================================"
echo ""
echo "Use THIS as the Image in AWX Execution Environment (NOT localhost...):"
echo "  $AWX_IMAGE_REF"
echo ""
echo "In AWX UI: Administration -> Execution Environments"
echo "  Image: $AWX_IMAGE_REF"
echo "  Pull: Missing (or Always if you prefer)"
echo ""
echo "Tip: If you only need to re-push after changes, run:"
echo "  SKIP_BUILD=1 ./build.sh"
