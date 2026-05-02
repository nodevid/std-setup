# Std-Setup: Ansible Server Hardening Repository

Repository Ansible untuk standar konfigurasi dan hardening server yang mendukung multi-distro (Debian/Ubuntu dan RHEL/Rocky).

## Fitur Utama

- **Server Hardening Lengkap**: SSH hardening, firewall, fail2ban, auditd, IPv6 disable, SELinux/AppArmor
- **Multi-Distro Support**: Otomatis mendeteksi dan mengonfigurasi berdasarkan OS family
- **Modular Roles**: Terpisah antara common, webserver, database, dan app
- **Environment Separation**: Production dan staging inventories
- **Custom SSH Port**: Default port 2222 (bisa dikonfigurasi)
- **Test Coverage**: 76+ tests via Molecule + testinfra across 6 scenarios

## Requirements

- Ansible >= 2.9
- Python 3 on target hosts
- SSH access dengan key-based authentication

## Quick Start

### 1. Install Dependencies

```bash
ansible-galaxy collection install -r requirements.yml
```

### 2. Konfigurasi Inventory

Edit `inventory/production/hosts.yml` dengan server Anda:

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

Edit `inventory/production/group_vars/all.yml`, tambahkan SSH public key:

```yaml
ssh_authorized_keys:
  - "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... user@workstation"
```

### 4. Jalankan Playbook

```bash
# Apply semua konfigurasi
ansible-playbook playbooks/site.yml

# Atau per kategori
ansible-playbook playbooks/webserver.yml
ansible-playbook playbooks/database.yml
ansible-playbook playbooks/app.yml

# Dry-run (check mode)
ansible-playbook --check playbooks/site.yml

# Target spesifik role
ansible-playbook --tags "ssh,firewall" playbooks/site.yml
```

## Struktur Direktori

```
std-setup/
├── ansible.cfg                    # Konfigurasi Ansible
├── .ansible-lint                  # Ansible-lint rules
├── requirements.yml               # Dependensi collections/roles
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
pip install molecule molecule-plugins[docker] docker pytest-testinfra
```

### Run All Tests for a Role

```bash
cd roles/common && molecule test
cd roles/webserver && molecule test
cd roles/database && molecule test -s mysql
cd roles/database && molecule test -s postgresql
cd roles/app && molecule test -s nodejs
cd roles/app && molecule test -s python
```

### Run Specific Stages

```bash
# Only converge (apply role) without destroy
molecule converge

# Only verify (run tests)
molecule verify

# Check playbook syntax
molecule syntax
```

### Lint Check

```bash
ansible-lint
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

Semua operasi bisa dijalankan via `make`. Lihat semua target:

```bash
make help
```

### Dependencies

| Command | Description |
|---------|-------------|
| `make deps` | Install Ansible Galaxy collections dari `requirements.yml` |
| `make dev-deps` | Install Python test dependencies (molecule, testinfra, ansible-lint) |

### Linting

| Command | Description |
|---------|-------------|
| `make lint` | Run `ansible-lint` pada seluruh repo |

### Playbooks

| Command | Description |
|---------|-------------|
| `make run` | Jalankan `site.yml` ke production inventory |
| `make run-staging` | Jalankan `site.yml` ke staging inventory |
| `make run-web` | Jalankan `webserver.yml` playbook |
| `make run-db` | Jalankan `database.yml` playbook |
| `make run-app` | Jalankan `app.yml` playbook |
| `make check` | Dry-run `site.yml` ke production (`--check` mode) |
| `make check-staging` | Dry-run `site.yml` ke staging (`--check` mode) |

### Testing (Molecule)

| Command | Description |
|---------|-------------|
| `make test` | Jalankan SEMUA molecule tests (6 scenarios) |
| `make test-common` | Test `common` role (debian12, ubuntu2204) |
| `make test-web` | Test `webserver` role (debian12, ubuntu2204) |
| `make test-mysql` | Test `database` role dengan MySQL |
| `make test-pgsql` | Test `database` role dengan PostgreSQL |
| `make test-nodejs` | Test `app` role dengan Node.js |
| `make test-python` | Test `app` role dengan Python |
| `make test-list` | List semua scenario yang tersedia |

### Cleanup

| Command | Description |
|---------|-------------|
| `make clean` | Hapus artifact molecule, `__pycache__`, dan `.pyc` |
| `make clean-containers` | Destroy semua container molecule yang running |

### Vault

| Command | Description |
|---------|-------------|
| `make vault-edit` | Edit file vault-encrypted (default: `inventory/production/group_vars/all.yml`) |
| `make vault-view` | Lihat isi file vault-encrypted tanpa decrypt |
| `make vault-encrypt` | Encrypt file vars dengan vault |
| `make vault-decrypt` | Decrypt file vars |

Untuk override file vault: `make vault-edit VAULT_FILE=path/to/file.yml`

## Hardening yang Diterapkan

### Common Role (Semua Server)
- **SSH Hardening**: Custom port (2222), disable root login, disable password auth
- **Firewall**: UFW (Debian) / Firewalld (RHEL), whitelist ports
- **Fail2ban**: Proteksi brute force SSH
- **Auditd**: Audit sistem dan login
- **IPv6**: Dinonaktifkan (rekomendasi)
- **SELinux/AppArmor**: Enforcing mode (aktif)
- **Auto-Update**: Security updates otomatis
- **System Hardening**: Disable unused filesystems, harden /tmp, disable core dumps

### Webserver Role
- Nginx atau Apache installation
- SSL/TLS configuration (TLS 1.2/1.3)
- Security headers (HSTS, X-Frame-Options, etc.)
- Support multiple sites

### Database Role
- MySQL atau PostgreSQL installation
- Remove anonymous users & test database
- Create databases & users

### App Role
- Node.js, Python, atau Java support
- Systemd service management
- App user isolation

## Konfigurasi Variabel

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
webserver_type: nginx  # atau apache
ssl_enabled: true
```

### Database Type
```yaml
database_type: mysql  # atau postgresql
mysql_root_password: "{{ vault_mysql_root_password }}"
```

## Best Practices

1. **Gunakan Vault**: Simpan password database dan secret lainnya di Ansible Vault
   ```bash
   ansible-vault encrypt_string 'mysecret' --name 'vault_mysql_root_password'
   ```

2. **Test di Staging**: Selalu uji di staging sebelum production
   ```bash
   ansible-playbook -i inventory/staging/hosts.yml playbooks/site.yml
   ```

3. **Check Mode**: Gunakan `--check` untuk dry-run
   ```bash
   ansible-playbook --check playbooks/site.yml
   ```

4. **Run Tests First**: Selalu jalankan Molecule tests sebelum apply ke server
   ```bash
   cd roles/common && molecule test
   ```

## License

MIT

## Author

Generated by opencode/big-pickle
