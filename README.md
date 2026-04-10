# yc-ops

CLI for managing Yandex Cloud resources. Start, stop, and monitor VMs and managed databases with one command.

Works standalone and as a tool for AI agents (Claude Code, Cursor, etc.) via bash.

## Install

```bash
# with uv (recommended)
uv tool install yc-ops

# or with pip
pip install yc-ops
```

## Prerequisites

### 1. Install Yandex Cloud CLI

```bash
curl -sSL https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash
```

Restart your shell, then:

```bash
yc init
```

This will ask you to log in and select a default folder.

### 2. Create a service account (for servers / CI)

If you run yc-ops on a server or in CI (not your laptop), create a service account:

```bash
# Create account
yc iam service-account create --name yc-ops-sa

# Get its ID
SA_ID=$(yc iam service-account get yc-ops-sa --format json | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")

# Grant editor role on your folder
FOLDER_ID=$(yc config get folder-id)
yc resource-manager folder add-access-binding $FOLDER_ID \
  --role editor \
  --subject serviceAccount:$SA_ID

# Create authorized key
yc iam key create --service-account-name yc-ops-sa --output sa-key.json

# Authenticate as service account
yc config profile create yc-ops
yc config set service-account-key sa-key.json
yc config set folder-id $FOLDER_ID
```

Keep `sa-key.json` safe. Do not commit it to git.

## Quick start

```bash
# Interactive setup: register your resources
yc-ops init

# Manage resources
yc-ops start          # start all
yc-ops stop           # stop all
yc-ops status         # show status table
yc-ops start my-vm    # start specific resource
yc-ops stop my-pg     # stop specific resource

# Config management
yc-ops config         # show current config
yc-ops remove my-vm   # remove resource from config
```

## Supported resource types

| Type | Examples |
|------|----------|
| `compute` | VMs, preemptible instances |
| `managed-postgresql` | Managed PostgreSQL clusters |
| `managed-mysql` | Managed MySQL clusters |
| `managed-clickhouse` | Managed ClickHouse clusters |
| `managed-redis` | Managed Redis clusters |

## Configuration

Config is stored in `~/.config/yc-ops/config.yaml`:

```yaml
yc_path: ~/.yandex-cloud/bin/yc
resources:
  - name: my-app-server
    type: compute
  - name: my-pg-cluster
    type: managed-postgresql
```

Override config location with `YC_OPS_CONFIG_DIR` env variable.

## Usage with AI agents

Any agent that can run bash commands can use yc-ops:

```bash
# In Claude Code CLAUDE.md or any agent instructions:
# "Use `yc-ops status` to check infrastructure, `yc-ops start` before deploy, `yc-ops stop` after."
```

## License

MIT
