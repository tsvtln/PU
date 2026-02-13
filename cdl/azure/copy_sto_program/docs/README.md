# Azure File Share Copy Program

A modular, reusable Python tool for copying files between Azure storage accounts with verification.

## How the Copy Works

In `core/azure_storage.py` → `copy_file_with_verification()`, we use `download_file()` with an initialized `source_file_client` (authenticated with SPN), which uses the Azure SDK module in `index.py`.

The `download_file()` method in `index.py` is a utility for downloading files from URLs (typically from a package index like PyPI) with built-in verification.

### How It Works Behind the Scenes

#### 1. Block-Based Streaming Download

- Opens URL connection
- Reads file in blocks (chunks)
- For each block:
  - Writes block to destination file
  - Updates digest (MD5/SHA) calculation
  - Calls progress callback (`reporthook`)

#### 2. Progressive Operations

- The method performs three simultaneous operations per block:
  - Read a chunk from the network stream
  - Append the chunk to the destination file on disk
  - Update the cryptographic hash with the chunk's data

#### 3. Reasons to Use This Approach

- **Memory Efficient:** Only one block in memory at a time (not the entire file)
- **Progressive Hash:** Digest calculated incrementally during download
- **Progress Tracking:** `reporthook` callback shows download progress
- **Verification Ready:** After download completes, computed digest is compared with expected digest parameter

#### 4. Key Difference from Azure Copy That Runs Inside a Terminal (CLI)

- **index.py (pip):**
  - Network → Read Block → Write to Disk + Update Hash → Repeat
  - (One-way: Download only)
- **Azure File Share Copy:**
  - Source → Read Block → Upload Block + Update Source Hash → Repeat
  - Then:
    - Destination → Read Block → Update Dest Hash → Repeat
    - Compare Hashes
  - (Two-way: Download + Upload + Verification)

#### 5. Block Appending

- File is opened in append or write-binary mode
- Each block read from the network is immediately appended to the file
- Hash digest is updated with the same block data
- Process repeats until entire file is downloaded
- **Result:** Downloaded file on disk + cryptographic proof (hash) that download succeeded without corruption

#### _TLDR:_ The program recursively walks the source directory tree and recreates the same structure in the destination, copying files one by one with verification. 
#### _Result:_ All files are copied with cryptographic proof (MD5) that source and destination are identical.

## Features

- ✅ Copies files from Premium to Standard Azure storage accounts
- ✅ MD5 checksum verification for all copied files
- ✅ Supports both Azure Global and Azure China environments
- ✅ Automatic discovery of subscriptions and resource groups
- ✅ Modular and reusable architecture
- ✅ SSL verification handling for corporate environments
- ✅ Detailed logging and progress tracking

## Installation

### Prerequisites

- Python 3.7 or higher
- Azure subscription with appropriate permissions
- Service Principal credentials

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in directory (`src/`) with your credentials:

```ini
# Azure Global credentials
tenant_id="your-tenant-id"
client_id="your-client-id"
client_secret="your-client-secret"

# Azure China credentials (optional)
tenant_id_china="your-china-tenant-id"
client_id_china="your-china-client-id"
client_secret_china="your-china-client-secret"
```

Alternatively, set the following environment variables:

```ini
tenant_id="your-tenant-id"
client_id="your-client-id"
client_secret="your-client-secret"
tenant_id_china="your-china-tenant-id"
client_id_china="your-china-client-id"
client_secret_china="your-china-client-secret"
```

## Usage

### Basic Usage (Auto-discovery)

```bash
python main.py \
  --source-storage-account srcaccount \
  --source-share srcshare \
  --dest-storage-account destaccount \
  --dest-share destshare
```

### With Resource Groups Specified (Faster)

```bash
python main.py \
  --source-storage-account srcaccount \
  --source-resource-group src-rg \
  --source-share srcshare \
  --dest-storage-account destaccount \
  --dest-resource-group dest-rg \
  --dest-share destshare
```

### Azure China Environment

```bash
python main.py \
  --source-storage-account srcaccount \
  --source-share srcshare \
  --dest-storage-account destaccount \
  --dest-share destshare \
  --environment china
```

### Additional Options

- `--dec`: Use python-decouple config() instead of os.getenv() (meaning it will read from .env file)
- `--enable-ssl-verify`: Enable SSL certificate verification
- `--environment <global/china>`: Specify Azure environment (default: global)

## Module Structure

```
copy_sto_program/
├── __init__.py          # Package initialization
├── main.py              # Main entry point
├── azure_auth.py        # Authentication handling
├── azure_discovery.py   # Resource discovery
├── azure_storage.py     # Storage operations
├── config.py            # Configuration classes
└── utils.py             # Utility functions
```

### Module Descriptions

- **azure_auth.py**: Handles Azure authentication using Service Principal
- **azure_discovery.py**: Discovers subscriptions and resource groups
- **azure_storage.py**: Manages storage operations and file copying
- **config.py**: Configuration dataclasses and environment settings
- **utils.py**: Helper functions for formatting, verification, etc.

## Using as a Library

You can import and use the modules in your own scripts:

```python
from azure_auth import AzureAuthenticator
from azure_discovery import AzureDiscovery
from azure_storage import AzureStorageManager, FileShareCopier
from config import StorageAccountConfig, CopyConfig
from utils import setup_ssl_verification

# Setup
setup_ssl_verification(disable=True)

# Authenticate
auth = AzureAuthenticator(environment='global')
auth.load_env_file()
credential = auth.authenticate()

# Discover resources
discovery = AzureDiscovery(credential, environment='global')
sub_id, rg, _ = discovery.find_storage_account_location('mystorageaccount')

# Perform operations
storage_mgr = AzureStorageManager(credential, sub_id, environment='global')
details = storage_mgr.get_storage_account_details(rg, 'mystorageaccount')
```

## Error Handling

The program includes comprehensive error handling:
- Azure API errors with status codes
- SSL verification issues
- Missing credentials
- Resource not found errors
- File copy and verification failures

## Security

- Credentials are loaded from `.env` file (not committed to version control)
- SSL verification can be disabled for corporate proxy environments
- Service Principal authentication (no user passwords)

## Author

tsvetelin.maslarski-ext@ldc.com

## License

LDC Internal use only
