Step 1: Log in to Azure Portal

- Go to https://portal.azure.com.

- Log in with your credentials.

============================================================================
Step 2: Select the Correct Subscription

- In the top right, click your profile.

- Click Switch directory and Switch to LDCLab

============================================================================
Step 3: Create a Resource Group

- In the left menu, click Resource groups.

- Click + Create.

- Enter a name.

- Select the region (e.g., West Europe or your preferred region).

- Click Review + Create, then Create.

** Or use an existing one, for example I had available: CDM1KTSVRSG001

============================================================================
Step 4: Create a Virtual Network, Subnets, IPAM, and Bastion

- In the left menu, search for Virtual networks.
- Click + Create.
- Fill in:
  * Name: e.g., AWX-POC-VNet
  * Region: same as resource group, e.g. (Europe) West Europe
  * Resource group: select your group
  * Address space: e.g., 10.0.0.0/16 (allows multiple subnets)

- Under IP Addresses, click + Add subnet and create:
  * AKS Subnet: Name ATW-POC-Subnet, Address range 10.0.0.0/24 (if your VNet address space is 10.0.0.0/16, 
you can start your subnet at 10.0.0.0 with a /24 mask)
  * App Gateway Subnet: Name AppGatewaySubnet, Address range 10.0.1.0/24 
(next available /24 in the VNet; manually enter this range if not listed; for Subnet Purpose, 
select "Application Gateway subnet" or similar)
  * Bastion Subnet: Name AzureBastionSubnet, Address range 10.0.2.0/27 (required name for Bastion, next available range)

- In the Security tab during subnet or virtual network creation, you can choose to Enable Azure Bastion. 
This is recommended if you want secure, browser-based RDP/SSH access to your VMs without exposing 
them to the public internet. Enable it if you plan to use Bastion for VM access; otherwise, 
you can skip this step for a basic setup.

- (Optional) For advanced IPAM, use Azure Private DNS Zones and custom address spaces. 
For most POCs, default settings are sufficient.

- Click Review + Create, then Create.

----------------------------------------------------------------------------
Step 4a: Create Azure Bastion (for secure VM access)

- In the left menu, search for Bastion.
- Click + Create.
- Fill in:
  * Name: e.g., AWX-POC-Bastion
  * Region: same as VNet
  * Resource group: select your group
  * Virtual network: select AWX-POC-VNet
  * Subnet: select AzureBastionSubnet
  * Public IP: create new or use existing
- Click Review + Create, then Create.

----------------------------------------------------------------------------
Step 4b: Network Security Groups (NSG)

- (Optional but recommended) Create a dedicated NSG for each subnet 
    (AKS, App Gateway, Bastion) to control inbound/outbound traffic. 
    This allows you to apply specific security rules tailored to each subnet's purpose.
- Attach each NSG to its respective subnet via Networking > Network security groups.
- Example rules:
  * AKS Subnet NSG: Allow inbound 443, 80 (AWX web/API), 5432 (if using external PostgreSQL DB), 
    and outbound 22/5986 to managed hosts (SSH/WinRM for Ansible inventory). 
  * App Gateway Subnet NSG: Allow traffic from the internet to the gateway frontend (80, 443).
  * Bastion Subnet NSG: Allow only Bastion management ports (e.g., 443, 22).

============================================================================
Step 5: Create Azure Container Registry (ACR)

- Search for Container Registry.

- Click + Create.

- Fill in:
* Registry name: e.g., atwpocacr
* Resource group: select your group
* Location: same as above
* SKU: Basic (for small POC)

- Click Review + Create, then Create.


============================================================================
Step 6: Create AKS Cluster (Detailed for AWX Deployment)

1. In Azure Portal, search for "Kubernetes services" and click "+ Create".

----------------------------------------------------------------------------
**Basics Tab**
- Subscription: Select your subscription (e.g., CDM1TAZUSUBF02)
- Resource group: Select your resource group (e.g., CDM1KTSVRSG001)
- Cluster name: CSM1KATWAKS001
- Region: Select the same region as your VNet (e.g., West Europe)
- Kubernetes version: Use the default or latest stable
- Availability zones: Optional (for HA)

----------------------------------------------------------------------------
**Node pools Tab**
- Node pool name: nodepool1 (default)
- VM size: D2as_v4 (as per requirements)
- Node count: 2 (for small POC)
- Scale method: Manual (default)
- OS type: Linux
- Max pods per node: Default is fine
- Enable virtual nodes: No (unless you need ACI integration)

----------------------------------------------------------------------------
**Node pools Tab (Step-by-step for adding a new node pool)**
- Node pool name: Enter a unique name (e.g., awxpool, nodepool2)
- Mode: Select "User" for AWX workloads ("System" is for system pods only)
- OS SKU: Select "Ubuntu" (recommended for AWX)
- Availability zones: Select one or more zones for high availability (optional)
- Enable Azure Spot instances: Leave disabled unless you want low-cost, preemptible nodes (not recommended for AWX)
- Node size: Choose a VM size (e.g., D2as_v4 for AWX, or larger if needed)
- Scale method: Choose "Autoscale" (recommended) to automatically adjust node count based on workload, or "Manual" for a fixed number of nodes
- Minimum node count: Set to 1 (minimum recommended for test/dev)
- Maximum node count: Set based on your expected workload (e.g., 5 for POC, up to 1000 per pool for large clusters)

**Example for AWX node pool:**
- Node pool name: awxpool
- Mode: User
- OS SKU: Ubuntu
- Availability zones: 1, 2, 3 (if available)
- Enable Azure Spot instances: No
- Node size: D2as_v4
- Scale method: Autoscale
- Minimum node count: 1
- Maximum node count: 5

**Notes:**
- For AWX, use a "User" mode node pool.
- Autoscale is recommended for flexibility.
- Spot instances are not recommended for AWX unless you are running non-critical workloads.

----------------------------------------------------------------------------
**Networking Tab (Step-by-step for AWX)**
- Private access: Enable private cluster: No (unless you want API access restricted to VNet only)
- Public access: Set authorized IP ranges (optional; add your public IP for security, or leave open for POC)
- Network configuration: Bring your own Azure virtual network
  - Virtual network: AWX-POC-VNet
  - Subnet: ATW-POC-Subnet
- DNS name prefix: CSM1KATWAKS001-dns
- Enable Cilium dataplane and network policy: No (leave disabled unless required)
- Network policy: Azure (default)
- Load balancer: Standard

----------------------------------------------------------------------------
**Integrations Tab**
- Container registry: Select atwpocacr (your ACR)
- Azure Monitor for containers: Enable if you want monitoring/logs
- Enable managed identity: Yes (default)

----------------------------------------------------------------------------
**Monitoring Tab**
- Enable monitoring: Yes (recommended)
- Log Analytics workspace: Create new or select existing

----------------------------------------------------------------------------
**Security Tab**
- Enable RBAC: Yes (recommended)
- Enable Azure AD integration: Optional (for enterprise auth)
- Enable local accounts: Yes (default)
- Enable managed identity: Yes (default)
- Enable pod security policy: Optional

----------------------------------------------------------------------------
**Advanced Tab**
- Enable Kubernetes dashboard: No (deprecated)
- Enable Azure Policy: Optional
- Enable private cluster: No (unless required)
- Enable node pool labels/tags: Optional

----------------------------------------------------------------------------
**Tags Tab**
- Add tags for cost management, environment, owner, etc. (e.g., Environment: POC, Owner: ATW)

----------------------------------------------------------------------------
**Review + Create Tab**
- Review all settings
- Click "Create" to deploy the AKS cluster

============================================================================
After deployment, use Azure CLI to connect:
_NOTE:_ I used https://portal.azure.com/#cloudshell/ because I couldn't find a jumphost to successfully connect me to the AKS cluster otherwise.
az aks get-credentials --resource-group CDM1KTSVRSG001 --name CSM1KATWAKS001
kubectl get nodes

============================================================================
Step 7: Create Application Gateway (for AWX Ingress)

- Search for Application Gateway.
- Click + Create.
- Fill in:
  * Name: CSM1NATWAGW001
  * Region: same as above
  * Resource group: select your group
  * Tier: Standard_v2 (for POC)
  * Virtual network: select ATW-POC-VNet
  * Subnet: select AppGatewaySubnet (10.0.1.0/24)
- Configure frontend IP (public for POC, unless you want private access)
- Configure backend pool (leave empty for now, will point to AKS service after AWX is deployed)
- Click Review + Create, then Create.

============================================================================
Step 8: Deploy AWX to AKS (Minimum POC)

1. Install kubectl and helm if not already installed (not needed when running in cloudshell):
   - https://kubernetes.io/docs/tasks/tools/
   - https://helm.sh/docs/intro/install/

2. Connect to your AKS cluster:
   az aks get-credentials --resource-group CDM1KTSVRSG001 --name CSM1KATWAKS001

3. Create a namespace for AWX:
   kubectl create namespace awx

4. Install AWX Operator using the official Helm chart repository (recommended)

----------------------------------------------------------------------------
# 1. Add the AWX Operator Helm chart repository
helm repo add awx-operator https://ansible-community.github.io/awx-operator-helm/
helm repo update

# 2. Install the AWX Operator in the 'awx' namespace (recommended)
helm install my-awx-operator awx-operator/awx-operator -n awx --create-namespace

# 3. (Optional) To install a specific version or use custom values:
# helm install my-awx-operator awx-operator/awx-operator -n awx --create-namespace --version <version> -f my-values.yml

# 4. Continue with AWX deployment as described below

# Download the AWX custom resource manifest that matches your installed operator version.
# Do NOT use the devel branch for production/stable deployments, as it may contain breaking changes.
# Always use the manifest from the tag/release that matches your operator version (e.g., 3.2.0):
# wget https://raw.githubusercontent.com/ansible/awx-operator/3.2.0/config/samples/awx_v1beta1_awx.yaml
# kubectl apply -f awx_v1beta1_awx.yaml -n awx

# If no versioned manifest is available (e.g., 3.2.0 returns 404), use the devel branch manifest:
wget https://raw.githubusercontent.com/ansible/awx-operator/devel/config/samples/awx_v1beta1_awx.yaml
kubectl apply -f awx_v1beta1_awx.yaml -n awx

# WARNING: The devel branch manifest may not exactly match your installed operator version and is not recommended for production. Use only for POC/testing if no versioned manifest is available.

# Example manifest content (for reference):
---
apiVersion: awx.ansible.com/v1beta1
kind: AWX
metadata:
  name: example-awx
spec:
  service_type: nodeport
  postgres_storage_class: azurefile
  web_resource_requirements:
    requests:
      cpu: 50m
      memory: 128M
  task_resource_requirements:
    requests:
      cpu: 50m
      memory: 128M
  ee_resource_requirements:
    requests:
      cpu: 50m
      memory: 64M

# Edit resource requirements as needed for your environment.
# Other sample files in config/samples are for advanced use cases (ingress, resource limits, backup/restore).

----------------------------------------------------------------------------

6. Deploy AWX custom resource:
   # Download the sample AWX custom resource manifest from the official documentation or the operator's GitHub repo.
   # As of November 2025, the recommended way is to use the example from the official docs:
   # https://docs.ansible.com/projects/awx-operator/en/latest/installation/basic-install.html

   # Example:
   wget https://raw.githubusercontent.com/ansible/awx-operator/2.19.1/config/samples/awx.yaml
   kubectl apply -f awx.yaml -n awx

   # (You can edit awx.yaml for custom settings, but defaults are fine for POC)

7. Wait for AWX pods to be ready:
   kubectl get pods -n awx

8. Expose AWX web service:
   kubectl expose service awx-service --type=LoadBalancer --name=awx-lb -n awx
   # Get the external IP:
   kubectl get svc awx-lb -n awx

9. Access AWX web UI:
   - Open the external IP in your browser.
   - Default credentials are usually admin / password (check the operator logs for the generated password).

============================================================================
Step 9: (Optional) Integrate Application Gateway with AWX

- In Application Gateway, add a backend pool pointing to the AWX LoadBalancer external IP.
- Create a listener and routing rule to forward traffic from the frontend IP to the AWX backend pool.
- For POC, you can access AWX directly via the LoadBalancer IP and skip App Gateway integration if not needed.

============================================================================
Step 10: Verify and Test AWX

- Log in to AWX web UI.
- Create a test project, inventory, and job template.
- Run a simple Ansible job to verify AWX functionality.

============================================================================

# How to find your AWX Custom Resource (CR)

1. List all AWX custom resources in the awx namespace:
   kubectl get awx -n awx
   ### Output example:
   ``` 
   NAME       AGE
   awx-demo   4m50s
   ```

2. Get the YAML for a specific AWX CR:
   ``` 
    kubectl get awx <name> -n awx -o yaml
   ```
   _Replace <name> with the value from the NAME column (e.g., awx-demo)_

3. Do NOT use 'kubectl get awx-demo' (this is not a resource type).
   Always use 'kubectl get awx <name>'

4. To see all AWX CRs in all namespaces:
   ```
   kubectl get awx --all-namespaces
   ```
6. The YAML file you applied (e.g., awx-demo.yml) is your AWX CR manifest in source form.



# Additional pointers and references

### Install guide:
https://docs.ansible.com/projects/awx-operator/en/latest/installation/basic-install.html


### Helpful commands:
```
kubectl describe pod awx-demo-postgres-15-0 -n awx
kubectl get pods --all-namespaces
kubectl get pods -n awx
kubectl get storageclass
kubectl describe pvc 
kubectl get statefulset
kubectl edit statefulset awx-demo-postgres-15
```

### Configs:
```
tsvetelin [ ~/awx-operator ]$ cat kustomization.yaml 
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  # Find the latest tag here: https://github.com/ansible/awx-operator/releases
  - github.com/ansible/awx-operator/config/default?ref=2.19.1
  - awx-demo.yml
  - postgres.yaml

# Set the image tags to match the git version from above
images:
  - name: quay.io/ansible/awx-operator
    newTag: 2.19.1

# Specify a custom namespace in which to install AWX
namespace: awx

tsvetelin [ ~/awx-operator ]$ cat awx-demo.yml 
---
apiVersion: awx.ansible.com/v1beta1
kind: AWX
metadata:
  name: awx-demo
spec:
  service_type: nodeport
  postgres_storage_class: managed-cs
  
tsvetelin [ ~/awx-operator ]$ cat postgres.yaml 
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-15-awx-demo-postgres-15-0
  namespace: awx
spec:
  storageClassName: managed-csi
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 8Gi
	  
tsvetelin [ ~/awx-operator ]$ cat scawx.yaml 
# Source - https://stackoverflow.com/a
# Posted by PjoterS
# Retrieved 2025-12-03, License - CC BY-SA 4.0

kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: manual
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer


After deployment run:
kubectl -n awx patch pod awx-demo-postgres-15-0 --type='merge' -p '{"spec":{"securityContext":{"fsGroup":1000}}}'
kubectl -n awx delete pod awx-demo-postgres-15-0
```