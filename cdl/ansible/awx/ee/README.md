# Custom AWX Execution Environment

This directory contains the definition for a custom AWX Execution Environment (EE) that includes the `ldc_custom.azure_manager` collection.

## Prerequisites

On the AWX host, you need:
- `ansible-builder` installed
- `podman` or `docker` installed

Install ansible-builder:
```bash
pip install ansible-builder
```

## Building the Execution Environment

### Option 1: Build on AWX host and use locally

1. SSH to your AWX VM
2. Copy this entire `ee` directory to the AWX host
3. Navigate to the directory:
   ```bash
   cd ~/CAAC/ee
   ```
4. Build the execution environment:
   ```bash
   ansible-builder build --tag localhost/awx-ee-custom:latest --container-runtime podman
   ```

5. In AWX UI:
   - Go to **Administration** → **Execution Environments**
   - Click **Add**
   - Name: `AWX EE Custom`
   - Image: `localhost/awx-ee-custom:latest`
   - Pull: `Missing`
   - Save

6. Update your Job Template to use the new `AWX EE Custom` execution environment

### Option 2: Build and push to a registry

1. Build with a registry tag:
   ```bash
   ansible-builder build --tag your-registry.com/awx-ee-custom:1.0.0 --container-runtime podman
   ```

2. Push to registry:
   ```bash
   podman push your-registry.com/awx-ee-custom:1.0.0
   ```

3. In AWX UI, add the execution environment with the registry URL

## Quick Test (Alternative for POC)

If you just want to test quickly without building a custom EE, you can:

1. Copy the collection tar.gz to AWX's project directory
2. Add a `collections/requirements.yml` in your project:
   ```yaml
   collections:
     - name: /path/to/ldc_custom-azure_manager-1.2.2.tar.gz
       type: file
   ```

3. AWX will install it when the job runs

However, building a custom EE is the **recommended approach** for production use.

## Verifying the Collection

After building and using the EE, your job should be able to find the module:
```
ldc_custom.azure_manager.azure_power_manager
```

## Troubleshooting

- If build fails, check that the path to the tar.gz is correct
- Ensure you have enough disk space for the image build
- Check podman/docker logs for specific errors
- If permission error for docker, run:
```bash
sudo usermod -aG docker $USER
newgrp docker
./build.sh
```