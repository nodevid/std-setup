# Std-Setup Makefile
# Multi-distro Ansible server hardening with Molecule testing

SHELL := /bin/bash

# ==============================================================================
# Variables
# ==============================================================================
ANSIBLE         := ansible-playbook
ANSIBLE_CFG     := ./ansible.cfg
INVENTORY_PROD  := inventory/production/hosts.yml
INVENTORY_STG   := inventory/staging/hosts.yml
GALAXY_REQ      := requirements.yml
ROLES_DIR       := roles
PLAYBOOKS       := playbooks

# Python / pip
PIP             := pip
PYTHON          := python3

# Lint
ANSIBLE_LINT    := ansible-lint

# Molecule scenarios
MOLECULE_COMMON := $(ROLES_DIR)/common
MOLECULE_WEB    := $(ROLES_DIR)/webserver
MOLECULE_DB     := $(ROLES_DIR)/database
MOLECULE_APP    := $(ROLES_DIR)/app

# Init
INIT_INVENTORY  ?= inventory/new-hosts.yml

# Colors for output
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
NC     := \033[0m

# ==============================================================================
# Help
# ==============================================================================
.PHONY: help
help: ## Show this help message
	@echo "$(GREEN)Std-Setup Makefile$(NC)"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Dependencies:"
	@echo "  deps           Install Ansible Galaxy collections"
	@echo "  dev-deps       Install Python test dependencies (molecule, testinfra)"
	@echo ""
	@echo "Linting:"
	@echo "  lint           Run ansible-lint on the whole repo"
	@echo ""
	@echo "Playbooks:"
	@echo "  run            Run full site playbook against production"
	@echo "  run-staging    Run full site playbook against staging"
	@echo "  run-web        Run webserver playbook"
	@echo "  run-db         Run database playbook"
	@echo "  run-app        Run app playbook"
	@echo "  init           Initialize new server (create admin, set SSH port 2222, disable root)"
	@echo "  check          Dry-run site playbook (--check)"
	@echo "  check-staging  Dry-run staging playbook (--check)"
	@echo ""
	@echo "Testing (Molecule):"
	@echo "  test           Run ALL molecule tests"
	@echo "  test-common    Run common role tests (debian12, ubuntu2204)"
	@echo "  test-web       Run webserver role tests (debian12, ubuntu2204)"
	@echo "  test-mysql     Run database/MySQL role tests"
	@echo "  test-pgsql     Run database/PostgreSQL role tests"
	@echo "  test-nodejs    Run app/Node.js role tests"
	@echo "  test-python    Run app/Python role tests"
	@echo "  test-list      List all molecule scenarios"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean          Remove molecule artifacts and __pycache__"
	@echo "  clean-containers  Destroy all running molecule containers"
	@echo ""
	@echo "Vault:"
	@echo "  vault-edit     Edit vault encrypted vars file"
	@echo "  vault-encrypt  Encrypt a vars file with vault"
	@echo "  vault-decrypt  Decrypt a vars file"
	@echo ""
	@echo "  help           Show this help message"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# ==============================================================================
# Dependencies
# ==============================================================================
.PHONY: deps
deps: ## Install Ansible Galaxy collections
	@echo "$(GREEN)Installing Galaxy collections...$(NC)"
	ansible-galaxy collection install -r $(GALAXY_REQ)

.PHONY: dev-deps
dev-deps: ## Install Python test dependencies
	@echo "$(GREEN)Installing test dependencies...$(NC)"
	$(PIP) install molecule molecule-plugins[docker] docker pytest-testinfra ansible-lint

# ==============================================================================
# Linting
# ==============================================================================
.PHONY: lint
lint: ## Run ansible-lint on the whole repo
	@echo "$(GREEN)Running ansible-lint...$(NC)"
	$(ANSIBLE_LINT)

# ==============================================================================
# Playbooks
# ==============================================================================
.PHONY: run
run: ## Run full site playbook against production
	$(ANSIBLE) -i $(INVENTORY_PROD) $(PLAYBOOKS)/site.yml

.PHONY: run-staging
run-staging: ## Run full site playbook against staging
	$(ANSIBLE) -i $(INVENTORY_STG) $(PLAYBOOKS)/site.yml

.PHONY: run-web
run-web: ## Run webserver playbook
	$(ANSIBLE) $(PLAYBOOKS)/webserver.yml

.PHONY: run-db
run-db: ## Run database playbook
	$(ANSIBLE) $(PLAYBOOKS)/database.yml

.PHONY: run-app
run-app: ## Run app playbook
	$(ANSIBLE) $(PLAYBOOKS)/app.yml

.PHONY: check
check: ## Dry-run site playbook (--check)
	$(ANSIBLE) --check -i $(INVENTORY_PROD) $(PLAYBOOKS)/site.yml

.PHONY: check-staging
check-staging: ## Dry-run staging playbook (--check)
	$(ANSIBLE) --check -i $(INVENTORY_STG) $(PLAYBOOKS)/site.yml

.PHONY: init
init: ## Initialize new server (set INIT_INVENTORY=path to new host inventory)
	@echo "$(GREEN)Initializing new server...$(NC)"
	@echo "$(YELLOW)Connecting as root, will prompt for password and admin SSH key.$(NC)"
	$(ANSIBLE) -u root --ask-pass -i $(INIT_INVENTORY) $(PLAYBOOKS)/init.yml

# ==============================================================================
# Testing (Molecule)
# ==============================================================================
.PHONY: test-common
test-common: ## Run common role tests (debian12, ubuntu2204)
	cd $(MOLECULE_COMMON) && molecule test

.PHONY: test-web
test-web: ## Run webserver role tests (debian12, ubuntu2204)
	cd $(MOLECULE_WEB) && molecule test

.PHONY: test-mysql
test-mysql: ## Run database/MySQL role tests
	cd $(MOLECULE_DB) && molecule test -s mysql

.PHONY: test-pgsql
test-pgsql: ## Run database/PostgreSQL role tests
	cd $(MOLECULE_DB) && molecule test -s postgresql

.PHONY: test-nodejs
test-nodejs: ## Run app/Node.js role tests
	cd $(MOLECULE_APP) && molecule test -s nodejs

.PHONY: test-python
test-python: ## Run app/Python role tests
	cd $(MOLECULE_APP) && molecule test -s python

.PHONY: test ## Run ALL molecule tests
test: test-common test-web test-mysql test-pgsql test-nodejs test-python
	@echo "$(GREEN)All tests complete.$(NC)"

.PHONY: test-list
test-list: ## List all molecule scenarios
	@echo "$(GREEN)Molecule scenarios:$(NC)"
	@for role in $(ROLES_DIR)/*/; do \
		if [ -d "$${role}molecule" ]; then \
			echo "  Role: $$(basename $$role)"; \
			for scenario in $${role}molecule/*/; do \
				scenario_name=$$(basename $$scenario); \
				if [ -f "$${scenario}molecule.yml" ]; then \
					echo "    - $$scenario_name"; \
				fi; \
			done; \
		fi; \
	done

# ==============================================================================
# Cleanup
# ==============================================================================
.PHONY: clean
clean: ## Remove molecule artifacts and __pycache__
	@echo "$(YELLOW)Cleaning molecule artifacts...$(NC)"
	find $(ROLES_DIR) -path "*/.molecule" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)Clean complete.$(NC)"

.PHONY: clean-containers
clean-containers: ## Destroy all running molecule containers
	@echo "$(YELLOW)Destroying molecule containers...$(NC)"
	for role in $(ROLES_DIR)/common $(ROLES_DIR)/webserver $(ROLES_DIR)/database $(ROLES_DIR)/app; do \
		if [ -d "$${role}/molecule" ]; then \
			echo "  Destroying $$role..."; \
			cd "$${role}" && molecule destroy 2>/dev/null || true; \
		fi; \
	done
	@echo "$(GREEN)Containers destroyed.$(NC)"

# ==============================================================================
# Vault Helpers
# ==============================================================================
VAULT_FILE ?= inventory/production/group_vars/all.yml

.PHONY: vault-edit
vault-edit: ## Edit vault encrypted vars file (set VAULT_FILE=path)
	ansible-vault edit $(VAULT_FILE)

.PHONY: vault-encrypt
vault-encrypt: ## Encrypt a vars file with vault (set VAULT_FILE=path)
	ansible-vault encrypt $(VAULT_FILE)

.PHONY: vault-decrypt
vault-decrypt: ## Decrypt a vars file (set VAULT_FILE=path)
	ansible-vault decrypt $(VAULT_FILE)

.PHONY: vault-view
vault-view: ## View vault encrypted vars file (set VAULT_FILE=path)
	ansible-vault view $(VAULT_FILE)
