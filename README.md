# Std-Setup: Ansible Server Hardening Repository

Ansible repository for standard server configuration and hardening with multi-distro support (Debian/Ubuntu and RHEL/Rocky).

## Features

- **Comprehensive Server Hardening**: SSH hardening, firewall, fail2ban, auditd, IPv6 disable, SELinux/AppArmor
- **Multi-Distro Support**: Automatically detects and configures based on OS family
- **Modular Roles**: Separated into common, webserver, database, and app
- **Environment Separation**: Production and staging inventories
- **Custom SSH Port**: Default port 2222 (configurable)
- **Test Coverage**: 76+ tests via Molecule + testinfra across 6 scenarios

## Requirements

- Ansible >= 2.9
- Python 3 on target hosts
- SSH access with key-based authentication

## Quick Start

### 1. Install Dependencies

```bash
make deps
```

Or manually:

```bash
ansible-galaxy collection install -r requirements.yml
```

### 2. Configure Inventory

Edit `inventory/production/hosts.yml` with your servers:

```yaml
all:
  children:
    webservers:
      hosts:
        web01.example.com:
        web02.example.com:
    databases:
      hosts:
        db01.example.com:
    appservers:
      hosts:
        app01.example.com:
```

### 3. Set Authorized Keys

Edit `inventory/production/group_vars/all.yml` and add your SSH public key:

```yaml
ssh_authorized_keys:
  - "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... user@workstation"
```

### 4. Run Playbook

```bash
# Apply all configuration
make run

# Or per category
make run-web
make run-db
make run-app

# Dry-run (check mode)
make check

# Target specific roles
ansible-playbook --tags "ssh,firewall" playbooks/site.yml
```

## Directory Structure

```
std-setup/
├── ansible.cfg                    # Ansible configuration
├── .ansible-lint                  # Ansible-lint rules
├── Makefile                       # Command shortcuts for all operations
├── requirements.yml               # Collection/role dependencies
├── inventory/
│   ├── production/               # Production environment
│   │   ├── hosts.yml
│   │   └── group_vars/
│   └── staging/                  # Staging environment
│       ├── hosts.yml
│       └── group_vars/
├── roles/
│   ├── common/                   # Hardening & base config
│   │   └── molecule/default/     # Molecule tests (33 tests)
│   ├── webserver/                # Nginx/Apache
│   │   └── molecule/default/     # Molecule tests (10 tests)
│   ├── database/                 # MySQL/PostgreSQL
│   │   ├── molecule/mysql/       # Molecule tests (8 tests)
│   │   └── molecule/postgresql/  # Molecule tests (6 tests)
│   └── app/                      # Node.js/Python/Java
│       ├── molecule/nodejs/      # Molecule tests (11 tests)
│       └── molecule/python/      # Molecule tests (8 tests)
└── playbooks/
    ├── site.yml                  # Master playbook
    ├── webserver.yml
    ├── database.yml
    └── app.yml
```

## Running Tests

### Prerequisites

```bash
make dev-deps
```

Or manually:

```bash
pip install molecule molecule-plugins[docker] docker pytest-testinfra
```

### Run Tests

```bash
# Run all tests
make test

# Run specific role tests
make test-common     # common role (debian12, ubuntu2204)
make test-web        # webserver role (debian12, ubuntu2204)
make test-mysql      # database role with MySQL
make test-pgsql      # database role with PostgreSQL
make test-nodejs     # app role with Node.js
make test-python     # app role with Python

# List available scenarios
make test-list
```

### Test Scenarios Overview

| Role | Scenario | Platforms | Test Count |
|------|----------|-----------|------------|
| `common` | `default` | debian12, ubuntu2204 | 33 tests |
| `webserver` | `default` | debian12, ubuntu2204 | 10 tests |
| `database` | `mysql` | debian12 | 8 tests |
| `database` | `postgresql` | debian12 | 6 tests |
| `app` | `nodejs` | debian12 | 11 tests |
| `app` | `python` | debian12 | 8 tests |

> **Note**: Docker containers require network access to install packages. Ensure your Docker environment can reach package repositories before running tests.

## Makefile Commands

All operations can be run via `make`. See all targets:

```bash
make help
```

### Dependencies

| Command | Description |
|---------|-------------|
| `make deps` | Install Ansible Galaxy collections from `requirements.yml` |
| `make dev-deps` | Install Python test dependencies (molecule, testinfra, ansible-lint) |

### Linting

| Command | Description |
|---------|-------------|
| `make lint` | Run `ansible-lint` on the entire repo |

### Playbooks

| Command | Description |
|---------|-------------|
| `make run` | Run `site.yml` against production inventory |
| `make run-staging` | Run `site.yml` against staging inventory |
| `make run-web` | Run `webserver.yml` playbook |
| `make run-db` | Run `database.yml` playbook |
| `make run-app` | Run `app.yml` playbook |
| `make check` | Dry-run `site.yml` against production (`--check` mode) |
| `make check-staging` | Dry-run `site.yml` against staging (`--check` mode) |

### Testing (Molecule)

| Command | Description |
|---------|-------------|
| `make test` | Run ALL molecule tests (6 scenarios) |
| `make test-common` | Test `common` role (debian12, ubuntu2204) |
| `make test-web` | Test `webserver` role (debian12, ubuntu2204) |
| `make test-mysql` | Test `database` role with MySQL |
| `make test-pgsql` | Test `database` role with PostgreSQL |
| `make test-nodejs` | Test `app` role with Node.js |
| `make test-python` | Test `app` role with Python |
| `make test-list` | List all available scenarios |

### Cleanup

| Command | Description |
|---------|-------------|
| `make clean` | Remove molecule artifacts, `__pycache__`, and `.pyc` files |
| `make clean-containers` | Destroy all running molecule containers |

### Vault

| Command | Description |
|---------|-------------|
| `make vault-edit` | Edit vault-encrypted file (default: `inventory/production/group_vars/all.yml`) |
| `make vault-view` | View vault-encrypted file contents without decrypting |
| `make vault-encrypt` | Encrypt a vars file with vault |
| `make vault-decrypt` | Decrypt a vars file |

To override the vault file: `make vault-edit VAULT_FILE=path/to/file.yml`

## Hardening Applied

### Common Role (All Servers)
- **SSH Hardening**: Custom port (2222), disable root login, disable password auth
- **Firewall**: UFW (Debian) / Firewalld (RHEL), whitelist ports
- **Fail2ban**: SSH brute-force protection
- **Auditd**: System and login auditing
- **IPv6**: Disabled (recommended)
- **SELinux/AppArmor**: Enforcing mode (active)
- **Auto-Update**: Automatic security updates
- **System Hardening**: Disable unused filesystems, harden /tmp, disable core dumps

### Webserver Role
- Nginx or Apache installation
- SSL/TLS configuration (TLS 1.2/1.3)
- Security headers (HSTS, X-Frame-Options, etc.)
- Support multiple sites

### Database Role
- MySQL or PostgreSQL installation
- Remove anonymous users & test database
- Create databases & users

### App Role
- Node.js, Python, or Java support
- Systemd service management
- App user isolation

## Configuration Variables

### SSH Configuration
```yaml
ssh_port: 2222
ssh_permit_root_login: "no"
ssh_password_authentication: "no"
```

### Firewall Rules
```yaml
firewall_allowed_tcp_ports:
  - "{{ ssh_port }}"
  - 80
  - 443
firewall_allowed_subnets:
  - 10.0.1.0/24
```

### Webserver Type
```yaml
webserver_type: nginx  # or apache
ssl_enabled: true
```

### Database Type
```yaml
database_type: mysql  # or postgresql
mysql_root_password: "{{ vault_mysql_root_password }}"
```

## Best Practices

1. **Use Vault**: Store database passwords and secrets in Ansible Vault
   ```bash
   ansible-vault encrypt_string 'mysecret' --name 'vault_mysql_root_password'
   ```

2. **Test in Staging**: Always test in staging before production
   ```bash
   make run-staging
   ```

3. **Check Mode**: Use `--check` for dry-run
   ```bash
   make check
   ```

4. **Run Tests First**: Always run Molecule tests before applying to servers
   ```bash
   make test
   ```

5. **Run Lint**: Check for issues before committing
   ```bash
   make lint
   ```

## License

MIT

## Author

Generated by opencode/big-pickle
